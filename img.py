from PIL import Image
import sys

def image_to_1bit(input_path, out_png, out_raw=None, target_size=None,
                  rotate_deg=0, use_dither=False, threshold=128):
    """
    Convert an image to 1-bit black & white, optionally save raw packed bits.
    
    Parameters:
        input_path (str): Input image path.
        out_png (str): Output PNG file path.
        out_raw (str, optional): Output raw 1-bit file path.
        target_size (tuple, optional): (width, height) target canvas size. Maintains aspect ratio.
        rotate_deg (int, optional): Clockwise rotation in degrees.
        use_dither (bool, optional): Apply Floyd-Steinberg dithering.
        threshold (int, optional): Threshold for non-dither conversion (0-255).
    """
    # --- Open image and convert to grayscale ---
    img = Image.open(input_path).convert("L")

    # --- Proportional resize ---
    if target_size:
        target_w, target_h = target_size
        orig_w, orig_h = img.size
        scale = min(target_w / orig_w, target_h / orig_h)
        new_w = int(orig_w * scale)
        new_h = int(orig_h * scale)
        img = img.resize((new_w, new_h), Image.NEAREST)
    else:
        target_w, target_h = img.size
        new_w, new_h = img.size

    # --- Rotate clockwise ---
    if rotate_deg:
        img = img.rotate(-rotate_deg, expand=True)

    # --- Paste onto target-sized canvas if target_size specified ---
    if target_size:
        canvas = Image.new('L', target_size, 0)  # black background
        offset_x = (target_w - img.width) // 2
        offset_y = (target_h - img.height) // 2
        canvas.paste(img, (offset_x, offset_y))
    else:
        canvas = img

    # --- Convert to 1-bit ---
    if use_dither:
        bw = canvas.convert("1", dither=Image.FLOYDSTEINBERG)
    else:
        bw = canvas.point(lambda p: 255 if p >= threshold else 0, mode='1')

    # --- Save PNG ---
    bw.save(out_png)

    # --- Save raw 1-bit packed file if requested ---
    if out_raw:
        w, h = bw.size
        pixels = bw.load()
        with open(out_raw, "wb") as f:
            for y in range(h):
                byte = 0
                bit_count = 0
                for x in range(w):
                    val = 1 if pixels[x, y] == 255 else 0
                    byte = (byte << 1) | val
                    bit_count += 1
                    if bit_count == 8:
                        f.write(bytes([byte]))
                        byte = 0
                        bit_count = 0
                if bit_count:
                    byte = byte << (8 - bit_count)  # pad remaining bits
                    f.write(bytes([byte]))

    print(f"Saved PNG: {out_png}")
    if out_raw:
        print(f"Saved raw 1-bit: {out_raw}")

if __name__ == "__main__":
    # Example usage:
    # python convert_1bit.py input.png out.png out.raw 68 140 90 dither
    args = sys.argv[1:]
    if not args:
        print("Usage: input out_png [out_raw] [width height] [rotate_deg] [dither|nodither]")
        sys.exit(1)
    input_path = args[0]
    out_png = args[1]
    out_raw = args[2] if len(args) > 2 and not args[2].isdigit() else None

    # find width/height in args
    width = None
    height = None
    rotate = 0
    use_dither = False
    rest = args[2 if out_raw else 2:]
    if len(rest) >= 2 and rest[0].isdigit() and rest[1].isdigit():
        width = int(rest[0]); height = int(rest[1])
        rest = rest[2:]
    if rest:
        if rest[0].isdigit():
            rotate = int(rest[0]); rest = rest[1:]
    if rest and rest[0].lower().startswith("dither"):
        use_dither = True

    image_to_1bit(input_path, out_png, out_raw, target_size=(width,height) if width else None,
                  rotate_deg=rotate, use_dither=use_dither)

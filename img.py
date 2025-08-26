from PIL import Image
import sys

def image_to_1bit(input_path, out_png, out_raw=None, target_size=None,
                  rotate_deg=0, use_dither=False, threshold=128):
    img = Image.open(input_path).convert("L")  # convert to grayscale

    # Optional: resize (use NEAREST to keep pixel blocks)
    if target_size:
        img = img.resize(target_size, Image.NEAREST)

    # Optional: rotate clockwise (PIL rotate is counter-clockwise, so use -angle)
    if rotate_deg:
        img = img.rotate(-rotate_deg, expand=True)

    # Convert to 1-bit
    if use_dither:
        bw = img.convert("1", dither=Image.FLOYDSTEINBERG)
    else:
        bw = img.point(lambda p: 255 if p >= threshold else 0, mode='1')

    # Save PNG/BMP 1-bit
    bw.save(out_png)

    # Optionally write raw packed bits (no header): top-to-bottom, left-to-right, MSB first per byte
    if out_raw:
        w, h = bw.size
        pixels = bw.convert("1").load()
        with open(out_raw, "wb") as f:
            for y in range(h):
                byte = 0
                bit_count = 0
                for x in range(w):
                    # In '1' mode: pixel is 0 for black, 255 for white
                    val = 1 if pixels[x, y] == 255 else 0
                    # Pack MSB first
                    byte = (byte << 1) | val
                    bit_count += 1
                    if bit_count == 8:
                        f.write(bytes([byte]))
                        byte = 0
                        bit_count = 0
                # If row width not multiple of 8, pad the last byte with zeros on the right
                if bit_count:
                    byte = byte << (8 - bit_count)
                    f.write(bytes([byte]))

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

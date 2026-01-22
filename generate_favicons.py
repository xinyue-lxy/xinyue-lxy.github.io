import os
from PIL import Image, ImageDraw, ImageFont

EMOJI = "💫"
OUTPUT_DIR = "images"
FONT_PATH = "/System/Library/Fonts/Apple Color Emoji.ttc"

SIZES = {
    "favicon-16x16.png": 16,
    "favicon-32x32.png": 32,
    "apple-touch-icon.png": 180,
    "android-chrome-192x192.png": 192,
    "android-chrome-512x512.png": 512,
    "mstile-144x144.png": 144
}

def load_font(size):
    try:
        return ImageFont.truetype(FONT_PATH, size)
    except:
        return None

def generate_base_image():
    # Try to find the largest valid font size up to 512
    # Apple Color Emoji often supports specific sizes.
    # We prefer the largest one to support 512px icon.
    candidate_sizes = [512, 256, 160, 96, 64, 48, 40, 32]
    
    font = None
    used_size = 0
    
    for s in candidate_sizes:
        font = load_font(s)
        if font:
            used_size = s
            print(f"Using font size: {used_size}")
            break
            
    if not font:
        print("Could not load any suitable font size.")
        return None

    # Draw
    # Create ample canvas
    canvas_size = int(used_size * 1.5)
    img = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    try:
        left, top, right, bottom = font.getbbox(EMOJI)
        w = right - left
        h = bottom - top
        x = (canvas_size - w) / 2 - left
        y = (canvas_size - h) / 2 - top
        draw.text((x, y), EMOJI, font=font, embedded_color=True)
    except Exception as e:
        print(f"Error drawing emoji: {e}")
        return None
        
    # Crop to content
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        
    # Make square
    w, h = img.size
    max_dim = max(w, h)
    
    final_dim = max_dim
    square_img = Image.new("RGBA", (final_dim, final_dim), (0, 0, 0, 0))
    square_img.paste(img, ((final_dim - w) // 2, (final_dim - h) // 2))
    
    return square_img

def main():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    base_img = generate_base_image()
    if not base_img:
        print("Failed to generate base image.")
        return

    generated_images = {}
    for filename, size in SIZES.items():
        # Resize
        resampled = base_img.resize((size, size), Image.Resampling.LANCZOS)
        save_path = os.path.join(OUTPUT_DIR, filename)
        resampled.save(save_path)
        print(f"Saved {save_path}")
        generated_images[size] = resampled

    # ICO
    ico_imgs = []
    img_48 = base_img.resize((48, 48), Image.Resampling.LANCZOS)
    ico_imgs.append(img_48)
    
    for s in [32, 16]:
        if s in generated_images:
            ico_imgs.append(generated_images[s])
            
    if ico_imgs:
        ico_path = os.path.join(OUTPUT_DIR, "favicon.ico")
        primary = ico_imgs[0]
        others = ico_imgs[1:]
        primary.save(ico_path, format='ICO', sizes=[(i.width, i.height) for i in ico_imgs], append_images=others)
        print(f"Saved {ico_path}")

if __name__ == "__main__":
    main()

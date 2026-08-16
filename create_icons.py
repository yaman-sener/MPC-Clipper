"""
MPC Clipper Icon Generator Script
Generates icon.ico, icon.png, favicon.ico, and favicon.png for the application.
"""
import os
import sys

def create_simple_icon():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    print("İkon dosyaları kontrol ediliyor...")
    
    # Try importing Pillow if available
    try:
        from PIL import Image, ImageDraw
        
        # Create a 256x256 icon canvas
        size = (256, 256)
        img = Image.new("RGBA", size, (15, 23, 42, 255)) # Dark slate background
        draw = ImageDraw.Draw(img)
        
        # Draw rounded rectangle background
        draw.rounded_rectangle([16, 16, 240, 240], radius=48, fill=(30, 41, 59, 255), stroke=(51, 65, 85, 255), width=4)
        
        # Draw glowing film strip curve (cyan-purple gradient style)
        draw.arc([40, 60, 216, 216], start=45, end=225, fill=(6, 182, 212, 255), width=24)
        draw.arc([40, 60, 216, 216], start=180, end=340, fill=(168, 85, 247, 255), width=24)
        
        # Draw scissor blade X
        draw.line([70, 70, 186, 186], fill=(248, 250, 252, 255), width=16)
        draw.line([70, 186, 186, 70], fill=(248, 250, 252, 255), width=16)
        
        # Scissor handle loops
        draw.ellipse([45, 45, 85, 85], outline=(248, 250, 252, 255), width=8)
        draw.ellipse([45, 171, 85, 211], outline=(248, 250, 252, 255), width=8)
        
        # Center pivot
        draw.ellipse([120, 120, 136, 136], fill=(56, 189, 248, 255))
        
        # Save PNG and ICO
        png_path = os.path.join(base_dir, "icon.png")
        ico_path = os.path.join(base_dir, "icon.ico")
        fav_png = os.path.join(base_dir, "favicon.png")
        fav_ico = os.path.join(base_dir, "favicon.ico")
        
        img.save(png_path, "PNG")
        img.save(fav_png, "PNG")
        img.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
        img.save(fav_ico, format="ICO", sizes=[(16, 16), (32, 32), (48, 48)])
        
        print("✅ İkonlar başarıyla oluşturuldu:")
        print(f"   - {png_path}")
        print(f"   - {ico_path}")
        print(f"   - {fav_ico}")
    except ImportError:
        print("ℹ️ Pillow kütüphanesi bulunamadı. varsayılan ikona geçiliyor.")

if __name__ == "__main__":
    create_simple_icon()

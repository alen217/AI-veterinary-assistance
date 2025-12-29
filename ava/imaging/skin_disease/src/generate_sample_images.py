import os
from PIL import Image, ImageDraw
import random


def generate_sample_images(data_dir="../data", images_per_class=5):
    """
    Generate sample placeholder images for each disease category.
    
    Args:
        data_dir: Path to the data directory
        images_per_class: Number of images to generate per class per split
    """
    classes = ["mange", "fungal", "wound", "normal"]
    splits = ["train", "val", "test"]
    
    for split in splits:
        split_path = os.path.join(data_dir, split)
        for disease_class in classes:
            class_path = os.path.join(split_path, disease_class)
            os.makedirs(class_path, exist_ok=True)
            
            for i in range(images_per_class):
                # Create a simple colored image based on class
                img = Image.new("RGB", (224, 224), color=get_color_for_class(disease_class))
                draw = ImageDraw.Draw(img)
                
                # Add some random elements to make them different
                for _ in range(random.randint(5, 15)):
                    x0, y0 = random.randint(0, 200), random.randint(0, 200)
                    x1, y1 = x0 + random.randint(10, 40), y0 + random.randint(10, 40)
                    draw.rectangle([x0, y0, x1, y1], fill=get_random_color())
                
                # Add text label
                draw.text((10, 10), f"{disease_class.upper()} #{i+1}", fill=(255, 255, 255))
                
                # Save image
                filename = f"{disease_class}_{split}_{i+1:03d}.png"
                filepath = os.path.join(class_path, filename)
                img.save(filepath)
                print(f"Created: {filepath}")


def get_color_for_class(disease_class):
    """Return a base color for each disease class."""
    colors = {
        "mange": (200, 150, 100),      # Brown-ish
        "fungal": (150, 100, 150),     # Purple-ish
        "wound": (200, 100, 100),      # Red-ish
        "normal": (150, 200, 150),     # Green-ish
    }
    return colors.get(disease_class, (128, 128, 128))


def get_random_color():
    """Generate a random color."""
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


if __name__ == "__main__":
    print("Generating sample placeholder images...")
    generate_sample_images(images_per_class=5)
    print("✅ Sample images generated successfully!")

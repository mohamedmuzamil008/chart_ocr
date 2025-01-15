from PIL import Image
import pytesseract
import sys
import os
import re

# Configure Tesseract path
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def extract_text_from_image(image_path):
    # Open the image
    img = Image.open(image_path)
    # Use Tesseract OCR to extract text
    text = pytesseract.image_to_string(img)
    return text

# Example usage
image_path = r"E:\App Dev\GitHub\chart_ocr\data\test.png"
if os.path.exists(image_path):
    raw_text = extract_text_from_image(image_path)
    print(raw_text)
else:
    print(f"Image not found at: {image_path}")


def parse_levels(raw_text):
    # Regular expression to match levels (e.g., "VPoc: 383", "PoorL: 378.45")
    pattern = r"(\w+):\s?([\d.]+)"
    matches = re.findall(pattern, raw_text)
    
    # Organize levels in a dictionary
    levels = {}
    for label, value in matches:
        if label.lower() not in levels:
            levels[label.lower()] = []
        levels[label.lower()].append(float(value))
    return levels

# Example usage
parsed_levels = parse_levels(raw_text)
print(parsed_levels)

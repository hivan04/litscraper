import cv2
import pytesseract
import numpy as np
from tkinter import Tk, filedialog, messagebox
from pathlib import Path
import sys
import os

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# --- FUNCTIONS ---
def preprocess_image(img):
    """Clean image for OCR"""
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    return cv2.medianBlur(thresh, 1)  # Light noise removal

def extract_table(img_path):
    """Extract tabular data from image"""
    img = cv2.imread(img_path)
    processed = preprocess_image(img)
    
    # Use Tesseract with table detection settings
    data = pytesseract.image_to_data(
        processed, 
        config='--psm 6 --oem 3',  # Assume uniform block of text
        output_type=pytesseract.Output.DICT
    )
    
    # Group text by line (y-coordinate)
    lines = {}
    for i in range(len(data['text'])):
        if int(data['conf'][i]) > 60:  # Minimum confidence
            y = data['top'][i]
            lines.setdefault(y, []).append(
                (data['left'][i], data['text'][i])  # (x-position, text)
            )
    
    # Sort by Y then X coordinates
    sorted_lines = []
    for y in sorted(lines.keys()):
        sorted_lines.append(' '.join(
            [text for _, text in sorted(lines[y], key=lambda x: x[0])]
        ))
    
    return '\n'.join(sorted_lines)

def save_results(text, input_path):
    """Save to text file next to original image"""
    output_path = Path(input_path).with_suffix('.txt')
    with open(output_path, 'w') as f:
        f.write(text)
    return output_path

# --- MAIN ---
if __name__ == "__main__":
    # Hide tkinter root window
    root = Tk()
    root.withdraw()
    
    # Ask for image
    img_path = filedialog.askopenfilename(
        title="Select Table Image",
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
    )
    
    if not img_path:
        print("No file selected. Exiting.")
        exit()
    
    # Process image
    print(f"\nProcessing: {os.path.basename(img_path)}...")
    extracted_text = extract_table(img_path)
    output_path = save_results(extracted_text, img_path)
    
    # Print results
    print("\n--- EXTRACTED TABLE DATA ---")
    print(extracted_text)
    print(f"\nSaved to: {output_path}")

    # Simple console confirmation
    input("\nPress Enter to exit...")
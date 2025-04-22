import cv2
import numpy as np
from PIL import Image
import pytesseract
import os

class ImageProcessor:
    def __init__(self):
        # Initialize any required models or configurations
        pass
        
    def preprocess_image(self, image_path):
        """Preprocess the image for better OCR results"""
        # Read image
        img = cv2.imread(image_path)
        if img is None:
            return None
            
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(thresh)
        
        return denoised
        
    def extract_serial_number(self, image_path):
        """Extract serial number from bill image"""
        processed_img = self.preprocess_image(image_path)
        if processed_img is None:
            return None
            
        # Use Tesseract OCR to extract text
        try:
            # Configure Tesseract parameters for better serial number recognition
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
            text = pytesseract.image_to_string(processed_img, config=custom_config)
            
            # Clean and validate serial number
            # US currency serial numbers are typically 8-11 characters
            # containing letters and numbers
            serial_candidates = []
            for word in text.split():
                if 8 <= len(word) <= 11 and any(c.isdigit() for c in word) and any(c.isalpha() for c in word):
                    serial_candidates.append(word.upper())
                    
            if serial_candidates:
                return serial_candidates[0]
            return None
            
        except Exception as e:
            print(f"Error in OCR processing: {e}")
            return None
            
    def detect_star_note(self, image_path):
        """Detect if the bill is a star note"""
        processed_img = self.preprocess_image(image_path)
        if processed_img is None:
            return None
            
        # Convert to PIL Image for processing
        pil_img = Image.fromarray(processed_img)
        
        # Look for star symbol in the serial number area
        # This is a simplified version - would need more sophisticated
        # pattern recognition for accurate detection
        try:
            text = pytesseract.image_to_string(pil_img)
            return '*' in text
        except Exception as e:
            print(f"Error in star note detection: {e}")
            return None
            
    def process_bill_image(self, image_path):
        """Main method to process bill image and extract information"""
        result = {
            'serial_number': None,
            'is_star_note': None,
            'success': False
        }
        
        if not os.path.exists(image_path):
            return result
            
        # Extract serial number
        serial_number = self.extract_serial_number(image_path)
        if serial_number:
            result['serial_number'] = serial_number
            result['success'] = True
            
        # Detect star note
        is_star_note = self.detect_star_note(image_path)
        if is_star_note is not None:
            result['is_star_note'] = is_star_note
            
        return result 
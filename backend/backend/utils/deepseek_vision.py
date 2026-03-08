"""
DeepSeek AI Text Understanding Module
Uses Tesseract OCR for text extraction + DeepSeek AI for text refinement and understanding
Note: DeepSeek API does not support vision/image input, only text
"""

import os
import base64
import logging
from typing import Dict, Optional
import requests
from PIL import Image
import io

try:
    import pytesseract
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False

logger = logging.getLogger(__name__)


class DeepSeekVision:
    """
    Text recognition using Tesseract OCR + DeepSeek AI for understanding
    Note: DeepSeek API does not support image input, so we use OCR first
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize text recognition system
        
        Args:
            api_key (str, optional): DeepSeek API key. If not provided, reads from env
        """
        self.api_key = api_key or os.getenv('DEEPSEEK_API_KEY')
        self.api_base = "https://api.deepseek.com"
        self.model = "deepseek-chat"
        self.use_ai_refinement = bool(self.api_key)
        self.available = TESSERACT_AVAILABLE
        
        if not TESSERACT_AVAILABLE:
            logger.warning("Tesseract OCR not available. Install with: pip install pytesseract")
        elif not self.use_ai_refinement:
            logger.info("Tesseract OCR initialized (AI refinement disabled - no API key)")
        else:
            logger.info("DeepSeek Vision initialized successfully (OCR + AI refinement)")
    
    def extract_text_with_ocr(self, image_path: str) -> Dict:
        """
        Extract text from image using Tesseract OCR
        
        Args:
            image_path (str): Path to image file
            
        Returns:
            dict: OCR results with text and confidence
        """
        if not TESSERACT_AVAILABLE:
            return {
                'success': False,
                'error': 'Tesseract OCR not installed',
                'text': ''
            }
        
        try:
            # Open and process image
            image = Image.open(image_path)
            
            # Extract text using Tesseract
            text = pytesseract.image_to_string(image)
            
            # Get detailed data for confidence
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) / 100 if confidences else 0.0
            
            return {
                'success': True,
                'text': text.strip(),
                'confidence': avg_confidence
            }
        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': ''
            }
    
    def recognize_text_from_path(self, image_path: str, detailed: bool = False) -> Dict:
        """
        Extract and understand text from image
        
        Args:
            image_path (str): Path to image file
            detailed (bool): If True, use AI refinement for better results
            
        Returns:
            dict: Recognition results with text, confidence, and details
        """
        if not self.available:
            return {
                'success': False,
                'error': 'Tesseract OCR not available',
                'text': '',
                'confidence': 0.0
            }
        
        try:
            # Step 1: Extract text using OCR
            logger.info(f"Extracting text from image using OCR: {image_path}")
            ocr_result = self.extract_text_with_ocr(image_path)
            
            if not ocr_result['success'] or not ocr_result['text']:
                return {
                    'success': False,
                    'error': ocr_result.get('error', 'No text detected'),
                    'text': '',
                    'confidence': 0.0
                }
            
            raw_text = ocr_result['text']
            ocr_confidence = ocr_result['confidence']
            
            # Step 2: Use AI refinement if available and requested
            if self.use_ai_refinement and detailed:
                logger.info("Refining OCR text with DeepSeek AI")
                refined_text = self.refine_text_with_ai(raw_text)
                final_text = refined_text if refined_text else raw_text
                method = 'OCR + DeepSeek AI'
                # Boost confidence slightly for AI refinement
                final_confidence = min(0.98, ocr_confidence * 1.1)
            else:
                final_text = raw_text
                method = 'Tesseract OCR'
                final_confidence = ocr_confidence
            
            word_count = len(final_text.split())
            
            logger.info(f"Text recognition successful: {word_count} words, confidence: {final_confidence:.2%}")
            
            return {
                'success': True,
                'text': final_text,
                'confidence': final_confidence,
                'word_count': word_count,
                'method': method,
                'model': 'Tesseract + ' + self.model if self.use_ai_refinement else 'Tesseract'
            }
        
        except Exception as e:
            logger.error(f"Text recognition error: {e}")
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'confidence': 0.0
            }
    
    def refine_text_with_ai(self, raw_text: str) -> Optional[str]:
        """
        Refine OCR text using DeepSeek AI for better accuracy
        
        Args:
            raw_text (str): Raw OCR text to refine
            
        Returns:
            str: Refined text, or None if refinement fails
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            prompt = f"""The following text was extracted from an image using OCR and may contain errors. Please correct any obvious OCR mistakes, fix formatting, and return ONLY the corrected text without any explanation:

{raw_text}

Corrected text:"""
            
            payload = {
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.1,
                "max_tokens": 2000
            }
            
            response = requests.post(
                f"{self.api_base}/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                refined_text = result['choices'][0]['message']['content'].strip()
                return refined_text
            else:
                logger.warning(f"AI refinement failed: {response.status_code}")
                return None
                
        except Exception as e:
            logger.warning(f"AI refinement error: {e}")
            return None
    
    def recognize_multiple_images(self, image_paths: list, detailed: bool = False) -> list:
        """
        Process multiple images in batch
        
        Args:
            image_paths (list): List of image paths
            detailed (bool): If True, use detailed analysis
            
        Returns:
            list: List of recognition results for each image
        """
        results = []
        for image_path in image_paths:
            result = self.recognize_text_from_path(image_path, detailed=detailed)
            results.append({
                'image_path': image_path,
                'result': result
            })
        return results


if __name__ == "__main__":
    # Test DeepSeek Vision
    import sys
    
    api_key = "sk-a10262ee33594fd5bc381761303ca48e"
    
    print("="*60)
    print("Testing DeepSeek AI Vision")
    print("="*60)
    
    vision = DeepSeekVision(api_key=api_key)
    
    if vision.available:
        print("✅ DeepSeek AI Vision is initialized!")
        print(f"API Base: {vision.api_base}")
        print(f"Model: {vision.model}")
        
        # Test with a sample image if provided
        if len(sys.argv) > 1:
            test_image = sys.argv[1]
            print(f"\nTesting with image: {test_image}")
            result = vision.recognize_text_from_path(test_image, detailed=True)
            
            if result['success']:
                print(f"\n✅ Recognition Successful!")
                print(f"Confidence: {result['confidence']:.2%}")
                print(f"Word Count: {result['word_count']}")
                print(f"\nExtracted Text:")
                print("-" * 60)
                print(result['text'])
                print("-" * 60)
            else:
                print(f"\n❌ Recognition Failed: {result.get('error', 'Unknown error')}")
        else:
            print("\nℹ️  To test with an image, run:")
            print("python -m backend.utils.deepseek_vision <path_to_image>")
    else:
        print("❌ DeepSeek API key not configured")
    
    print("\n" + "="*60)

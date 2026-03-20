"""
PDF to Image Converter for LLM Vision Processing
Converts PDF documents to base64-encoded images for vision model processing
"""
import fitz  # PyMuPDF
import base64
from typing import Tuple
from loguru import logger


class PDFConverter:
    """Handles PDF to image conversion for LLM vision processing"""
    
    @staticmethod
    def convert_pdf_to_base64_image(pdf_bytes: bytes, page_number: int = 0, dpi: int = 150) -> Tuple[str, str]:
        """
        Convert a PDF page to a base64-encoded JPEG image.
        
        Args:
            pdf_bytes: Raw bytes of the PDF file
            page_number: Which page to convert (default: 0 = first page)
            dpi: Resolution for rendering (default: 150, higher = better quality but larger)
            
        Returns:
            Tuple of (base64_string, mime_type)
            - base64_string: Base64-encoded image data
            - mime_type: MIME type (always 'image/jpeg')
        """
        try:
            logger.info(f"Converting PDF page {page_number} to image at {dpi} DPI")
            
            # Open PDF from bytes
            pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
            
            # Check if page number is valid
            if page_number >= pdf_document.page_count:
                logger.warning(f"Page {page_number} not found, using first page")
                page_number = 0
            
            # Get the specified page
            page = pdf_document[page_number]
            
            # Calculate zoom factor based on DPI (72 is default DPI)
            zoom = dpi / 72.0
            mat = fitz.Matrix(zoom, zoom)
            
            # Render page to pixmap (image)
            pixmap = page.get_pixmap(matrix=mat)
            
            # Convert pixmap to JPEG bytes
            img_bytes = pixmap.tobytes("jpeg")
            
            # Close the PDF document
            pdf_document.close()
            
            # Encode to base64
            base64_image = base64.b64encode(img_bytes).decode('utf-8')
            
            logger.info(f"PDF converted successfully. Image size: {len(base64_image)} bytes")
            return base64_image, "image/jpeg"
            
        except Exception as e:
            logger.error(f"Failed to convert PDF to image: {str(e)}")
            raise Exception(f"PDF conversion error: {str(e)}")
    
    @staticmethod
    def convert_image_to_base64(image_bytes: bytes, mime_type: str = "image/jpeg") -> Tuple[str, str]:
        """
        Convert image bytes to base64-encoded string.
        
        Args:
            image_bytes: Raw bytes of the image file
            mime_type: MIME type of the image (e.g., 'image/jpeg', 'image/png')
            
        Returns:
            Tuple of (base64_string, mime_type)
        """
        try:
            logger.info(f"Converting {mime_type} image to base64")
            base64_image = base64.b64encode(image_bytes).decode('utf-8')
            logger.info(f"Image converted successfully. Size: {len(base64_image)} bytes")
            return base64_image, mime_type
        except Exception as e:
            logger.error(f"Failed to convert image to base64: {str(e)}")
            raise Exception(f"Image conversion error: {str(e)}")
    
    @staticmethod
    def process_document_for_vision(file_content: bytes, content_type: str) -> Tuple[str, str]:
        """
        Process uploaded document and convert to base64 image format for LLM vision.
        
        Args:
            file_content: Raw bytes of the uploaded file
            content_type: MIME type of the file
            
        Returns:
            Tuple of (base64_string, mime_type) ready for vision model
        """
        logger.info(f"Processing document of type: {content_type}")
        
        if content_type == "application/pdf":
            return PDFConverter.convert_pdf_to_base64_image(file_content)
        elif content_type in ["image/jpeg", "image/jpg"]:
            return PDFConverter.convert_image_to_base64(file_content, "image/jpeg")
        elif content_type == "image/png":
            return PDFConverter.convert_image_to_base64(file_content, "image/png")
        else:
            raise ValueError(f"Unsupported content type: {content_type}. Supported: PDF, JPG, PNG")


# Convenience functions
def pdf_to_base64(pdf_bytes: bytes, page_number: int = 0) -> str:
    """Quick conversion of PDF to base64 image string"""
    base64_str, _ = PDFConverter.convert_pdf_to_base64_image(pdf_bytes, page_number)
    return base64_str


def image_to_base64(image_bytes: bytes, mime_type: str = "image/jpeg") -> str:
    """Quick conversion of image to base64 string"""
    base64_str, _ = PDFConverter.convert_image_to_base64(image_bytes, mime_type)
    return base64_str
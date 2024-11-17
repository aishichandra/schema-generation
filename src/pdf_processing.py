import base64
from io import BytesIO
from typing import List

import fitz  # PyMuPDF
import PIL.Image


def base64_encode_image(image: 'PIL.Image.Image') -> str:
    """
    Encode a PIL Image object to a base64 string.

    Args:
        image (PIL.Image.Image): The image to encode.

    Returns:
        str: The base64 encoded string representation of the image.
    """
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


def get_images(pdf_path: str) -> List["PIL.Image.Image"]:
    """
    Convert a PDF file to a list of PIL Image objects using PyMuPDF.

    Args:
        pdf_path (str): The file path to the PDF.

    Returns:
        List[PIL.Image.Image]: A list of PIL Image objects, each representing a page of the PDF.
    """
    try:
        pdf_document = fitz.open(pdf_path)
        images = []
        
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))  # 300 DPI
            
            # Convert to PIL Image
            img = PIL.Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)
            
        pdf_document.close()
        return images
    
    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")

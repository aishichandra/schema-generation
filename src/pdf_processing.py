import base64
from io import BytesIO
from typing import List

import PIL.Image
from pdf2image import convert_from_path


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
    Convert a PDF file to a list of PIL Image objects.

    Args:
        pdf_path (str): The file path to the PDF.

    Returns:
        List[PIL.Image.Image]: A list of PIL Image objects, each representing a page of the PDF.
    """
    images = convert_from_path(pdf_path)
    return images
    # TODO: Add logic if images need to be saved to disk

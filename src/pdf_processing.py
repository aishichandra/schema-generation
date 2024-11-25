import base64
from io import BytesIO


def base64_encode_image(image: "PIL.Image.Image") -> str:
    """
    Encode a PIL Image object to a base64 string.

    Args:
        image (PIL.Image.Image): The image to encode.

    Returns:
        str: The base64 encoded string representation of the image.
    """
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode("utf-8")

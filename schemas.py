import json
import re
from typing import Dict, List, Tuple, Type

import PIL.Image
from dotenv import load_dotenv
from openai import OpenAI
from pdf_processing import base64_encode_image
from pydantic import BaseModel

load_dotenv()

openai_client = OpenAI()





def determine_type(input: List[str | PIL.Image.Image]) -> str:
    """
    Determine the format of data on a page from a PDF document.

    Args:
        input (str|PIL.Image.Image): The input data, either as a string or a PIL Image object.

    Returns:
        str: The inferred data format, which can be one of 'table', 'form', or 'freeform_text'.

    Raises:
        ValueError: If no response is received from the OpenAI API or if an invalid data format is inferred.
    """
    prompt_decide = """Here is a page from a PDF document. Your task is to determine the format of the data on the page.

    The data format can be one of the following:
    - Table
    - Form
    - Freeform text

    Structure your response as follows:

    EXPLANATION: [explanation of how you determined the data format]
    DATA FORMAT: [table/form/freeform_text]
    """
    message_input = [format_input_message(i) for i in input]

    resp = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt_decide},
            {"role": "user", "content": message_input},
        ],
    )

    response_text = resp.choices[0].message.content
    if not isinstance(response_text, str):
        raise ValueError("No response received from the OpenAI API")

    inferred_format = response_text.split("DATA FORMAT: ")[1].strip().lower()
    if inferred_format not in ["table", "form", "freeform_text"]:
        raise ValueError(f"Invalid data format: {inferred_format}")

    return inferred_format


def generate_schema(input: List[str | PIL.Image.Image]) -> str:
    """
    Generate a Pydantic schema based on the input and data type.

    Args:
        input (str|PIL.Image.Image): The input data, either as a string or a PIL Image object.

    Returns:
        str: A string representation of the generated Pydantic schema.

    Raises:
        ValueError: If no response is received from the OpenAI API.
    """
    prompts = {
        "table": {
            "generate": """Here is a table. Please list the columns in this table. Be comprehensive, including every field that contains data. The table may be complex, so make sure you're not omitting any information, such as columns with multiple values.

            Use the following response format:
            <thinking>[Your internal reasoning about how to approach this problem]</thinking>
            [List of identified columns]""",
            "refine": """Based on the fields you identified, please generate a Pydantic model class that can represent this entire table, making sure that the model can capture all rows in the table.""",
        },
        "form": {
            "generate": """Here is a form. Please list the fields on this form. Be comprehensive, including every field that requires a response. The form may be complex, so make sure you're not omitting any information, such as questions with multiple checkboxes, or fields with multiple columns.

            Use the following response format:
            <thinking>[Your internal reasoning about how to approach this problem]</thinking>
            [List of identified fields]""",
            "refine": """Based on the fields you identified, please generate a Pydantic model class that can represent this form.""",
        },
        "freeform_text": {
            "generate": """Here is a page of text. Please list the key entities and attributes in this text. Be comprehensive, including every entity and attribute that is mentioned. The text may be complex, so make sure you're not omitting any information, such as entities with multiple attributes.""",
            "refine": """Based on the entities and attributes you identified, please generate a Pydantic model class that can represent this text.""",
        },
    }

    prompt_pydantic = """Update your Pydantic model with the following constraints:
    - Remove any Fields
    - Represent any dates as strings
    - Nest any helper classes inside your main class
    - Wrap any references to helper classes in double quotes (e.g. "HelperClass")
    - Remove any example data, or example implementations
    - Remove any default values and constraints
    - Remove any configs"""

    data_type = determine_type(input)

    message_input = [format_input_message(i) for i in input]
    message_input.append({"type": "text", "text": prompts[data_type]["generate"]})

    messages = [
        {
            "role": "system",
            "content": "You are an expert at identifying data structures.",
        },
        {"role": "user", "content": message_input},
    ]

    resp = openai_client.chat.completions.create(model="gpt-4o", messages=messages)

    messages.extend(
        [
            {"role": "assistant", "content": resp.choices[0].message.content},
            {"role": "user", "content": prompts[data_type]["refine"]},
        ]
    )

    resp = openai_client.chat.completions.create(model="gpt-4o", messages=messages)

    messages.extend(
        [
            {"role": "assistant", "content": resp.choices[0].message.content},
            {"role": "user", "content": prompt_pydantic},
        ]
    )

    resp = openai_client.chat.completions.create(model="gpt-4o", messages=messages)

    output_text = resp.choices[0].message.content
    if not isinstance(output_text, str):
        raise ValueError("No response received from the OpenAI API")

    output_text = re.split(r"```.*", output_text)[1].strip()

    return output_text


def get_schema_class(schema_str: str) -> Tuple[Type[BaseModel], str]:
    """
    Extract and create a Pydantic schema class from a string representation.

    Args:
        schema_str (str): A string containing the Pydantic schema definition.

    Returns:
        Tuple[Type[BaseModel], str]: A tuple containing:
            - The dynamically created Pydantic schema class.
            - The name of the schema class as a string.

    Raises:
        NameError: If the schema class name is not found in the local namespace after execution.
        SyntaxError: If there's a syntax error in the schema definition.

    Note:
        This function uses `exec()` to dynamically create the schema class,
        which can be a security risk if `schema_str` comes from an untrusted source.
    """
    schema_name = schema_str.split("(")[0].split("class")[1].strip()

    namespace = {}
    exec(schema_str, namespace)
    schema_class = namespace[schema_name]

    return schema_class, schema_name


def extract_data_with_schema(
    input: "str | PIL.Image.Image", schema: Type[BaseModel]
) -> Dict:
    prompt_extract = (
        """Based on the provided schema, please extract data from the input."""
    )

    message_input = format_input_message(input)

    parsed = openai_client.beta.chat.completions.parse(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": prompt_extract},
            {"role": "user", "content": [message_input]},
        ],
        response_format=schema,
    )

    # Parse the response to extract the data
    # The response is expected to be a JSON object with the extracted data
    parsed_data = parsed.choices[0].message.content
    if not isinstance(parsed_data, str):
        raise ValueError("No response received from the OpenAI API")
    parsed_data_json = json.loads(parsed_data)

    return parsed_data_json

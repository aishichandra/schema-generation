import json
import re
from pathlib import Path
from typing import Dict, Tuple, Type

import PIL.Image
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from streamlit import secrets

from src.pdf_processing import base64_encode_image

load_dotenv()

llm = OpenAI(api_key=secrets["OPENAI_API_KEY"])


class SchemaSelection(BaseModel):
    explanation: str
    chosen_schema: str


def format_input_message(input: "str | PIL.Image.Image") -> Dict:
    """
    Formats the input message for API consumption.

    This function takes either a string or a PIL.Image.Image object and returns a dictionary
    formatted for use in API requests. For text inputs, it returns a dictionary with
    'type' set to 'text' and 'text' containing the input string. For image inputs,
    it returns a dictionary with 'type' set to 'image_url' and 'image_url' containing
    the base64-encoded image data.

    Args:
        input (str|PIL.Image.Image): The input to be formatted, either a string or a PIL.Image.Image object.

    Returns:
        Dict: A dictionary containing the formatted input message.

    Raises:
        TypeError: If the input is neither a string nor a PIL.Image.Image object.
    """
    if isinstance(input, str):
        return {"type": "text", "text": input}
    elif isinstance(input, PIL.Image.Image):
        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_encode_image(input)}"
            },
        }
    else:
        raise TypeError("Input must be a string or an image object.")


def build_schema_prompt():
    schema_paths = Path("./schemas").glob("*.py")

    schema_blocks = []
    # load in each file to a string
    for schema_path in schema_paths:
        with open(schema_path, "r") as schema_file:
            schema_block = schema_file.read()
        schema_block = schema_path.stem + ":\n" + schema_block
        schema_blocks.append(schema_block)

    seed_schemas = "\n".join(schema_blocks)
    schema_prompt = f"Do either of the schemas below align with this document?\n\nAVAILABLE SCHEMAS:\n\n{seed_schemas}"

    return schema_prompt


def get_schema_selection(pages):
    schema_path = Path("./schemas")
    with open("./prompts/schema_selection.txt", "r") as f:
        system_prompt = f.read()

    prompt = build_schema_prompt()

    inputs_formatted = [format_input_message(prompt)] + [
        format_input_message(page) for page in pages
    ]
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": inputs_formatted},
    ]

    resp = llm.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06", messages=messages, response_format=SchemaSelection
    )

    response_text = json.loads(resp.choices[0].message.content)

    messages.append({"role": "assistant", "content": str(response_text)})

    if response_text["chosen_schema"] == "None":
        return None, messages
    else:
        schema_path = schema_path / f"{response_text['chosen_schema']}.py"
        with open(schema_path, "r") as schema_file:
            schema_definition = schema_file.read()

        return schema_definition, messages


def generate_custom_schema(history):
    with open("./prompts/schema_data_identification.txt", "r") as f:
        prompt_schema = f.read()

    with open("./prompts/schema_pydantic_generation.txt", "r") as f:
        prompt_generate = f.read()

    with open("./prompts/schema_pydantic_refine.txt", "r") as f:
        prompt_refine = f.read()

    messages = history + [{"role": "user", "content": prompt_schema}]

    resp = llm.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=messages,
    )

    messages.append({"role": "assistant", "content": resp.choices[0].message.content})

    messages.append({"role": "user", "content": prompt_generate})

    resp = llm.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )

    messages.append({"role": "assistant", "content": resp.choices[0].message.content})

    messages.append({"role": "user", "content": prompt_refine})

    resp = llm.chat.completions.create(
        model="gpt-4o-mini", messages=messages, temperature=0.3
    )
    resp_str = resp.choices[0].message.content

    messages.append({"role": "assistant", "content": resp_str})

    schema_str = re.split(r"```.*", resp_str)[1].strip()

    return schema_str, messages


def extract_data_with_schema(pages, schema, local=False):
    prompt_extract = (
        """Based on the provided schema, please extract data from the input."""
    )

    inputs_formatted = [format_input_message(page) for page in pages]
    messages = [
        {"role": "system", "content": prompt_extract},
        {"role": "user", "content": inputs_formatted},
    ]

    if not local:
        resp = llm.beta.chat.completions.parse(
            model="gpt-4o-mini", messages=messages, response_format=schema
        )

    else:
        client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")
        resp = client.beta.chat.completions.parse(
            model="qwen2-v1-7b-instruct@4bit", messages=messages, response_format=schema
        )

    return json.loads(resp.choices[0].message.content)


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


def update_table_schema(extracted_data):
    table_data = extracted_data["table_columns"]

    prompt = f"""Translate the column names and data types from this data into a Pydantic model:

        {table_data}
    """
    prompt_pydantic = """Update your Pydantic model with the following constraints:
    - Remove any Fields
    - Represent any dates as strings
    - Nest any helper classes inside your main class
    - Wrap any references to helper classes in double quotes (e.g. "HelperClass")
    - Remove any example data, or example implementations
    - Remove any default values and constraints
    - Remove any configs"""

    messages = [
        {"role": "user", "content": prompt},
    ]

    resp = llm.chat.completions.create(model="gpt-4o-2024-08-06", messages=messages)

    resp_str = resp.choices[0].message.content

    messages.append({"role": "assistant", "content": resp_str})

    messages.append({"role": "user", "content": prompt_pydantic})

    resp = llm.chat.completions.create(model="gpt-4o-2024-08-06", messages=messages)

    resp_str = resp.choices[0].message.content
    model_class = re.split(r"```.*", resp_str)[1].strip()

    return model_class


def persist_schema_definition(schema_str, schema_name):
    schema_path = Path("./schemas") / f"{schema_name}.py"
    with open(schema_path, "w") as schema_file:
        schema_file.write(schema_str)


def generate_schema(pages):
    schema, history = get_schema_selection(pages)

    if schema is None:
        schema, history = generate_custom_schema(history)

    schema_class, schema_name = get_schema_class(schema)

    if schema_name == "Table":
        test_data = extract_data_with_schema([pages[0]], schema_class)
        schema = update_table_schema(test_data)

    return schema

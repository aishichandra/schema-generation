import json
from typing import List

from pydantic import BaseModel

from src.pdf_processing import get_images
from src.schema_flow import extract_data_with_schema, generate_schema, get_schema_class

images = get_images("./data/poll.pdf")
poll = images[:3]


class Response(BaseModel):
    response_text: str
    response_n: int
    response_percentage: float


class Question(BaseModel):
    question_number: int
    question_text: str
    responses: List[Response]

class Poll(BaseModel):
    questions: List[Question]


def flow(pages, prebaked_schema):
    # generated_schema_str = generate_schema(pages)
    # print(generated_schema_str)
    # generated_schema, _ = get_schema_class(generated_schema_str)
    # extracted_data_gen = extract_data_with_schema(pages, generated_schema)
    # extracted_data = extract_data_with_schema(pages, prebaked_schema)
    extracted_data_local = extract_data_with_schema(pages, prebaked_schema, local=True)

    return (
        None,
        None,
        None,
        extracted_data_local,
    )


gen_data_poll, data_poll, schema_poll, local_data_poll = flow(poll, Poll)


# with open("data/eval_outputs/poll.json", "w") as f:
#     json.dump(data_poll, f, indent=2)

# with open("data/eval_outputs/generated_poll.json", "w") as f:
#     json.dump(gen_data_poll, f, indent=2)

# with open("data/eval_outputs/generated_poll_schema.txt", "w") as f:
#     f.write(schema_poll)

with open("data/eval_outputs/local_poll.json", "w") as f:
    json.dump(local_data_poll, f, indent=2)

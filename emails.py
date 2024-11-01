import json
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel
from tqdm import tqdm

from src.schema_flow import extract_data_with_schema, generate_schema, get_schema_class

emails = list(Path("./data/enron_email_sample").glob("*.txt"))


class ParsingRules(BaseModel):
    sender_regex: str
    to_regex: str
    ccs_regex: Optional[str]
    bccs_regex: Optional[str]
    subject_regex: str


class Email(BaseModel):
    sender: str
    to: List[str]
    ccs: Optional[List[str]]
    bccs: Optional[List[str]]
    subject: str
    has_external_recipients: bool
    parsing_rules: ParsingRules


def flow(pages, prebaked_schema):
    generated_schema_str = generate_schema(pages)
    print(generated_schema_str)
    generated_schema, _ = get_schema_class(generated_schema_str)
    extracted_data_gen = extract_data_with_schema(pages, generated_schema)
    extracted_data = extract_data_with_schema(pages, prebaked_schema)

    return extracted_data_gen, extracted_data, generated_schema_str


for email_path in tqdm(emails):
    with open(email_path, "r") as f:
        html = f.read()

    email_data_gen, email_data, email_data_schema = flow([html], Email)

    with open(f"data/eval_outputs/{email_path.stem}.json", "w") as f:
        json.dump(email_data, f, indent=2)

    with open(f"data/eval_outputs/generated_{email_path.stem}.json", "w") as f:
        json.dump(email_data_gen, f, indent=2)

    with open(f"data/eval_outputs/generated_{email_path.stem}_schema.txt", "w") as f:
        f.write(email_data_schema)

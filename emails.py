import json
from typing import List, Optional

import duckdb
from pydantic import BaseModel
from tqdm import tqdm

from src.schema_flow import extract_data_with_schema, generate_schema, get_schema_class

con = duckdb.connect(database=":memory:")
emails = con.execute(
    "SELECT message FROM './data/enron_sample_small.parquet';"
).fetchall()


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


for i, email in tqdm(enumerate(emails)):
    email_data_gen, email_data, email_data_schema = flow([email], Email)

    with open(f"data/eval_outputs/email_{i}.json", "w") as f:
        json.dump(email_data, f, indent=2)

    with open(f"data/eval_outputs/generated_email_{i}.json", "w") as f:
        json.dump(email_data_gen, f, indent=2)

    with open(f"data/eval_outputs/generated_email_{i}_schema.txt", "w") as f:
        f.write(email_data_schema)

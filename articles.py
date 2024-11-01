import json
from pathlib import Path
from typing import Optional

from pydantic import BaseModel
from tqdm import tqdm

from src.schema_flow import extract_data_with_schema, generate_schema, get_schema_class

articles = list(Path("./data/article_html").glob("*.html"))


class ParsingRules(BaseModel):
    byline_xpath: str
    headline_xpath: str
    pub_datetime_xpath: str
    subhed_xpath: Optional[str]
    section_xpath: str


class Article(BaseModel):
    byline: str
    headline: str
    pub_datetime: str
    subhed: Optional[str]
    section: str
    parsing_rules: ParsingRules


with open(articles[0], "r") as f:
    test = f.read()


def flow(pages, prebaked_schema):
    generated_schema_str = generate_schema(pages)
    print(generated_schema_str)
    generated_schema, _ = get_schema_class(generated_schema_str)
    extracted_data_gen = extract_data_with_schema(pages, generated_schema)
    extracted_data = extract_data_with_schema(pages, prebaked_schema)

    return extracted_data_gen, extracted_data, generated_schema_str


for article_path in tqdm(articles):
    with open(article_path, "r") as f:
        html = f.read()

    article_data_gen, article_data, article_data_schema = flow([html], Article)

    with open(f"data/eval_outputs/{article_path.stem}.json", "w") as f:
        json.dump(article_data, f, indent=2)

    with open(f"data/eval_outputs/generated_{article_path.stem}.json", "w") as f:
        json.dump(article_data_gen, f, indent=2)

    with open(f"data/eval_outputs/generated_{article_path.stem}_schema.txt", "w") as f:
        f.write(article_data_schema)

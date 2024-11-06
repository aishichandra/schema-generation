import json
from enum import Enum
from typing import List

from pydantic import BaseModel

from src.pdf_processing import get_images
from src.schema_flow import extract_data_with_schema, generate_schema, get_schema_class

images = get_images("./data/campaign_finance.pdf")

cover_sheet = images[0]
individual_contributions = images[1:11]


class ReportType(str, Enum):
    pre_primary = "pre_primary"
    pre_election = "pre_election"
    annual = "annual"
    nomination = "nomination"
    final = "final"
    outgoing_treasurer = "outgoing_treasurer"
    other = "other"


class ContributionType(str, Enum):
    direct = "direct"
    in_kind = "in_kind"
    loan = "loan"
    interest = "interest"
    misc = "misc"


class CoverSheet(BaseModel):
    committee_name: str
    committee_phone_number: str
    committee_address: str
    committee_party_affiliation: str
    candidate_name: str
    candidate_party_affiliation: str
    candidate_office_sought: str
    candidate_county: str
    report_type: ReportType
    reporting_period_from: str
    reporting_period_to: str
    cash_on_hand_period_beginning: float
    cash_on_hand_jan_1: float
    itemized_contributions_this_period: float
    itemized_contributions_ytd: float
    unitemized_contributions_this_period: float
    unitemized_contributions_ytd: float
    subtotal_contributions_this_period: float
    subtotal_contributions_ytd: float
    total_contributions_this_period: float
    total_contributions_ytd: float
    itemized_expenditures_this_period: float
    itemized_expenditures_ytd: float
    unitemized_expenditures_this_period: float
    unitemized_expenditures_ytd: float
    subtotal_expenditures_this_period: float
    subtotal_expenditures_ytd: float
    cash_on_hand_this_period: float
    cash_on_hand_ytd: float
    debts_owed_by_committee: float
    debts_owed_to_committee: float
    treasurer_signature: str
    treasurer_date: str
    candidate_signature: str
    candidate_date: str


class IndividualContribution(BaseModel):
    contributer_name: str
    contributer_address: str
    contributer_occupation: str
    contribution_type: ContributionType
    amount_this_period: float
    amount_ytd: float
    date: str
    received_by: str


class IndividualContributionTable(BaseModel):
    contributions: List[IndividualContribution]


def flow(pages, prebaked_schema):
    generated_schema_str = generate_schema(pages)
    print(generated_schema_str)
    generated_schema, _ = get_schema_class(generated_schema_str)
    extracted_data_gen = extract_data_with_schema(pages, generated_schema)
    extracted_data = extract_data_with_schema(pages, prebaked_schema)
    extracted_data_local = extract_data_with_schema(pages, prebaked_schema, local=True)

    return (
        extracted_data_gen,
        extracted_data,
        generated_schema_str,
        extracted_data_local,
    )


gen_data_cover_sheet, data_cover_sheet, schema_cover_sheet, local_data_cover_sheet = (
    flow([cover_sheet], CoverSheet)
)

with open("data/eval_outputs/cover_sheet.json", "w") as f:
    json.dump(data_cover_sheet, f, indent=2)

with open("data/eval_outputs/generated_cover_sheet.json", "w") as f:
    json.dump(gen_data_cover_sheet, f, indent=2)


with open("data/eval_outputs/generated_cover_sheet_schema.txt", "w") as f:
    f.write(schema_cover_sheet)

with open("data/eval_outputs/local_cover_sheet.json", "w") as f:
    json.dump(local_data_cover_sheet, f, indent=2)


(
    gen_data_individual_contributions,
    data_individual_contributions,
    schema_individual_contributions,
    local_data_individual_contributions,
) = flow(individual_contributions, IndividualContributionTable)


with open("data/eval_outputs/individual_contributions.json", "w") as f:
    json.dump(data_individual_contributions, f, indent=2)

with open("data/eval_outputs/generated_individual_contributions.json", "w") as f:
    json.dump(gen_data_individual_contributions, f, indent=2)


with open("data/eval_outputs/generated_individual_contributions_schema.txt", "w") as f:
    f.write(schema_individual_contributions)

with open("data/eval_outputs/local_individual_contributions.json", "w") as f:
    json.dump(local_data_individual_contributions, f, indent=2)

import base64

from openai import OpenAI
from pydantic import BaseModel


class FinanceForm(BaseModel):
    committee_name: str
    candidate_name: str
    itemized_contributions_this_period: float
    itemized_contributions_ytd: float


# Path to the image file
image_path = "data/campaign_finance_form.png"

# Read the image file and convert to base64
with open(image_path, "rb") as image_file:
    base64_image = base64.b64encode(image_file.read()).decode("utf-8")

client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="lm-studio")

completion = client.beta.chat.completions.parse(
    model="qwen2-vl-7b-instruct@4bit",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Identify the contents of this image"},
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                },
            ],
        },
    ],
    temperature=0.2,
    response_format=FinanceForm,
)

print(completion.choices[0].message)

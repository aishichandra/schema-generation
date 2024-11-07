import json

from docling.document_converter import DocumentConverter

source = "./data/campaign_finance_sample.pdf"
converter = DocumentConverter()
result = converter.convert(source)
result_json = result.document.export_to_dict()

with open("./data/eval_outputs/campaign_finance_ocr.json", "w") as f:
    json.dump(result_json, f, indent=2)

source = "./data/poll.pdf"
converter = DocumentConverter()
result = converter.convert(source)
result_json = result.document.export_to_dict()

with open("./data/eval_outputs/poll_ocr.json", "w") as f:
    json.dump(result_json, f, indent=2)

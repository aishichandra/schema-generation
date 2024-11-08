from docling.document_converter import DocumentConverter

source = "./data/campaign_finance_sample.pdf"
converter = DocumentConverter()
result = converter.convert(source)
result_md = result.document.export_to_markdown()

with open("./data/eval_outputs/campaign_finance_ocr.md", "w") as f:
    f.write(result_md)

source = "./data/poll.pdf"
converter = DocumentConverter()
result = converter.convert(source)
result_md = result.document.export_to_markdown()

with open("./data/eval_outputs/poll_ocr.md", "w") as f:
    f.write(result_md)
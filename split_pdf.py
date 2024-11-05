import os

from PyPDF2 import PdfReader, PdfWriter


def split_pdf(input_path, output_folder):
    # Create output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Create PDF reader object
    reader = PdfReader(input_path)

    # Get total number of pages
    total_pages = len(reader.pages)

    # Extract each page and create new PDF
    for page_num in range(total_pages):
        # Create PDF writer object
        writer = PdfWriter()

        # Add the current page
        writer.add_page(reader.pages[page_num])

        # Generate output filename
        output_filename = f"page_{page_num + 1}.pdf"
        output_path = os.path.join(output_folder, output_filename)

        # Write the file
        with open(output_path, "wb") as output_file:
            writer.write(output_file)

    print(f"Split {total_pages} pages into separate PDFs in {output_folder}")


split_pdf("data/campaign_finance.pdf", "data/campaign_finance_pages")
split_pdf("data/poll.pdf", "data/poll_pages")

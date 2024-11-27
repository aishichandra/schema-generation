import streamlit as st

from components.data import download_data, extract_data
from components.files import file_uploader, page_selector
from components.schemas import schema_interface
from components.state import initialize_state

WELCOME_MESSAGE = """
This app uses AI to help you extract structured data from documents. Here's how it works:

1. **Upload a document** - Supports PDF files (max 10 pages)
2. **Select pages** - Choose which pages you want to process
3. **Define your schema** - You have two options:
   - Edit the default schema directly in the code editor
   - Click 'Generate Schema' to automatically create one based on your selected pages
4. **Extract data** - The app will process your document according to the schema
5. **Download results** - Get your structured data as a JSON file

The schema defines what data to extract and how to structure it. It uses Python's Pydantic library for data validation.

📚 Want to learn more? Check out the [detailed blog post](https://your-blog-post-url.com) about the technology behind this app.
"""

# Initialize session state variables
initialize_state()

# Welcome message first, then title
st.markdown("# 🤖 Welcome!")
st.info(WELCOME_MESSAGE, icon="🎯")

st.divider()

# Title
st.title("Schema-based data extraction from documents")

# File uploader
file_uploader()

if st.session_state.pages is not None:
    n_selected = page_selector()

    # Show schema section
    schema_interface()

    # Extract data button
    extract_data(n_selected)

    # If data has been extracted, allow user to download it as JSON
    download_data()

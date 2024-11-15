import json
from pathlib import Path

import streamlit as st
from streamlit_ace import st_ace

from src.schema_flow import extract_data_with_schema, generate_schema, get_schema_class
from src.ui_helpers import get_images_cached

# Initialize session state variables
# uploaded file
if "uploaded_file" not in st.session_state:
    st.session_state.uploaded_file = None
# page image objects
if "pages" not in st.session_state:
    st.session_state.pages = None
# generated/edited data schema
if "schema" not in st.session_state:
    st.session_state.schema = None
# extracted (JSON) data
if "extracted_data" not in st.session_state:
    st.session_state.extracted_data = None
# selected pages indices
if "selected_pages" not in st.session_state:
    st.session_state.selected_pages = []

# Title
st.title("Schema-based data extraction from documents")

# File uploader
uploaded_file = st.file_uploader("Upload a file", type=["pdf", "docx", "txt"])

if uploaded_file is not None and st.session_state.uploaded_file != uploaded_file:
    st.session_state.uploaded_file = uploaded_file
    # Save the uploaded file to a temporary location
    tmp_path = Path("tmp") / uploaded_file.name
    tmp_path.parent.mkdir(exist_ok=True)
    with open(tmp_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    pages = get_images_cached(tmp_path)
    # unlink the temporary file
    tmp_path.unlink()

    # Limit pages to first 10
    if len(pages) > 10:
        st.warning(f"Document has {len(pages)} pages. Only the first 10 pages will be processed.")
        pages = pages[:10]

    st.session_state.pages = pages
    st.session_state.schemas = None  # Reset schema
    st.session_state.extracted_data = None  # Reset extracted data

if st.session_state.pages is not None:
    st.write("## Page Selection")
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.write(f"Total pages: {len(st.session_state.pages)}")
        if st.checkbox("Select all pages", key="select_all"):
            st.session_state.selected_pages = list(range(len(st.session_state.pages)))
        else:
            # Only clear if it was previously all selected
            if len(st.session_state.selected_pages) == len(st.session_state.pages):
                st.session_state.selected_pages = []
        
    with col1:
        # Create a grid layout for page selection
        cols = st.columns(4)
        for idx, page in enumerate(st.session_state.pages):
            with cols[idx % 4]:
                st.image(page, caption=f"Page {idx + 1}", use_column_width=True)
                if st.checkbox(
                    f"Include page {idx + 1}",
                    value=idx in st.session_state.selected_pages,
                    key=f"page_{idx}",
                    on_change=lambda i=idx: toggle_page(i)
                ):
                    if idx not in st.session_state.selected_pages:
                        st.session_state.selected_pages.append(idx)
                else:
                    if idx in st.session_state.selected_pages:
                        st.session_state.selected_pages.remove(idx)
    
    # Add this helper function at the top of the file after the session state initialization
    def toggle_page(idx):
        if idx in st.session_state.selected_pages:
            st.session_state.selected_pages.remove(idx)
        else:
            st.session_state.selected_pages.append(idx)

    n_selected = len(st.session_state.selected_pages)
    st.write(f"Selected pages: {n_selected}")

    # Generate schema for selected pages
    if n_selected > 0 and st.button(
        "Generate Schema",
        key="generate_schema_button",
    ):
        selected_pages = [
            st.session_state.pages[i] for i in st.session_state.selected_pages
        ]
        schema = generate_schema(selected_pages)
        st.session_state.schema = schema

    # Show the schema in an editor
    if st.session_state.schema is not None:
        edited_schema = st_ace(
            value=st.session_state.schema,
            language="python",
            key="schema_editor",
            height=500,
            theme="monokai",
        )
        # Update the schema in session state
        st.session_state.schema = edited_schema

    # Allow the user to apply the schema to extract data
    if st.button("Extract Data", key="extract_data_button"):
        schema_code = st.session_state.schema
        if schema_code is not None:
            schema_class, _ = get_schema_class(schema_code)
            # Extract data
            selected_pages = [
                st.session_state.pages[i] for i in st.session_state.selected_pages
            ]
            data = extract_data_with_schema(selected_pages, schema_class)
            st.session_state.extracted_data = data
            st.success("Data extracted successfully.")
        else:
            st.error("Please generate or provide a schema first.")

    # If data has been extracted, allow user to download it as JSON
    if st.session_state.extracted_data is not None:
        data = st.session_state.extracted_data
        json_data = json.dumps(data, indent=2)
        st.download_button(
            label="Download Extracted Data",
            data=json_data,
            file_name="data.json",
            mime="application/json",
        )

import json
from pathlib import Path

import streamlit as st
from schemas import extract_data_with_schema, generate_schema, get_schema_class
from streamlit_ace import st_ace
from ui_helpers import get_images_cached, paginated_image_display

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

    st.session_state.pages = pages
    if "selected_pages" in st.session_state:
        del st.session_state.selected_pages  # Reset selected pages
    st.session_state.schemas = None  # Reset schema
    st.session_state.extracted_data = None  # Reset extracted data

if st.session_state.pages is not None:
    st.write("Select pages to process:")
    selected_pages = paginated_image_display(st.session_state.pages)

    st.write(f"Selected pages: {len(selected_pages)}")

    # Generate schema for selected pages
    if st.button(
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
            data = [extract_data_with_schema(i, schema_class) for i in selected_pages]
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

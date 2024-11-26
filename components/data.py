import json

import streamlit as st

from components.schema_flow import extract_data_with_schema, get_schema_class


def extract_data(n_selected):
    if st.button(
        "Extract Data",
        key="extract_data_button",
        disabled=n_selected == 0 or "selected_workflow" not in st.session_state,
    ):
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


def download_data():
    if st.session_state.extracted_data is not None:
        data = st.session_state.extracted_data
        json_data = json.dumps(data, indent=2)
        st.download_button(
            label="Download Extracted Data",
            data=json_data,
            file_name="data.json",
            mime="application/json",
        )

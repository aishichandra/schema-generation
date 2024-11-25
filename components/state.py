import streamlit as st

PLACEHOLDER_SCHEMA = '''from pydantic import BaseModel
from typing import List, Optional

class Document(BaseModel):
    """Edit this schema or use 'Generate Schema' to create one automatically."""
    title: Optional[str] = None
    content: Optional[List[str]] = None
'''

def initialize_state():
    """Initialize session state variables"""
        # uploaded file
    if "uploaded_file" not in st.session_state:
        st.session_state.uploaded_file = None
    # page image objects
    if "pages" not in st.session_state:
        st.session_state.pages = None
    # generated/edited data schema
    if "schema" not in st.session_state:
        st.session_state.schema = PLACEHOLDER_SCHEMA
    # extracted (JSON) data
    if "extracted_data" not in st.session_state:
        st.session_state.extracted_data = None
    # selected pages indices
    if "selected_pages" not in st.session_state:
        st.session_state.selected_pages = []
from dataclasses import dataclass
from typing import List

import streamlit as st
from streamlit_ace import st_ace

from components.schema_flow import generate_schema
from components.state import PLACEHOLDER_SCHEMA


@dataclass
class SchemaField:
    name: str
    type: str
    is_repeated: bool = False


ALLOWED_TYPES = ["str", "int", "float", "bool"]


def fields_to_pydantic(
    fields: List[SchemaField], class_name: str = "GeneratedSchema"
) -> str:
    lines = [
        "from pydantic import BaseModel",
        "from typing import List, Optional\n",
        f"class {class_name}(BaseModel):",
    ]
    if not fields:
        return PLACEHOLDER_SCHEMA
    else:
        for field in fields:
            type_str = field.type
            if field.is_repeated:
                type_str = f"List[{type_str}]"
            lines.append(f"    {field.name}: {type_str}")
        return "\n".join(lines)


def schema_interface_interactive():
    st.write("### Fields")
    # Add new field
    with st.container():
        new_name = st.text_input("Field name", key="new_field_name")
        new_type = st.selectbox("Field type", ALLOWED_TYPES, key="new_field_type")
        new_repeated = st.checkbox("Is repeated?", key="new_field_repeated")

        if st.button("Add Field"):
            st.session_state.schema_fields.append(
                SchemaField(name=new_name, type=new_type, is_repeated=new_repeated)
            )

    # List existing fields
    for i, field in enumerate(st.session_state.schema_fields):
        with st.container():
            st.write(
                f"**{field.name}**: {field.type} {'(repeated)' if field.is_repeated else ''}"
            )
            if st.button("Remove", key=f"remove_{i}"):
                st.session_state.schema_fields.pop(i)
                st.rerun()

    # Convert fields to Pydantic code
    st.session_state.schema = fields_to_pydantic(st.session_state.schema_fields)


def schema_interface_code(n_selected):
    # Generate schema first
    if n_selected > 0 and st.button("Generate Schema", key="generate_schema_button"):
        selected_pages = [
            st.session_state.pages[i] for i in st.session_state.selected_pages
        ]
        schema = generate_schema(selected_pages)
        st.session_state.schema = schema
        st.rerun()

    # Show the editor with the current schema
    edited_schema = st_ace(
        value=st.session_state.schema,
        language="python",
        key="schema_editor",
        height=300,
        theme="monokai",
    )

    if edited_schema != st.session_state.schema:
        st.session_state.schema = edited_schema
        st.rerun()


def schema_interface(n_selected):
    st.write("## Schema Definition")

    # Initialize session state for fields if not exists
    if "schema_fields" not in st.session_state:
        st.session_state.schema_fields = []

    workflow = st.segmented_control(
        "Schema Building Approach", ["Interface", "Code"], default="Interface"
    )

    if workflow == "Interface":
        schema_interface_interactive()
    else:
        schema_interface_code(n_selected)

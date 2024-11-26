from dataclasses import dataclass
from typing import List

import streamlit as st
from streamlit_ace import st_ace

from components.schema_flow import generate_schema


@dataclass
class SchemaField:
    name: str
    type: str
    is_repeated: bool = False


ALLOWED_TYPES = ["str", "int", "float", "bool", "datetime"]


def fields_to_pydantic(
    fields: List[SchemaField], class_name: str = "GeneratedSchema"
) -> str:
    lines = [
        "from pydantic import BaseModel",
        "from typing import List, Optional",
        "from datetime import datetime\n",
        f"class {class_name}(BaseModel):",
    ]
    for field in fields:
        type_str = field.type
        if field.is_repeated:
            type_str = f"List[{type_str}]"
        lines.append(f"    {field.name}: {type_str}")
    return "\n".join(lines)


def pydantic_to_fields(code: str) -> List[SchemaField]:
    fields = []
    lines = code.split("\n")
    for line in lines:
        if ":" in line and "class" not in line:
            name, type_def = line.strip().split(":", 1)
            name = name.strip()
            type_def = type_def.strip()
            is_repeated = "List[" in type_def
            if is_repeated:
                type_def = type_def[5:-1]  # Remove List[] wrapper
            fields.append(
                SchemaField(name=name, type=type_def, is_repeated=is_repeated)
            )
    return fields


def schema_interface(n_selected):
    st.write("## Schema Definition")

    # Initialize session state for fields if not exists
    if "schema_fields" not in st.session_state:
        st.session_state.schema_fields = []

    col1, col2 = st.columns(2)

    with col1:
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

    with col2:
        # Generate schema first
        if n_selected > 0 and st.button(
            "Generate Schema", key="generate_schema_button"
        ):
            selected_pages = [
                st.session_state.pages[i] for i in st.session_state.selected_pages
            ]
            schema = generate_schema(selected_pages)
            st.session_state.schema = schema
            st.session_state.schema_fields = pydantic_to_fields(schema)
            st.rerun()

        # Show the editor with the current schema
        current_schema = fields_to_pydantic(st.session_state.schema_fields)
        edited_schema = st_ace(
            value=current_schema,
            language="python",
            key="schema_editor",
            height=300,
            theme="monokai",
        )

        if edited_schema != current_schema:
            st.session_state.schema = edited_schema
            st.session_state.schema_fields = pydantic_to_fields(edited_schema)
            st.rerun()

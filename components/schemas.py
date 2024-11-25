import streamlit as st
from schema_flow import generate_schema
from streamlit_ace import st_ace


def schema_interface(n_selected):
    st.write("## Schema Definition")
    st.write(
        "You can either edit the schema directly or generate one from selected pages."
    )

    # Generate schema first
    if n_selected > 0 and st.button("Generate Schema", key="generate_schema_button"):
        selected_pages = [
            st.session_state.pages[i] for i in st.session_state.selected_pages
        ]
        schema = generate_schema(selected_pages)
        st.session_state.schema = schema
        # Force a rerun to update the ace editor
        st.rerun()

    # Then show the editor with the current schema
    edited_schema = st_ace(
        value=st.session_state.schema,
        language="python",
        key="schema_editor",
        height=300,
        theme="monokai",
    )

    if edited_schema != st.session_state.schema:
        st.session_state.schema = edited_schema

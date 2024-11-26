from pathlib import Path
from typing import List

import fitz  # PyMuPDF
import PIL.Image
import streamlit as st


def get_images(pdf_path: str) -> List["PIL.Image.Image"]:
    """
    Convert a PDF file to a list of PIL Image objects using PyMuPDF.

    Args:
        pdf_path (str): The file path to the PDF.

    Returns:
        List[PIL.Image.Image]: A list of PIL Image objects, each representing a page of the PDF.
    """
    try:
        pdf_document = fitz.open(pdf_path)
        images = []

        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            pix = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72))  # 300 DPI

            # Convert to PIL Image
            img = PIL.Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            images.append(img)

        pdf_document.close()
        return images

    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")


@st.cache_data
def get_images_cached(pdf_path):
    return get_images(pdf_path)


def toggle_page(idx):
    if idx in st.session_state.selected_pages:
        st.session_state.selected_pages.remove(idx)
    else:
        st.session_state.selected_pages.append(idx)


def file_uploader():
    uploaded_file = st.file_uploader("Upload a file", type=["pdf"])

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
            st.warning(
                f"Document has {len(pages)} pages. Only the first 10 pages will be processed."
            )
            pages = pages[:10]

        st.session_state.pages = pages
        st.session_state.schema = None  # Reset schema
        st.session_state.extracted_data = None  # Reset extracted data


def page_selector():
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
                st.image(page, caption=f"Page {idx + 1}", use_container_width=True)
                if st.checkbox(
                    f"Include page {idx + 1}",
                    value=idx in st.session_state.selected_pages,
                    key=f"page_{idx}",
                    on_change=lambda i=idx: toggle_page(i),
                ):
                    if idx not in st.session_state.selected_pages:
                        st.session_state.selected_pages.append(idx)
                else:
                    if idx in st.session_state.selected_pages:
                        st.session_state.selected_pages.remove(idx)

    n_selected = len(st.session_state.selected_pages)
    st.write(f"Selected pages: {n_selected}")

    return n_selected

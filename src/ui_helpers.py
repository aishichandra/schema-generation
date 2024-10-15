import streamlit as st
from pdf_processing import get_images


def display_image_with_checkbox(image, key, is_checked):
    col1, col2 = st.columns([1, 4])
    with col1:
        checked = st.checkbox("Include", value=is_checked, key=f"checkbox_{key}")
    with col2:
        st.image(image)
    return checked


def paginated_image_display(images, page_size=5):
    if "page_number" not in st.session_state:
        st.session_state.page_number = 1
    if "selected_pages" not in st.session_state:
        st.session_state.selected_pages = set()

    total_pages = len(images) // page_size + (1 if len(images) % page_size > 0 else 0)

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.session_state.page_number = st.slider(
            "Page", 1, total_pages, st.session_state.page_number
        )
    with col2:
        if st.button("Select All"):
            st.session_state.selected_pages = set(range(len(images)))
    with col3:
        if st.button("Clear All"):
            st.session_state.selected_pages.clear()

    start_idx = (st.session_state.page_number - 1) * page_size
    end_idx = min(start_idx + page_size, len(images))

    for idx, image in enumerate(images[start_idx:end_idx], start=start_idx):
        is_checked = idx in st.session_state.selected_pages
        if display_image_with_checkbox(image, idx, is_checked):
            st.session_state.selected_pages.add(idx)
        elif idx in st.session_state.selected_pages:
            st.session_state.selected_pages.remove(idx)

    return list(st.session_state.selected_pages)


@st.cache_data
def get_images_cached(pdf_path):
    return get_images(pdf_path)

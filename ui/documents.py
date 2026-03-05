import streamlit as st
from core.document_parser import extract_text
from core.document_extractor import extract_structured_data
from database.crud import save_document, save_document_summary, get_documents_by_user

def render_documents():
    st.title("Upload Document")

    user_id = st.session_state.user["id"]

    # Accept PDFs and images
    file = st.file_uploader(
        "Upload a medical report (PDF or image)",
        type=["pdf", "png", "jpg", "jpeg"]
    )

    if file:
        file_key = f"processed_{file.name}"

        if file_key not in st.session_state:

            existing = get_documents_by_user(user_id)
            existing_names = [d.original_filename for d in existing]

            if file.name in existing_names:
                st.warning(f"'{file.name}' has already been uploaded.")
            else:
                with st.spinner("Processing document..."):
                    text = extract_text(file)

                    if not text.strip():
                        st.error(
                            "Could not extract any text from this file. "
                            "If it's a scanned image, ensure it is clear and well-lit."
                        )
                        return

                    structured = extract_structured_data(text)
                    doc_id = save_document(user_id, file.name)
                    save_document_summary(user_id, doc_id, structured)

                st.session_state[file_key] = structured
                st.success("Document processed successfully.")

        if file_key in st.session_state:
            st.json(st.session_state[file_key])

    # -----------------------
    # Previously uploaded documents
    # -----------------------
    st.markdown("---")
    st.subheader("Uploaded Documents")

    existing = get_documents_by_user(user_id)

    if not existing:
        st.info("No documents uploaded yet.")
    else:
        for doc in existing:
            st.write(
                f"**{doc.original_filename}** — "
                f"uploaded {doc.uploaded_at.strftime('%Y-%m-%d')}"
            )


import base64
import html
import os

import requests
import streamlit as st


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="LegalEase",
    page_icon="⚖️",
    layout="wide",
)


# =========================================================
# BACKEND CONFIGURATION
# =========================================================

BACKEND_URL = st.sidebar.text_input(
    "Backend URL",
    value=os.getenv(
        "LEGALEASE_BACKEND_URL",
            os.getenv("BACKEND_URL", "http://localhost:8000"),
    ),
).rstrip("/")


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
    }

    .legal-preview {
        background: #111827;
        color: #f3f4f6;
        padding: 28px;
        border-radius: 14px;
        max-height: 650px;
        overflow-y: auto;
        white-space: pre-wrap;
        font-family: Georgia, serif;
        line-height: 1.7;
    }

    .app-subtitle {
        color: #6b7280;
        font-size: 1.05rem;
    }

    .warning-box {
        padding: 12px;
        border-radius: 8px;
        background: #fff7ed;
        border: 1px solid #fed7aa;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# HEADER
# =========================================================

st.title("⚖️ LegalEase")

st.markdown(
    '<div class="app-subtitle">'
    "AI-powered legal document drafting, editing and export."
    "</div>",
    unsafe_allow_html=True,
)

st.write("")


# =========================================================
# SESSION STATE
# =========================================================

if "document" not in st.session_state:
    st.session_state.document = ""

if "document_type" not in st.session_state:
    st.session_state.document_type = ""

if "terms" not in st.session_state:
    st.session_state.terms = ""

if "disclaimer" not in st.session_state:
    st.session_state.disclaimer = ""


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.header("📄 Document Details")

    document_type = st.selectbox(
        "Document Type",
        [
            "Employment Contract",
            "Lease Agreement",
            "Non-Disclosure Agreement",
            "Service Agreement",
            "Freelance Work Contract",
            "Employment Offer Letter",
            "Partnership Agreement",
            "Custom Agreement",
        ],
    )

    custom_type = st.text_input(
        "Custom document type",
        placeholder="Example: Software Licensing Agreement",
    )

    parties = st.text_area(
        "Parties Involved",
        placeholder=(
            "Jane Doe (Service Provider), "
            "TechNova Inc. (Client)"
        ),
        height=110,
    )

    terms = st.text_area(
        "Terms & Conditions",
        placeholder=(
            "Payment within 30 days; "
            "Confidentiality must be maintained; "
            "Either party may terminate with 15 days notice"
        ),
        height=160,
        help="Separate individual terms using semicolons (;).",
    )

    effective_date = st.text_input(
        "Effective Date",
        placeholder="September 26, 2026",
    )

    jurisdiction = st.text_input(
        "Jurisdiction",
        placeholder="Tamil Nadu, India",
    )

    additional_instructions = st.text_area(
        "Additional Instructions",
        placeholder=(
            "Example: Keep the document concise "
            "and use formal language."
        ),
        height=100,
    )

    logo = st.file_uploader(
        "Company Logo",
        type=[
            "png",
            "jpg",
            "jpeg",
        ],
    )

    st.divider()

    generate_button = st.button(
        "🚀 Generate Document",
        type="primary",
        use_container_width=True,
    )


# =========================================================
# GENERATION
# =========================================================

if generate_button:

    selected_type = (
        custom_type.strip()
        if custom_type.strip()
        else document_type
    )

    if not parties.strip():

        st.error(
            "Please enter the parties involved."
        )

    elif not terms.strip():

        st.error(
            "Please enter at least one term or condition."
        )

    elif not effective_date.strip():

        st.error(
            "Please enter the effective date."
        )

    else:

        payload = {
            "document_type": selected_type,
            "parties": parties,
            "terms": terms,
            "effective_date": effective_date,
            "jurisdiction": jurisdiction,
            "additional_instructions": (
                additional_instructions
            ),
        }

        try:

            with st.spinner(
                "🤖 Generating your legal document..."
            ):

                response = requests.post(
                    f"{BACKEND_URL}/generate",
                    json=payload,
                    timeout=180,
                )

            if response.ok:

                result = response.json()

                st.session_state.document = (
                    result["content"]
                )

                st.session_state.document_type = (
                    selected_type
                )

                st.session_state.terms = terms

                st.session_state.disclaimer = (
                    result.get(
                        "disclaimer",
                        "",
                    )
                )

                st.success(
                    "Document generated successfully."
                )

            else:

                try:

                    error_data = response.json()

                    error_message = error_data.get(
                        "detail",
                        response.text,
                    )

                except Exception:

                    error_message = response.text

                st.error(
                    f"Backend error: {error_message}"
                )

        except requests.RequestException as exc:

            st.error(
                "Could not connect to the FastAPI backend."
            )

            st.code(
                str(exc)
            )


# =========================================================
# MAIN DOCUMENT AREA
# =========================================================

st.subheader(
    "📑 Document Workspace"
)


if not st.session_state.document:

    st.info(
        "Enter the document details in the sidebar "
        "and click Generate Document."
    )

else:

    preview_tab, edit_tab, download_tab = st.tabs(
        [
            "👁️ Preview",
            "✏️ Edit",
            "⬇️ Downloads",
        ]
    )


    # =====================================================
    # PREVIEW
    # =====================================================

    with preview_tab:

        safe_document = html.escape(
            st.session_state.document
        )

        st.markdown(
            f"""
            <div class="legal-preview">
            {safe_document}
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.write("")

        if st.session_state.disclaimer:

            st.warning(
                st.session_state.disclaimer
            )


    # =====================================================
    # EDIT
    # =====================================================

    with edit_tab:

        edited_document = st.text_area(
            "Edit your document",
            value=st.session_state.document,
            height=650,
        )

        if st.button(
            "💾 Save Edits",
            use_container_width=True,
        ):

            st.session_state.document = (
                edited_document
            )

            st.success(
                "Your edits have been saved."
            )


    # =====================================================
    # DOWNLOADS
    # =====================================================

    with download_tab:

        st.subheader(
            "Export Document"
        )

        st.write(
            "Download your document in the required format."
        )

        # Logo conversion
        logo_base64 = None

        if logo is not None:

            logo_bytes = logo.getvalue()

            logo_base64 = (
                f"data:{logo.type};base64,"
                f"{base64.b64encode(logo_bytes).decode()}"
            )

        export_payload = {
            "document_type": (
                st.session_state.document_type
            ),
            "content": (
                st.session_state.document
            ),
            "terms": (
                st.session_state.terms
            ),
            "logo_base64": logo_base64,
        }

        col1, col2, col3 = st.columns(3)


        # =================================================
        # TXT
        # =================================================

        with col1:

            if st.button(
                "📄 Prepare TXT",
                use_container_width=True,
            ):

                try:

                    response = requests.post(
                        f"{BACKEND_URL}/export/txt",
                        json=export_payload,
                        timeout=60,
                    )

                    if response.ok:

                        st.download_button(
                            "⬇️ Download TXT",
                            data=response.content,
                            file_name=(
                                "legalease_document.txt"
                            ),
                            mime="text/plain",
                            use_container_width=True,
                        )

                    else:

                        st.error(
                            response.text
                        )

                except requests.RequestException as exc:

                    st.error(str(exc))


        # =================================================
        # DOCX
        # =================================================

        with col2:

            if st.button(
                "📝 Prepare DOCX",
                use_container_width=True,
            ):

                try:

                    response = requests.post(
                        f"{BACKEND_URL}/export/docx",
                        json=export_payload,
                        timeout=60,
                    )

                    if response.ok:

                        st.download_button(
                            "⬇️ Download DOCX",
                            data=response.content,
                            file_name=(
                                "legalease_document.docx"
                            ),
                            mime=(
                                "application/vnd.openxmlformats-officedocument."
                                "wordprocessingml.document"
                            ),
                            use_container_width=True,
                        )

                    else:

                        st.error(
                            response.text
                        )

                except requests.RequestException as exc:

                    st.error(str(exc))


        # =================================================
        # PDF
        # =================================================

        with col3:

            if st.button(
                "📕 Prepare PDF",
                use_container_width=True,
            ):

                try:

                    response = requests.post(
                        f"{BACKEND_URL}/export/pdf",
                        json=export_payload,
                        timeout=60,
                    )

                    if response.ok:

                        st.download_button(
                            "⬇️ Download PDF",
                            data=response.content,
                            file_name=(
                                "legalease_document.pdf"
                            ),
                            mime="application/pdf",
                            use_container_width=True,
                        )

                    else:

                        st.error(
                            response.text
                        )

                except requests.RequestException as exc:

                    st.error(str(exc))


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "LegalEase is an AI-assisted legal drafting tool. "
    "It does not provide legal advice. "
    "Review generated documents with a qualified legal "
    "professional before use."
)
"""
Citation Verifier - Streamlit Web Interface

A beautiful web interface for verifying citations in documents using AI.
"""

import streamlit as st
import asyncio
import tempfile
import os
from pathlib import Path
import json

# Set page config
st.set_page_config(
    page_title="Citation Verifier",
    page_icon="✓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import after streamlit config
from src.citation_verifier.main import verify_document
from src.reporters.json_report import generate_json_report
from src.reporters.markdown_report import format_markdown_report


def main():
    """Main Streamlit application."""

    # Header
    st.title("✓ Citation Verifier")
    st.markdown("**AI-powered citation verification** - Stop AI hallucinations by verifying every citation.")

    # Sidebar configuration
    st.sidebar.header("⚙️ Configuration")

    # Model selection
    model = st.sidebar.selectbox(
        "LLM Model",
        [
            "claude-3-5-haiku-20241022",
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229"
        ],
        index=0,
        help="Choose the Claude model for verification. Haiku is faster and cheaper, Sonnet is more accurate."
    )

    # RAG option
    use_rag = st.sidebar.checkbox(
        "Enable RAG for long documents",
        value=False,
        help="Retrieval-Augmented Generation for documents >15,000 characters. Requires ~400MB memory. Disable on low-memory systems."
    )

    # Output format
    output_format = st.sidebar.selectbox(
        "Output Format",
        ["Interactive Display", "JSON", "Markdown"],
        help="Choose how to display verification results"
    )

    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info(
        "Citation Verifier uses Claude AI to verify that sources actually "
        "support the claims made in your documents. Upload a document or "
        "paste a URL to get started."
    )

    # Main content area
    tab1, tab2 = st.tabs(["📄 Upload Document", "🔗 Verify URL"])

    # Tab 1: File Upload
    with tab1:
        st.header("Upload Document")
        st.markdown("Upload a document with citations to verify. Supported formats: **Markdown (.md)**, **PDF (.pdf)**, **HTML (.html)**")

        uploaded_file = st.file_uploader(
            "Choose a file",
            type=["md", "pdf", "html"],
            help="Upload a document containing citations"
        )

        if uploaded_file is not None:
            # Display file info
            st.success(f"✓ File uploaded: **{uploaded_file.name}** ({uploaded_file.size} bytes)")

            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name

            if st.button("🔍 Verify Citations", key="verify_file", type="primary"):
                verify_and_display(tmp_path, model, use_rag, output_format)

                # Cleanup
                os.unlink(tmp_path)

    # Tab 2: URL Input
    with tab2:
        st.header("Verify Document from URL")
        st.markdown("Enter the URL of a document to verify its citations.")

        url = st.text_input(
            "Document URL",
            placeholder="https://example.com/article.html",
            help="Enter the full URL of the document to verify"
        )

        if url:
            if st.button("🔍 Verify Citations", key="verify_url", type="primary"):
                verify_and_display(url, model, use_rag, output_format)

    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666; padding: 20px;'>
            <p>Version 0.1.0</p>
            <p>⚠️ Make sure to set your <code>ANTHROPIC_API_KEY</code> environment variable</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def verify_and_display(source: str, model: str, use_rag: bool, output_format: str):
    """Run verification and display results."""

    # Check API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        st.error("❌ **ANTHROPIC_API_KEY not found!** Please set your API key in the environment.")
        st.code("export ANTHROPIC_API_KEY=your-key-here", language="bash")
        return

    # Progress indicator
    with st.spinner("🔄 Processing document and verifying citations..."):
        try:
            # Run verification
            results = asyncio.run(verify_document(source, use_rag=use_rag))

            if not results:
                st.warning("⚠️ No verifiable claims found in the document.")
                return

            # Display results based on format
            if output_format == "Interactive Display":
                display_interactive_results(results)
            elif output_format == "JSON":
                display_json_results(results)
            elif output_format == "Markdown":
                display_markdown_results(results)

        except Exception as e:
            st.error(f"❌ **Error during verification:** {str(e)}")
            with st.expander("Show error details"):
                st.exception(e)


def display_interactive_results(results: list):
    """Display results in an interactive format."""

    st.success(f"✓ **Verification complete!** Found {len(results)} claims.")

    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)

    verdicts = [r.verdict.value for r in results]

    with col1:
        st.metric("Total Claims", len(results))
    with col2:
        supported = verdicts.count("supported")
        st.metric("✓ Supported", supported, delta=f"{supported/len(results)*100:.0f}%")
    with col3:
        not_supported = verdicts.count("not_supported")
        st.metric("✗ Not Supported", not_supported, delta=f"{not_supported/len(results)*100:.0f}%" if not_supported > 0 else None)
    with col4:
        partial = verdicts.count("partial")
        st.metric("⚠ Partial", partial)

    st.markdown("---")

    # Detailed results
    st.subheader("📋 Detailed Results")

    for i, result in enumerate(results, 1):
        # Verdict color mapping
        verdict_colors = {
            "supported": "green",
            "not_supported": "red",
            "partial": "orange",
            "inconclusive": "gray",
            "source_unavailable": "gray"
        }

        verdict_icons = {
            "supported": "✓",
            "not_supported": "✗",
            "partial": "⚠",
            "inconclusive": "?",
            "source_unavailable": "!"
        }

        color = verdict_colors.get(result.verdict.value, "gray")
        icon = verdict_icons.get(result.verdict.value, "•")

        with st.expander(
            f"{icon} **Claim {i}:** {result.claim.claim_text[:80]}... — **{result.verdict.value.upper()}**",
            expanded=(result.verdict.value in ["not_supported", "partial"])
        ):
            # Claim details
            st.markdown(f"**Full Claim:**")
            st.info(result.claim.claim_text)

            # Source URL
            st.markdown(f"**Source:** [{result.claim.citation_url}]({result.claim.citation_url})")

            # Verdict
            st.markdown(f"**Verdict:** :{color}[{icon} {result.verdict.value.upper()}]")

            # Confidence
            confidence_percent = result.confidence * 100
            st.progress(result.confidence)
            st.caption(f"Confidence: {confidence_percent:.0f}%")

            # Explanation
            st.markdown("**Explanation:**")
            st.write(result.explanation)

            # Source quote (if available)
            if result.source_quote:
                st.markdown("**Source Quote:**")
                st.quote(result.source_quote)

            # Context (if available)
            if hasattr(result.claim, 'original_context') and result.claim.original_context:
                with st.expander("Show context"):
                    st.text(result.claim.original_context)

    # Download options
    st.markdown("---")
    st.subheader("💾 Download Results")

    col1, col2 = st.columns(2)

    with col1:
        # JSON download
        json_data = generate_json_report(results)
        st.download_button(
            label="📥 Download JSON",
            data=json.dumps(json_data, indent=2),
            file_name="verification_results.json",
            mime="application/json"
        )

    with col2:
        # Markdown download
        md_data = format_markdown_report(results)
        st.download_button(
            label="📥 Download Markdown",
            data=md_data,
            file_name="verification_results.md",
            mime="text/markdown"
        )


def display_json_results(results: list):
    """Display results in JSON format."""

    st.success(f"✓ Verification complete! Found {len(results)} claims.")

    json_data = generate_json_report(results)

    st.json(json_data)

    # Download button
    st.download_button(
        label="📥 Download JSON",
        data=json.dumps(json_data, indent=2),
        file_name="verification_results.json",
        mime="application/json"
    )


def display_markdown_results(results: list):
    """Display results in Markdown format."""

    st.success(f"✓ Verification complete! Found {len(results)} claims.")

    md_data = format_markdown_report(results)

    st.markdown(md_data)

    # Download button
    st.download_button(
        label="📥 Download Markdown",
        data=md_data,
        file_name="verification_results.md",
        mime="text/markdown"
    )


if __name__ == "__main__":
    main()

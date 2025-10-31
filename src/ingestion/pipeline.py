from typing import List, Optional
from pathlib import Path
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


class IngestionPipeline:
    """Simple pipeline for loading and splitting PDF documents"""

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        api_key: Optional[str] = None
    ):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n\n", "\n", " ", ""],
            length_function=len,
            add_start_index=True
        )
        self.api_key = api_key

    def process_pdf(self, pdf_path: str) -> List[Document]:
        """Load and split a PDF into chunks"""
        if not Path(pdf_path).exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        if not pdf_path.lower().endswith('.pdf'):
            raise ValueError(f"File must be a PDF: {pdf_path}")

        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        chunks = self.splitter.split_documents(documents)
        return chunks

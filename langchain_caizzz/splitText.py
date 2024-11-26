
from langchain_core.documents.base import Document
from .loadDocuments import extract_text_from_file

from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_and_split_documents(file_path):
    content = extract_text_from_file(file_path)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    texts = text_splitter.split_text(content)
    documents = [Document(page_content=t,metadata={"source": file_path}) for t in texts]  
    return documents

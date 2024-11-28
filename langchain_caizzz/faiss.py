import os
import pickle
import faiss
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_core.documents.base import Document
from uuid import uuid4
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_caizzz.loadDocuments import load_and_split_documents

from logger import logger

def index_init(index_file_path:str,embeddings:OpenAIEmbeddings):

    index = faiss.IndexFlatL2(len(embeddings.embed_query(index_file_path)))
    return index


def vector_store_init(index_file_path:str,embeddings:OpenAIEmbeddings):

    index=index_init(index_file_path,embeddings)
    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=InMemoryDocstore({}),
        index_to_docstore_id={}
    )
    return vector_store


def save_faiss_index(vector_store, index_file_path, mapping_file_path):
    faiss.write_index(vector_store.index, index_file_path)
    with open(mapping_file_path, 'wb') as f:
        pickle.dump({
            'docstore': vector_store.docstore,
            'index_to_docstore_id': vector_store.index_to_docstore_id
        }, f)



def update_vdb(index_file_path:str, mapping_file_path:str, directory_path:str, embeddings:OpenAIEmbeddings):

    if os.path.exists(index_file_path) and os.path.exists(mapping_file_path):
        os.remove(index_file_path)
        os.remove(mapping_file_path)
    

    vector_store=vector_store_init(index_file_path,embeddings)

    # 遍历目录下的所有文件
    for root, _, files in os.walk(directory_path):
        for file in files:
            logger.info(f"Processing file: {file}")
            file_path = os.path.join(root, file)
            documents = load_and_split_documents(file_path)
            uuids = [str(uuid4()) for _ in range(len(documents))]
            vector_store.add_documents(documents=documents, ids=uuids)

    
    # 保存更新后的索引和映射
    save_faiss_index(vector_store, index_file_path, mapping_file_path)



def load_faiss_index(index_file_path, mapping_file_path, embeddings):
    index = faiss.read_index(index_file_path)
    with open(mapping_file_path, 'rb') as f:
        mapping = pickle.load(f)
        docstore = mapping['docstore']
        index_to_docstore_id = mapping['index_to_docstore_id']
    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=docstore,
        index_to_docstore_id=index_to_docstore_id
    )
    return vector_store
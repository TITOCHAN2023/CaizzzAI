
from langchain_core.documents.base import Document
from langchain_caizzz.loadDocuments import extract_text_from_file
from langchain_experimental.text_splitter import SemanticChunker
from langchain_text_splitters import RecursiveCharacterTextSplitter
from embedding import init_embedding


def load_and_split_documents(file_path,embeddings,text_spliter_way:str ="fast"):
    content = extract_text_from_file(file_path)
    if text_spliter_way not in ["fast","percentile","interquartile","standard_deviation","gradient"]:
        return ValueError

    '''分割方法判别'''
    if text_spliter_way=="fast": #硬性分割
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50
        )
        texts = text_splitter.split_text(content)
        documents = [Document(page_content=t,metadata={"source": file_path}) for t in texts]  
        return documents
    
    else: #其他分割方法

        text_splitter = SemanticChunker(embeddings,breakpoint_threshold_type=text_spliter_way)
        docs = text_splitter.create_documents([content])

        
        return docs
        # documents = [Document(page_content=doc.page_content, metadata={"source": file_path}) for doc in docs]
        # return documents
    
if __name__ == "__main__":
    file_path = "test/documents/faissDocuments/陈展鹏python 24.11.9.pdf"
    from env import OPENAI_API_KEY,OPENAI_EMBEDDING_MODEL,OPENAI_BASE_URL
    embeddings = init_embedding(embeddings_name=OPENAI_EMBEDDING_MODEL, base_url=OPENAI_BASE_URL, api_key=OPENAI_API_KEY)  # 初始化嵌入模型
    documents = load_and_split_documents(file_path, embeddings,"percentile")
    for doc in documents:
        print(doc.page_content)
        print('\n\n\n')
    
    ''' 
    硬性分割 fast

    百分位数 percentile
默认的分割方式是基于百分位数。在这个方法中，
会计算所有句子之间的差异，然后将大于X百分位数的任何差异进行分割。

    标准差 standard_deviation
在这个方法中，任何大于X个标准差的差异都会被分割。

    四分位距 interquartile
在这个方法中，使用四分位距来分割文本块。

    梯度 gradient
在这个方法中，使用距离的梯度以及百分位数方法来分割文本块。
当文本块彼此高度相关或特定于某个领域（例如法律或医学）时，
此方法很有用。其理念是在梯度数组上应用异常检测，以便使分布更宽，
并更容易在高度语义化的数据中识别边界。
    '''
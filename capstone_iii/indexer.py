from dotenv import load_dotenv
load_dotenv()

import faiss 
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders.pdf import PyPDFLoader

#Load and split PDFs
pdf_files = ["./pdfs/di_tech-trends-2024.pdf","./pdfs/di_tech-trends-2025.pdf","./pdfs/di_tech-trends-2026.pdf"] 
all_docs = []
for pdf_file in pdf_files:
    loader = PyPDFLoader(pdf_file)
    docs = loader.load()
    all_docs.extend(docs)

#Split text into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=300)
split_docs = splitter.split_documents(all_docs)

#Create embeddings
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

embedding_dim = len(embeddings.embed_query("hello world"))

#Create FAISS index and vector store
index = faiss.IndexFlatL2(embedding_dim)
vector_store = FAISS.from_documents(
    split_docs,
    embeddings
)

#Save vector store
vector_store.save_local("faiss_index")

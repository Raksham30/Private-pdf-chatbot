import io 
import os 

from fastapi import FastAPI , UploadFile , File
from pypdf import PdfReader

from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

model = ChatGoogleGenerativeAI(
    model = "gemini-3.6-flash"
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class LocalEmbedding(Embeddings):

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_documents(self, texts):
        return self.model.encode(texts).tolist()

    def embed_query(self, text):
        return self.model.encode(text).tolist()


embedding_function = LocalEmbedding()   

def create_vector_store():
    return Chroma(
        collection_name="pdf_documents",
        embedding_function=embedding_function,
        persist_directory="./chroma_db"
    )


vector_store = create_vector_store()


def extraxt_text(pdf_bytes : bytes)->str:
    pdf = PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in pdf.pages:
        page_text = page.extract_text()
        
        if page_text:
            text += page_text + "\n"
            
    return text


def split_text(text:str):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 1000,
        chunk_overlap = 150
    )
    chunks = splitter.split_text(text)
    
    return chunks

@app.post('/upload')
async def upload(pdf : UploadFile = File(...)):
    global vector_store
    pdf_bytes = await pdf.read()
    text = extraxt_text(pdf_bytes) 
    chunks = split_text(text)
    documents = []
    
    for i , chunk in enumerate(chunks):
        document = Document(
            page_content= chunk,
            metadata= {
                "file Name" : pdf.filename,
                "chunk id" : i
            }
        )
        documents.append(document)
    vector_store.delete_collection()
    vector_store = create_vector_store()
    vector_store.add_documents(documents)
    
    return {
        "file name" : pdf.filename,
        "total characters" : len(text),
        "total chunks" : len(chunks),
        "chunks" : chunks,
        
    } 
@app.get('/search')
def search(query:str):
    result = vector_store.similarity_search(
        query  , k = 3
    )
    return {
        "query" : query,
        "result" : [
            {
                "content" : doc.page_content ,
                "metadata" : doc.metadata
            }
            for doc in result
        ]
    }
    
@app.post("/chat")
def chat(query : str):
    result = vector_store.similarity_search(
        query ,
        k = 3
    )
    context = "\n\n".join(
        doc.page_content
        for doc in result
    )
    prompt = f"""
You are a helpful assistant answering questions about the uploaded document.

Answer the question using ONLY the provided context.

If the answer cannot be found in the context, say:
"I could not find the answer in the uploaded document."

CONTEXT:
{context}

QUESTION:
{query}

ANSWER:
"""
    response = model.invoke(prompt)

    return {
        "query": query,
        "answer": response.content
    }
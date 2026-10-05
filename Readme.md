# Private PDF Chatbot — RAG Application

A Retrieval-Augmented Generation (RAG) application that allows users to upload a PDF and ask questions about its content.

The application uses a local embedding model to convert document chunks into vectors, ChromaDB for vector storage and retrieval, and Google Gemini for generating answers from the retrieved context.

---

## Features

- Upload a PDF document
- Extract text from PDF
- Split documents into smaller chunks
- Generate embeddings locally using Sentence Transformers
- Store embeddings in ChromaDB
- Perform similarity search
- Retrieve relevant document chunks
- Generate answers using Google Gemini
- React frontend
- FastAPI backend
- Chat-style question answering
- Previous document data is cleared when a new PDF is uploaded

---

## Architecture

```text
                    React Frontend
                         │
             ┌───────────┴───────────┐
             │                       │
          Upload PDF             Ask Question
             │                       │
             ▼                       ▼
          FastAPI                 FastAPI
             │                       │
             ▼                       ▼
       Extract Text          Similarity Search
             │                       │
             ▼                       ▼
          Chunking                ChromaDB
             │                       │
             ▼                       ▼
   Sentence Transformer        Relevant Chunks
             │                       │
             ▼                       ▼
          ChromaDB                Context
                                     │
                                     ▼
                                  Gemini
                                     │
                                     ▼
                                   Answer
                                     │
                                     ▼
                              React Frontend
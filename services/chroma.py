from langchain_chroma import Chroma

from config import settings
from services.embedding import embeddings


def get_vector_store():
    """
    Create/connect to the Chroma vector store.
    """
    vector_store = Chroma(
        collection_name="rag_documents",
        embedding_function=embeddings,
        persist_directory=settings.CHROMA_PATH
    )

    return vector_store


def add_documents(documents, session_id: str):
    """
    Add a user's document chunks to Chroma.
    """

    vector_store = get_vector_store()

    for document in documents:
        document.metadata["session_id"] = session_id

    vector_store.add_documents(documents)

    return vector_store



def get_retriever(session_id: str):

    vector_store = get_vector_store()

    retriever = vector_store.as_retriever(
        search_type="mmr",
        search_kwargs={
            "k": 5,
            "fetch_k": 20,
            "lambda_mult": 0.5,
            "filter": {
                "session_id": session_id
            }
        }
    )

    return retriever




def delete_session_documents(session_id: str):

    vector_store = get_vector_store()

    vector_store._collection.delete(
        where={"session_id": session_id}
    )
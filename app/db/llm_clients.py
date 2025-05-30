import os
from dotenv import load_dotenv
from typing import Optional
from langchain_openai.chat_models import ChatOpenAI
from langchain_openai.embeddings import OpenAIEmbeddings

load_dotenv()

_llm_client_instance: Optional[ChatOpenAI] = None
_embedding_model_instance: Optional[OpenAIEmbeddings] = None


def get_llm_client() -> ChatOpenAI:
    """
    Returns a singleton ChatOpenAI client, initializing if necessary.
    """
    global _llm_client_instance
    if _llm_client_instance is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY must be set in environment variables.")
        try:
            _llm_client_instance = ChatOpenAI(
                openai_api_key=api_key,
                model_name=os.getenv("OPENAI_MODEL_NAME", "gpt-3.5-turbo"),
                temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
            )
            print("Initialized ChatOpenAI LLM client.")
        except Exception as e:
            print(f"Failed to initialize ChatOpenAI client: {e}")
            raise
    return _llm_client_instance


def get_embedding_model() -> OpenAIEmbeddings:
    """
    Returns a singleton OpenAIEmbeddings instance, initializing if necessary.
    """
    global _embedding_model_instance
    if _embedding_model_instance is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY must be set in environment variables.")
        try:
            _embedding_model_instance = OpenAIEmbeddings(
                openai_api_key=api_key,
                model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
            )
            print("Initialized OpenAIEmbeddings model.")
        except Exception as e:
            print(f"Failed to initialize OpenAIEmbeddings: {e}")
            raise
    return _embedding_model_instance

# Example usage:
if __name__ == "__main__":
    try:
        llm_client = get_llm_client()
        embedding_model = get_embedding_model()
        print("LLM client and embedding model are ready for use.")
    except Exception as e:
        print(f"Error initializing LLM client or embedding model: {e}")
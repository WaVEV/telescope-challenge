import logging
from typing import Any, Optional
from langchain.chains.qa_with_sources.retrieval import RetrievalQAWithSourcesChain
from langchain.chat_models import ChatOpenAI
from langchain.chat_models.base import BaseChatModel
from vectorizer_db_factory import VectorStoreDBCreator


# Configure the logging settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class ContextAwareQA:
    """
    Model that answers a query with the most relevant context.

    Args:
        vectorstore_creator (VectorStoreDBCreator): A factory class that provides access to the vector database.
        llm (Optional[BaseChatModel]): A factory class that provides access to the language model (LLM).
    """

    def __init__(self, vectorstore_creator: VectorStoreDBCreator, llm: Optional[BaseChatModel] = None) -> None:
        """
        Initialize the ContextAwareQA model.

        Args:
            vectorstore_creator (VectorStoreDBCreator): A factory class that provides access to the vector database.
            llm (Optional[BaseChatModel]): A factory class that provides access to the language model (LLM).
        """

        self.llm = llm or ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, max_tokens=500)
        self.vectorstore_creator = vectorstore_creator

    def query_with_sources(
        self, question: str, **kwargs: Any
    ) -> dict:
        """
        Query the vector store and retrieve sources relevant to the question.

        Args:
            question (str): The query question.

        Returns:
            dict: A dictionary containing the retrieved sources.

        Raises:
            Any exceptions raised by the underlying retrieval process.
        """
        logger.debug("Processing question: %s.", question)
        vectorstore = self.vectorstore_creator.vectorstore
        """Query the vectorstore and get back sources."""
        chain = RetrievalQAWithSourcesChain.from_chain_type(
            self.llm, retriever=vectorstore.as_retriever(search_kwargs={"k": 3}), **kwargs
        )
        return chain({chain.question_key: question})

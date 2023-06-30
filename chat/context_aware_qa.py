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

    def __init__(self, vectorstore_creator: VectorStoreDBCreator, llm: Optional[BaseChatModel] = None) -> None:
        self.llm = llm or ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0, max_tokens=500)
        self.vectorstore_creator = vectorstore_creator

    def query_with_sources(
        self, question: str, **kwargs: Any
    ) -> dict:
        logger.debug("Processing question: %s.", question)
        vectorstore = self.vectorstore_creator.vectorstore
        """Query the vectorstore and get back sources."""
        chain = RetrievalQAWithSourcesChain.from_chain_type(
            self.llm, retriever=vectorstore.as_retriever(search_kwargs={"k": 3}), **kwargs
        )
        return chain({chain.question_key: question})


if __name__ == '__main__':

    vdb_factory = VectorStoreDBCreator(persistent_directory="chromadb")
    qa = ContextAwareQA(vdb_factory)
    response = qa.query_with_sources("What was Jim Abdo looking for?")
    print(response)
    response = qa.query_with_sources("What is Northrop Grumman?")
    print(response)
    response = qa.query_with_sources("Who is Joe Biden?")
    print(response)

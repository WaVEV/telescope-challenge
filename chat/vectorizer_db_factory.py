import logging
import os
from functools import cached_property
from typing import List
from langchain.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter

from langchain.document_loaders import JSONLoader
from langchain.embeddings import OpenAIEmbeddings


# Configure the logging settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VectorStoreDBCreator:

    def __init__(self, corpora_folder: str = None, corpora_files: List = [], persistent_directory: str = None, llm=None):
        self.corpora_files = corpora_files
        self.corpora_folder = corpora_folder
        self.persistent_directory = persistent_directory
        self._embedding_function = OpenAIEmbeddings()
        self._db = None

    def _load_docs(self, db: Chroma):

        text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
        loaders = [JSONLoader(file, ".body") for file in self.corpora_files]

        if self.corpora_folder:
            loaders += [
                JSONLoader(os.path.join(self.corpora_folder, file), ".body") for file in os.listdir(self.corpora_folder)
            ]

        for loader in loaders:
            logger.info("processing data...")
            documents = loader.load()
            docs = text_splitter.split_documents(documents)
            db.add_documents(docs)

    @cached_property
    def vectorstore(self):

        if self.persistent_directory:
            logger.info("Creating a persistent DB.")
            self._db = Chroma(embedding_function=self._embedding_function, persist_directory=self.persistent_directory)
            self._db.persist()
        else:
            logger.info("Creating a non persistent DB.")
            self._db = Chroma(embedding_function=self._embedding_function)

        if self.corpora_folder or self.corpora_files:
            logger.info("Add new data to the DB.")
            self._load_docs(self._db)

        return self._db


if __name__ == '__main__':
    vdb_factory = VectorStoreDBCreator(persistent_directory="chromadb")
    db = vdb_factory.load_vector_store()

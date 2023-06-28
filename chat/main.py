import logging
import os
from drive_downloader import GoogleDriveDownloader
from context_aware_qa import ContextAwareQA
from vectorizer_db_factory import VectorStoreDBCreator

# Configure the logging settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

if __name__ == '__main__':

    DOWNLOAD_FOLDER = os.getenv("DOWNLOAD_FOLDER", default="downloads")
    VECTOR_DB_DIRECTORY = os.getenv("CHROMADB_FOLDER", default="chromadb")
    DRIVE_CREDENTIAL_FILE = "telescope-391101-0d419a69f595.json"

    if not os.path.exists(DOWNLOAD_FOLDER):
        os.mkdir(DOWNLOAD_FOLDER)

    if not os.listdir(DOWNLOAD_FOLDER):
        gdd = GoogleDriveDownloader(DRIVE_CREDENTIAL_FILE, DOWNLOAD_FOLDER)
        gdd.download_files()

    vdb_factory = VectorStoreDBCreator(persistent_directory=VECTOR_DB_DIRECTORY)
    qa = ContextAwareQA(vdb_factory)

    while True:
        try:
            question = input('Ask me anything(ctrl + D to close):\n')
        except EOFError:
            logger.info("Exiting")
            break
        response = qa.query_with_sources(question)
        print("="*20)
        print(f'Answer: {response["answer"]}')
        print("="*20)
        print(f'Sources: {response["sources"]}')
        print("="*20)

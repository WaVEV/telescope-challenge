import os
from drive_downloader import GoogleDriveDownloader
from context_aware_qa import ContextAwareQA
from vectorizer_db_factory import VectorStoreDBCreator


if __name__ == '__main__':
    DOWNLOAD_FOLDER = "downloads"
    DRIVE_CREDENTIAL_FILE = "telescope-391101-0d419a69f595.json"
    VECTOR_DB_DIRECTORY = "chromadb"
    if not os.path.exists(DOWNLOAD_FOLDER):
        os.mkdir(DOWNLOAD_FOLDER)
        gdd = GoogleDriveDownloader(DRIVE_CREDENTIAL_FILE, DOWNLOAD_FOLDER)
        gdd.download_files()

    vdb_factory = VectorStoreDBCreator(persistent_directory=VECTOR_DB_DIRECTORY)
    qa = ContextAwareQA(vdb_factory)

    while True:
        try:
            question = input('Ask me anything:\n')
        except EOFError:
            break
        response = qa.query_with_sources(question)
        print(response)

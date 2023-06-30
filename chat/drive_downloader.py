import logging
import os
from uuid import uuid4
from typing import Optional
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError


# Configure the logging settings
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class GoogleDriveDownloader:
    """
    A helper class to download files from Google Drive.

    Args:
        credentials_fileno (str): The Google Cloud credential file path.
        destination_folder (Optional[str]): The destination folder where the documents will be stored.
        Default is current directory.
    """

    def __init__(self, credentials_fileno: str, destination_folder: Optional[str] = '.'):
        """
        Initialize the GoogleDriveDownloader.

        Args:
            credentials_fileno (str): The Google Cloud credential file path.
            destination_folder (Optional[str]): The destination folder where the documents will be stored.
            Default is current directory.
        """
        self._credentials_fileno = credentials_fileno
        self._drive_service = None
        self.destination_folder = destination_folder

    def get_document_content(self, file_metadata: dict):
        """
        Download a file from Google Drive.

        Args:
            file_metadata (dict): Metadata of the file to be downloaded.

        Returns:
            str: The path of the downloaded file on the local system.

        Raises:
            HttpError: If an error occurs during the download process.
        """
        new_file_name = None
        try:
            request = self.drive_service.files().get_media(
                fileId=file_metadata["id"])
            new_file_name = os.path.join(self.destination_folder, f'{str(uuid4())}-{file_metadata["name"]}') 
            with open(new_file_name, "wb") as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    logger.info(F'Download {int(status.progress() * 100)}.')

        except HttpError as error:
            logger.error(F'An error occurred: {error}')
            new_file_name = None

        return new_file_name

    @property
    def drive_service(self):
        """
        Get the Google Drive service instance.

        Returns:
            Resource: The Google Drive service instance.

        Raises:
            FileNotFoundError: If the credentials file is not found.
        """
        if not self._drive_service:
            credentials = service_account.Credentials.from_service_account_file(self._credentials_fileno)
            self._drive_service = build('drive', 'v3', credentials=credentials)
        return self._drive_service

    def download_files(self):
        """
        Download all the files from Google Drive.

        Returns:
            None

        Raises:
            Any exceptions raised during the file download process.
        """
        files = self.drive_service.files().list(
            q="mimeType='application/octet-stream'").execute().get('files', [])
        for file in files:
            content = self.get_document_content(file)
            logger.info(content)

    def __delete__(self):
        """
        Clean up resources.

        Returns:
            None
        """
        self.drive_service.close()
        super().__delete__()

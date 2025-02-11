from abc import ABC, abstractmethod
from io import BytesIO
from typing import IO

import requests

# import boto3


class FileFetcher(ABC):
    @abstractmethod
    def fetch(self, config: dict) -> IO:
        """Returns file-like object with data"""


# class S3Fetcher(FileFetcher):
#     def fetch(self, config: dict) -> IO:
#         s3 = boto3.client(
#             "s3",
#             aws_access_key_id=config["aws_access_key"],
#             aws_secret_access_key=config["aws_secret_key"],
#         )
#         obj = s3.get_object(Bucket=config["bucket_name"], Key=config["file_key"])
#         return obj["Body"]


class LocalFileFetcher(FileFetcher):
    def fetch(self, config: dict) -> IO:
        return open(config["file_path"], "rb")


class APIFetcher(FileFetcher):
    def fetch(self, config: dict) -> IO:
        response = requests.get(config["api_url"], headers=config.get("headers", {}))
        response.raise_for_status()
        return BytesIO(response.content)

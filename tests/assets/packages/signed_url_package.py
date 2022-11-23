import logging

from steamship.data.workspace import SignedUrl
from steamship.invocable import InvocableResponse, PackageService, post
from steamship.utils.signed_urls import upload_to_signed_url, url_to_bytes

TEST_STRING = "A happy little test string"


class SignedURLPackage(PackageService):
    @post("writeReadSignedURL")
    def write_read_signed_url(self) -> InvocableResponse:
        logging.info("Starting invocation of signed url test package")
        workspace = self.client.get_workspace()

        filepath = "testPath"
        write_signed_url = workspace.create_signed_url(
            SignedUrl.Request(
                bucket=SignedUrl.Bucket.PLUGIN_DATA,
                filepath=filepath,
                operation=SignedUrl.Operation.WRITE,
            )
        ).signed_url

        logging.info(f"Got signed url for writing: {write_signed_url}")

        upload_to_signed_url(write_signed_url, bytes(TEST_STRING, "utf-8"))
        logging.info("Uploaded to signed url successfully.")

        read_signed_url = workspace.create_signed_url(
            SignedUrl.Request(
                bucket=SignedUrl.Bucket.PLUGIN_DATA,
                filepath=filepath,
                operation=SignedUrl.Operation.READ,
            )
        ).signed_url

        logging.info(f"Got signed url for reading: {read_signed_url}")

        result_bytes = url_to_bytes(read_signed_url)
        result_text = result_bytes.decode("utf-8")

        logging.info(f"Read from signed url: {result_text}")
        return InvocableResponse(string=result_text)

    @post("readSignedURL")
    def read_signed_url(self, filepath: str) -> InvocableResponse:
        logging.info("Starting invocation of signed url test package; read only")
        workspace = self.client.get_workspace()

        read_signed_url = workspace.create_signed_url(
            SignedUrl.Request(
                bucket=SignedUrl.Bucket.PLUGIN_DATA,
                filepath=filepath,
                operation=SignedUrl.Operation.READ,
            )
        ).signed_url

        logging.info(f"Got signed url for reading: {read_signed_url}")

        result_bytes = url_to_bytes(read_signed_url)
        result_text = result_bytes.decode("utf-8")

        logging.info(f"Read from signed url: {result_text}")
        return InvocableResponse(string=result_text)

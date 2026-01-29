import arweave
import os
from django.conf import settings
from arweave.arweave_lib import Transaction
from arweave.transaction_uploader import get_uploader
import mimetypes


def upload_to_arweave(file_path):
    if not os.path.isfile(file_path):
        raise ValueError(f"Invalid file path: {file_path} does not exist or is not a file")
    
    mimetypes.init()
    mimetypes.add_type('image/webp', '.webp')
    mime_type, _ = mimetypes.guess_type(file_path)
    mime_type = mime_type or 'application/octet-stream'
    wallet_path = settings.ARWEAVE_WALLET_PATH
    wallet = arweave.Wallet(wallet_path)

    with open(file_path, "rb", buffering=0) as file_handler:
        tx = Transaction(
            wallet,
            file_handler=file_handler,
            file_path=file_path)
        tx.add_tag('Content-Type', mime_type)
        tx.add_tag('File-Type', mime_type)
        tx.sign()

        uploader = get_uploader(tx, file_handler)

        while not uploader.is_complete:
            uploader.upload_chunk()

        image_url = f"https://arweave.net/{tx.id}"

    return image_url

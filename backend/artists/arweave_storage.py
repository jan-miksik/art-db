import arweave
from django.conf import settings
import os
from arweave.arweave_lib import Transaction
from arweave.transaction_uploader import get_uploader
import logging
import mimetypes
from django.core.files.storage import Storage
from django.conf import settings
import pdb
import uuid



def upload_to_arweave(file_path):
    wallet_path = os.path.join(settings.MEDIA_ROOT, 'arweave_wallet.json')
    wallet = arweave.Wallet(wallet_path)
    """This function uses the arweave package to upload a file."""
    
    logger = logging.getLogger(__name__)
    logger.info("Balance of $AR: %s", wallet.balance)

    mime_type, _ = mimetypes.guess_type(file_path)

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

        logger.info("FILE: %s", file_path)
        logger.info("TRANSACTION: %s\n", f"https://arweave.net/{tx.id}")

        image_url = f"https://arweave.net/{tx.id}"

    return image_url

# class ArweaveStorage(Storage):
#     def _save(self, name, content):
#         # Upload the file to Arweave and return the URL
#         # arweave_url = upload_to_arweave(content.path)
#         return name

#     # class ArweaveStorage(Storage):
#     def _save(self, name, content):
#         if hasattr(content.file, 'temporary_file_path'):
#             file_path = content.file.temporary_file_path()
#         else:
#             if not os.path.isdir('tmp'):
#                 os.mkdir('tmp')
#             with open(f'tmp/{name}', 'wb+') as out_file:
#                 out_file.write(content.file.read())
#             file_path = f'tmp/{name}'
#         arweave_url = self.upload_to_arweave(file_path)
#         return arweave_url

        
#     def exists(self, name):
#         # Arweave is a permanent storage system, so we assume that if a file
#         # was uploaded, it still exists.
#         return True

#     def url(self, name):
#         return name
    
#     def generate_filename(self, filename):
#         pass

# def get_arweave_storage():
#     return ArweaveStorage()
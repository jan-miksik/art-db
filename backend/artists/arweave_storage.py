import arweave
from django.conf import settings
import os
from arweave.arweave_lib import Transaction
from arweave.transaction_uploader import get_uploader
import mimetypes
from django.conf import settings

def upload_to_arweave(file_path):
    mimetypes.init()
    mimetypes.types_map['.webp'] = 'image/webp'
    mime_type, _ = mimetypes.guess_type(file_path)

    wallet_path = os.path.join(settings.MEDIA_ROOT, 'arweave_wallet.json')
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

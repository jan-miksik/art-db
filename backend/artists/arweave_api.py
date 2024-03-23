import arweave
from django.conf import settings
import os

def upload_to_arweave(file):
    wallet_path = os.path.join(settings.MEDIA_ROOT, 'arweave_wallet.json')
    wallet = arweave.Wallet(wallet_path)

    with open(file, 'rb') as f:
        data = f.read()

    transaction = arweave.Transaction(wallet, data=data)
    transaction.sign()
    transaction.send()

    if transaction.is_accepted():
        return transaction.id
    else:
        return None
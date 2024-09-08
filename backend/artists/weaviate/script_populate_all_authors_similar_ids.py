import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'artist_registry.settings')
django.setup()

from artists.weaviate.data_helpers import populate_all_authors_similar_ids

populate_all_authors_similar_ids()

from django.db import models
from .arweave_storage import upload_to_arweave
import weaviate

class Artist(models.Model):
    GENDER_CHOICES = [
        ('M', 'Man'),
        ('W', 'Woman'),
        ('N', 'Non-binary'),
    ]
    notes = models.TextField(default='', blank=True)
    profile_image = models.ImageField(null=True, blank=True)
    firstname = models.CharField(max_length=200, blank=True)
    surname = models.CharField(max_length=200, blank=True)
    born = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    auctions_turnover_2023_h1_USD = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    profile_image_url = models.URLField(blank=True, null=True) #saved to Arweave
    profile_image_weaviate_id = models.CharField(max_length=200, blank=True)
    # profile_image_vector = models.JSONField()

    @property
    def name(self):
        return f"{self.firstname} {self.surname}"

    def __str__(self):
            return f"{self.firstname or ''} {self.surname or ''}"

    class Meta:
        ordering = ['firstname', 'surname']

class Artwork(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)  
    title = models.CharField(max_length=250, default='without name', blank=True)
    picture = models.ImageField(upload_to='artworks/', null=True, blank=True)
    picture_url = models.URLField(blank=True, null=True) #saved to Arweave
    year = models.IntegerField(null=True, blank=True)
    sizeY = models.IntegerField(null=True, blank=True)
    sizeX = models.IntegerField(null=True, blank=True)
    picture_image_weaviate_id = models.CharField(max_length=200, blank=True)
    # picture_vector = models.JSONField()

    # def save(self, *args, **kwargs):
        # Calculate the image vector using Weaviate
        # weaviate_client = weaviate.connect_to_local()
        # self.picture_vector = weaviate_client.data_object.get_vector(self.picture_url)

        # Add the image vector to Weaviate
        # data_properties = {
            # "author": self.author,
            # "arweave_link": self.picture_url,
            # "vector": self.picture_vector,
        # }
        # with weaviate_client.batch.dynamic() as batch:
        #     batch.add_object(properties=data_properties, collection="Artworks")

        # super().save(*args, **kwargs)

    def __str__(self):
        return self.title

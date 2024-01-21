from django.db import models

class Artist(models.Model):
    name = models.CharField(max_length=100)
    notes = models.TextField(default='', blank=True)
    profile_image = models.ImageField(upload_to='artists/', null=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']

class Artwork(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)  
    title = models.CharField(max_length=250, default='', blank=True)
    picture = models.ImageField(upload_to='artworks/', null=True)
# Create your models here.

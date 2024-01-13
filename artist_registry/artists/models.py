from django.db import models

class Artist(models.Model):
    name = models.CharField(max_length=100)
    notes = models.TextField(blank=True)

class Artwork(models.Model):
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)  
    title = models.CharField(max_length=250)

# Create your models here.

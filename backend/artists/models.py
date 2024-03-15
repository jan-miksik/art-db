from django.db import models

class Artist(models.Model):
    GENDER_CHOICES = [
        ('M', 'Man'),
        ('W', 'Woman'),
        ('N', 'Non-binary'),
    ]
    notes = models.TextField(default='', blank=True)
    profile_image = models.ImageField(upload_to='artists/', null=True)
    firstname = models.CharField(max_length=200, blank=True)
    surname = models.CharField(max_length=200, blank=True)
    born = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True)
    auctions_turnover_2023_h1_USD = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

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
    picture = models.ImageField(upload_to='artworks/', null=True)
    year = models.IntegerField(null=True, blank=True)
    sizeY = models.IntegerField(null=True, blank=True)
    sizeX = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.title
# Create your models here.

from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

# Create your models here.


class Review(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(null=True, blank=True, upload_to='reviews_pictures/')
    content = models.TextField()
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    date_posted = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
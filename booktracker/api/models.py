from django.db import models

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey('userauth.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class BookAuthor(models.Model):
    author_name = models.CharField(max_length=255)
    book = models.ForeignKey(Book, related_name='authors', on_delete=models.CASCADE)

    def __str__(self):
        return self.author_name

    class Meta:
        indexes = [
            models.Index(fields=['author_name'], name='author_name_index'),
        ]

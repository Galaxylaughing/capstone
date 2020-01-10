from django.db import models

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey('userauth.User', on_delete=models.CASCADE)
    series = models.ForeignKey('Series', related_name='books', on_delete=models.SET_NULL, null=True)
    position_in_series = models.PositiveIntegerField(null=True)

    def __str__(self):
        return self.title

class BookAuthor(models.Model):
    author_name = models.CharField(max_length=255)
    book = models.ForeignKey(Book, related_name='authors', on_delete=models.CASCADE)
    user = models.ForeignKey('userauth.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.author_name

    class Meta:
        indexes = [
            models.Index(fields=['author_name'], name='author_name_index'),
        ]

class Series(models.Model):
    name = models.CharField(max_length=255)
    planned_count = models.PositiveIntegerField(null=False)
    user = models.ForeignKey('userauth.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class BookTag(models.Model):
    tag_name = models.CharField(max_length=255)
    book = models.ForeignKey(Book, related_name="tags", on_delete=models.CASCADE)
    user = models.ForeignKey('userauth.User', on_delete=models.CASCADE)

    def __str__(self):
        return self.tag_name

    class Meta:
        indexes = [
            models.Index(fields=['tag_name'], name='tag_name_index'),
        ]

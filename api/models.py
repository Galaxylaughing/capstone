from django.db import models
import django.utils.timezone

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey('userauth.User', on_delete=models.CASCADE)
    series = models.ForeignKey('Series', related_name='books', on_delete=models.SET_NULL, null=True)
    position_in_series = models.PositiveIntegerField(null=True)

    page_count = models.PositiveIntegerField(null=True)
    publisher = models.CharField(max_length=255, null=True)
    publication_date = models.CharField(max_length=50, null=True)
    description = models.TextField(null=True)

    # the maximum character count, including potential spaces/hyphens in an isbn-13, is probably 17 or 18.
    # but to be change-safe, I'm going to round up to 20 for both
    isbn_10 = models.CharField(max_length=20, null=True)
    isbn_13 = models.CharField(max_length=20, null=True)

    # from https://docs.djangoproject.com/en/3.0/ref/models/fields/#choices
    WANTTOREAD = 'WTR'
    CURRENT = 'CURR'
    COMPLETED = 'COMP'
    PAUSED = 'PAUS'
    DISCARDED = 'DNF'
    STATUS_CHOICES = [
        (WANTTOREAD, 'Want to Read'),
        (CURRENT, 'Currently Reading'),
        (COMPLETED, 'Completed'),
        (PAUSED, 'Paused'),
        (DISCARDED, 'Discarded'),
    ]
    current_status = models.CharField(
        max_length=4, 
        choices=STATUS_CHOICES, 
        default=WANTTOREAD
    )
    current_status_date = models.DateTimeField(default=django.utils.timezone.now)

    UNRATED = 0
    ONE = 1
    TWO = 2
    THREE = 3
    FOUR = 4
    FIVE = 5
    RATING_CHOICES = [
        (UNRATED,   'Unrated'),
        (ONE,       'One'),
        (TWO,       'Two'),
        (THREE,     'Three'),
        (FOUR,      'Four'),
        (FIVE,      'Five'),
    ]
    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES, 
        default=UNRATED
    )

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

class BookStatus(models.Model):
    user = models.ForeignKey('userauth.User', on_delete=models.CASCADE)
    book = models.ForeignKey(Book, related_name="statuses", on_delete=models.CASCADE)
    date = models.DateTimeField(default=django.utils.timezone.now)
    status_code = models.CharField(max_length=4, choices=Book.STATUS_CHOICES)

    def __str__(self):
        return self.status_code

    class Meta:
        indexes = [
            models.Index(fields=['status_code'], name='status_code_index')
        ]
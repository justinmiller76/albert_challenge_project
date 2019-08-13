from django.db import models


class Book(models.Model):
    """
    Represents a single book in the wish list
    """
    # Couldn't find clear docs on how long this key could be, so err on large
    key_text = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.key_text

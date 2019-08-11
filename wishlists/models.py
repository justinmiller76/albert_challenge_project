from django.db import models


# Represents a single book in the wishlist
class Book(models.Model):
    # Couldn't find clear docs on how long this key could be, so err on large
    key_text = models.CharField(max_length=32, unique=True)

    # TODO: should we locally cache the results of the book details too?

    def __str__(self):
        return self.key_text


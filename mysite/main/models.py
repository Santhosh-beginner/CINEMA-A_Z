from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.


class list(models.Model):
    name = models.CharField(max_length=200)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="todolist", null=True)

    def __str__(self):
        return self.name


class item(models.Model):
    l = models.ForeignKey(list, on_delete=models.CASCADE)
    text = models.CharField(max_length=300)
    checked = models.BooleanField()

    def __str__(self):
        return self.text


class Movie(models.Model):
    """ Database for storing all the information about a movie. the attributes of this class are equivalent to columns of a database
    """

    title = models.CharField(max_length=100, null=True)
    plot = models.CharField(max_length=1000)
    language = models.CharField(max_length=100)
    Director = models.CharField(max_length=100, null=True)
    Producer = models.CharField(max_length=100, null=True)
    Writer = models.CharField(max_length=100, null=True)
    year = models.CharField(max_length=1000)
    duration = models.CharField(max_length=100)
    genre = models.CharField(max_length=100)
    rating = models.CharField(max_length=100)
    platform = models.JSONField(default='{}')
    cast = models.JSONField(default='{}')
    image = models.CharField(max_length=100000, null=True)
    users_wishlist = models.ManyToManyField(
        User, related_name="users_wishlist", blank=True)
    users_favlist = models.ManyToManyField(
        User, related_name="users_fav", blank=True)
    users_watchedlist = models.ManyToManyField(
        User, related_name="users_watchedlist", blank=True)
    rotten_reviews = models.JSONField(default='{}')
    meta_reviews = models.JSONField(default='{}')
    m_rating = models.CharField(max_length=100, null=True)
    similar_movies = models.ManyToManyField('self')

    def _str_(self):
        return self.year


class tvshow(models.Model):
    """ Database for storing all the information about a tv show. the attributes of this class are equivalent to columns of the database
    """
    
    title = models.CharField(max_length=100, null=True)
    plot = models.CharField(max_length=1000)
    rating = models.CharField(max_length=100)
    platform = models.JSONField(default='{}')
    genre = models.CharField(max_length=100)
    cast = models.JSONField(default='{}')
    image = models.CharField(max_length=100000, null=True)
    users_wishlist = models.ManyToManyField(
        User, related_name="users_tvwishlist", blank=True)
    users_favlist = models.ManyToManyField(
        User, related_name="users_tvfav", blank=True)
    users_watchedlist = models.ManyToManyField(
        User, related_name="users_tvwatchedlist", blank=True)
    meta_reviews = models.JSONField(default='{}')
    m_rating = models.CharField(max_length=100, null=True)
    similar_shows = models.ManyToManyField('self')

    def __str__(self):
        return self.title


class Searchclass(models.Model):
    """stores all the typed text in search bar from all users
    """

    name = models.CharField(max_length=20000)
    movieobjects = models.ManyToManyField(Movie)
    tvshowobjects = models.ManyToManyField(tvshow)

    def __str__(self):
        return self.name


class Romancemovies(models.Model):
    title = models.CharField(max_length=100, null=True)
    plot = models.CharField(max_length=1000)
    rating = models.CharField(max_length=100)
    genre = models.CharField(max_length=100)
    cast = models.JSONField(default='{}')
    image = models.CharField(max_length=100000, null=True)
    meta_rating=models.CharField(max_length=100)
    vote=models.CharField(max_length=100)
    Director=models.CharField(max_length=100)
    runtime=models.CharField(max_length=100)
    year=models.CharField(max_length=100)

    def __str__(self) :
        return self.title
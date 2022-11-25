from django.urls import path
from . import views

app_name="main"
urlpatterns=[
    path("",views.start,name="start"),
    path("home/",views.home,name="home"),
    path("index/",views.index,name="index"),
    #path("<int:id>",views.li,name="list"),
    path("create/",views.create,name="create"),
    path("view/",views.view,name="view"),
    path("results/<str:moviename>",views.results,name="results"),
    path("movie/<int:id>",views.cinema,name="movie"),
    path("show/<int:id>",views.show,name="show"),
    path("searchresults/",views.searchresults,name="searchresults"),
    path("romancemovie/<int:id>",views.romance,name="romance"),

    # Wish list
    path("wishlist/", views.wishlist, name="wishlist"),
    path("wishlist/add_to_wishlist/<int:id>", views.add_to_wishlist, name="user_wishlist"),
    path("wishlist/add_to_tvwishlist/<int:id>", views.add_to_tvwishlist, name="user_tvwishlist"),
    # Fav list
    path("favlist/", views.favlist, name="favlist"),
    path("favlist/add_to_favlist/<int:id>", views.add_to_favlist, name="user_favlist"),
    path("favlist/add_to_tvfavlist/<int:id>", views.add_to_tvfavlist, name="user_tvfavlist"),
    # Watched list
    path("watchedlist/", views.watchedlist, name="watchedlist"),
    path("watchedlist/add_to_watchedlist/<int:id>", views.add_to_watchedlist, name="user_watchedlist"),
    path("watchedlist/add_to_tvwatchedlist/<int:id>", views.add_to_tvwatchedlist, name="user_tvwatchedlist"),
]
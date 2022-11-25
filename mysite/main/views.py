from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, HttpResponseRedirect
from .models import *
from .forms import createnew
import requests
from requests.compat import quote_plus
from bs4 import BeautifulSoup
from urllib.parse import quote
from . import func

'''
		some sites doesn't take any get requests sent using requsets.get().'headers' are used for this to pretend that request is being sent from reliable browsers
'''

headers = {
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
}

meta_url = "https://www.metacritic.com/search/movie/{}/results"
show_meta_url = "https://www.metacritic.com/search/tv/{}/results"
base_url = "https://www.rottentomatoes.com/search?search={}"

def romance(response,id):
    mo = Romancemovies.objects.get(id=id)
    return render(response,"main/romance.html",{'mo' : mo})
def start(response):
    """First function that gets called when user requests for the site. It redirects to the /login page, which return the rendered register/login.html
    """
    return HttpResponseRedirect("/login")


def index(response):
    return render(response, "main/base.html", {})


def home(response):
    """ returns the rendered home.html content to the user. Function gets called when a request is sent to home/
    """
    if len(Romancemovies.objects.all()) == 0:
     x=func.sc()
     print(1)
     return render(response, "main/home.html", {'x' : x})
    else:
        movie_obj=[]
        print(2)
        for m in Romancemovies.objects.all():
            movie_obj.append(m)          
        return render(response,"main/home.html", {'x' : movie_obj})


def li(response, id):
    ls = list.objects.get(id=id)
    if response.method == "POST":
        if response.POST.get("save"):
            for item in ls.item_set.all():
                if response.POST.get("c"+str(item.id)):
                    item.checked = True
                else:
                    item.checked = False
                item.save()
        elif response.POST.get("add"):
            txt = response.POST.get("arg1")
            if len(txt) > 2:
                if response.POST.get("arg2"):
                    b = True
                else:
                    b = False
                ls.item_set.create(text=txt, checked=b)
    return render(response, "main/lists.html", {"ls": ls})


def searchresults(response):
    """ Calls results function from views.py with data containing about all the movies and tv shows, if it is present in the movie/tv shows database which are related to the fields movieobjects and 
				tvshowobjects of Searchclass class defined in models.py. If not then it returns rendered results.html. NOTE: There will be a significant waiting time in the second case, where it needs to scrapes
				the data from the websites and stores in database
    """
    search = response.POST.get("search")
    if len(Searchclass.objects.all()) == 0:
        HttpResponseRedirect("/results/%s" % search)
    for s in Searchclass.objects.all():
        if (s.name == search):
            x = s.movieobjects.all()
            y = s.tvshowobjects.all()
            send = {
                "searched": search,
                'movie_obj': x,
                'show_obj': y,
            }
            print("already searched")
            return render(response, "main/results.html", send)
    else:
        return HttpResponseRedirect("/results/%s" % search)


def cinema(response, id):
    """Returns the html file containing the movie info about a particular movie. This function gets called when user sends request to /movie/<int:id>. id is the movie id 
				in the database(primary key generated by default).
    """
    movie = Movie.objects.get(id=id)
    return render(response, "main/particular.html", {"movie": movie})


def show(response, id):
    """ Returns the html file containing the tv show info about a particular show. This function gets called when user sends requests to /show/<int:id>. id is the show id
				in the database (primary key generated by default).
    """
    tvsho = tvshow.objects.get(id=id)
    return render(response, "main/showparticular.html", {"show": tvsho})


def create(response):
    if response.method == "POST":
        form = createnew(response.POST)
        if form.is_valid():
            n = form.cleaned_data["name"]
            t = list(name=n)
            t.save()
            response.user.todolist.add(t)
        return HttpResponseRedirect("/%i" % t.id)
    else:
        form = createnew()
    return render(response, "main/create.html", {"form": form})


def view(response):
    return render(response, "main/view.html", {})


def results(response, moviename):
    """ Gets called when user types the movie name in search bar (indirectly. directly it gets called from searchresults). It checks if the movies/ tv shows exist in the database. if they do
				then it returns ######################## Incomplete ###########################
    """
    # search = response.POST.get("search")
    # print(search)
#   if  response.POST:
    print("new search")
    s10bj = Searchclass(name=moviename)
    s10bj.save()
    final_url = base_url.format(quote_plus(moviename))
    r = requests.get(final_url)
    print(final_url)
    soup = BeautifulSoup(r.content, 'html5lib')
    spr = soup.find_all('search-page-result')
    movie_title = []
    movie_links = []
    movie_rating = []
    movie_images = []
    show_title = []
    show_links = []
    show_rating = []
    show_images = []
    meta_rating = []
    if spr:
        for dat in spr:
            if (dat.get('type')=="movie"):
                x=dat.find_all('search-page-media-row')
                for j in range(0,len(x)):
                    y=x[j].find('a', attrs={'class':'unset', 'slot':'title'})
                    img=x[j].find('a', attrs={'class':'unset', 'slot':'thumbnail'})
                    img1=img.find('img').get('src')
                    if (y.get('href') != ""):
                        movie_links.append(y.get('href'))
                        movie_title.append(y.text.strip())
                        movie_images.append(img1)
                        if x[j].get('tomatometerscore') == "":
                            movie_rating.append('N/A')
                        else:
                            movie_rating.append(x[j].get('tomatometerscore'))
            elif (dat.get('type')=="tv"):
                x=dat.find_all('search-page-media-row')
                for j in range(0, len(x)):
                    y=x[j].find('a', attrs={'class':'unset', 'slot':'title'})
                    img=x[j].find('a', attrs={'class':'unset', 'slot':'thumbnail'})
                    img1=img.find('img').get('src')
                    show_images.append(img1)
                    show_links.append(y.get('href'))
                    show_title.append(y.text.strip())
                    if (x[j].get('tomatometerscore')==""):
                        show_rating.append('N/A')
                    else:
                        show_rating.append(x[j].get('tomoatometerscore'))
    # movies_list=[]
    shows_id = []
    show_obj = []
    movies_id = []
    movie_obj = []
    show_meta_rating = []

    # for dat in range(0,len(show_title)):
    #     shows_list.append((show_title[i],show_links[i],show_cast[i],show_images[i],show_rating[i],show_year[i]))

    # cast_list=[]
    # movie_info_list=[]
    # watch_list=[]
    # scraped=0
    # rotten_reviews_list=[]
    # meta_reviews_list=[]
    for i in range(0, len(show_title)):
        havetocheck1 = False
        for x in tvshow.objects.all():
            if (x.title == show_title[i]):
                tvshow_id = x.id
                show_meta_rating.append('err')
                havetocheck1 = True
                break
        else:
            site = None
            if (show_links[i] != ''):
                site = requests.get(show_links[i])
                print(site)
            else:
                show_meta_rating.append('err')
                continue
            soup = BeautifulSoup(site.content, 'html5lib')
            xv = soup.find_all('img', attrs={'class': 'PhotosCarousel__image'})
            img_url = ""
            if (xv):
                img_url = xv[0].get('src')
                show_images[i] = img_url

            show_info = {}
            plot = soup.find('div', attrs={'id': 'movieSynopsis'}).text.strip()
            show_info['plot:'] = plot
            y = soup.find('section', attrs={
                'id': 'detail_panel'
            })
            if y:
                z = y.find_all('tr')
# print(y)
                for fe in range(0, 3):
                    l = z[fe]
                    show_info[l.find_all("td")[0].text.strip()] = l.find_all("td")[
                        1].text.strip()
            else:
                show_info['Genre:'] = "N/A"
                show_info['plot:'] = "N/A"

            show_watch_dict = {}
            where = soup.find_all('where-to-watch-meta')
            for k in where:
                show_watch_dict[k.get('href')] = k.find(
                    'where-to-watch-bubble').get('image')

            show_cast_dict = {}
            castsection = soup.find('div', attrs={'class': 'castSection'})
            cast_table = []
            if (castsection):
                cast_table = castsection.find_all(
                    'div', attrs={'class': 'cast-item media inlineBlock'})
            for l in cast_table:
                if len(l.find_all('span')) > 1:
                    show_cast_dict[l.find_all('span')[0].text.strip()] = l.find_all('span')[
                        1].text.strip()

            se = show_meta_url.format(quote(show_title[i]))
            print(se)
            got = requests.get(se, headers=headers)
            res = BeautifulSoup(got.content, 'html5lib')
            x = res.find('div', attrs={
                'class': "main_stats"
            })
            if x:
                if x.findChildren():
                   show_meta_rating.append(x.findChildren()[0].text)
            else:
                show_meta_rating.append("N/A")
            print(show_meta_rating)

            searchMeta = "https://www.metacritic.com/search/tv/{}/results"
            movieMeta = "https://www.metacritic.com/tv/{}"
            name = show_title[i].lower()
# name="friends"
            s = requests.Session()
            s.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
            search_results = s.get(searchMeta.format(quote(name)))
            soup = BeautifulSoup(search_results.content, 'html5lib')
            show_reviewsMC = {}
            x = soup.find('h3', attrs={'class': 'product_title basic_stat'})
            if (soup.find('h3', attrs={'class': 'product_title basic_stat'})):
                firstsearch = soup.find(
                    'h3', attrs={'class': 'product_title basic_stat'}).find('a')
                m_url = movieMeta.format(quote(name))
                previews = "{}/user-reviews?dist=positive"
                nreviews = "{}/user-reviews?dist=negative"
                pr = previews.format(m_url)
                nr = nreviews.format(m_url)
                if (BeautifulSoup(s.get(pr).content, 'html5lib').find('div', attrs={'class': 'user_reviews'})):
                    psoup = BeautifulSoup(s.get(pr).content, 'html5lib').find('div', attrs={
                        'class': 'user_reviews'}).find_all('div', attrs={'class': 'review pad_top1'})
                    if psoup:
                        if psoup[0].find('div', attrs={'class': 'right fl'}).find('div', attrs={'class': 'summary'}).find('span'):
                            show_reviewsMC['10'] = psoup[0].find('div', attrs={'class': 'right fl'}).find(
                                'div', attrs={'class': 'summary'}).find('span').text
                        if len(psoup) > 1:
                            show_reviewsMC['8'] = psoup[1].find('div', attrs={'class': 'right fl'}).find(
                                'div', attrs={'class': 'summary'}).find('span').text

                if (BeautifulSoup(s.get(nr).content, 'html5lib').find('div', attrs={'class': 'user_reviews'})):
                    nsoup = BeautifulSoup(s.get(nr).content, 'html5lib').find('div', attrs={
                        'class': 'user_reviews'}).find_all('div', attrs={'class': 'review pad_top1'})
                    if nsoup:
                        if nsoup[0].find('div', attrs={'class': 'right fl'}).find('div', attrs={'class': 'summary'}).find('span'):
                            show_reviewsMC['5'] = nsoup[0].find('div', attrs={'class': 'right fl'}).find(
                                'div', attrs={'class': 'summary'}).find('span').text
                        if nsoup[1].find('div', attrs={'class': 'right fl'}).find('div', attrs={'class': 'summary'}).find('span'):
                            show_reviewsMC['3'] = nsoup[1].find('div', attrs={'class': 'right fl'}).find(
                                'div', attrs={'class': 'summary'}).find('span').text

                print(show_reviewsMC)

            soup = BeautifulSoup(site.content, 'html5lib')
            show_kwargs = []
            similar_names = []
            similar_names_tag = []
            if (soup.find('section', attrs={'id': 'you-might-like'})):
                similar_names_tag = soup.find('section', attrs={
                                              'id': 'you-might-like'}).find_all('span', attrs={'class': 'p--small'})
            for m in similar_names_tag:
                similar_names.append(m.text)
            print(similar_names)
            for n in range(0, len(similar_names)):
                #    if (Movie.objects.filter(title=similar_names[n]).first()):
                #       print(similar_names[n])
                #       kwargs.append(Movie.objects.get(title=similar_names[n]))
                for x in tvshow.objects.all():
                    if (x.title == similar_names[n]):
                        simmovie_id = x.id
                        show_kwargs.append(tvshow.objects.get(id=simmovie_id))
                        break
                else:
                    temp1 = 3
            if show_meta_rating[i] != 'err':
                s1 = tvshow(title=show_title[i], plot=show_info['plot:'],
                            genre=show_info['Genre:'], rating=show_rating[i], platform=show_watch_dict,
                            cast=show_cast_dict, image=show_images[i], meta_reviews=show_reviewsMC, m_rating=show_meta_rating[i])
                s1.save()
                s1.similar_shows.add(*show_kwargs)
                tvshow_id = s1.id
        if havetocheck1:
            if len(shows_id) > 1:
                if tvshow_id not in shows_id:
                    shows_id.append(tvshow_id)
                    show_obj.append(tvshow.objects.get(id=tvshow_id))
                    s10bj.tvshowobjects.add(tvshow.objects.get(id=tvshow_id))
        else:
            shows_id.append(tvshow_id)
            show_obj.append(tvshow.objects.get(id=tvshow_id))
            s10bj.tvshowobjects.add(tvshow.objects.get(id=tvshow_id))

    for i in range(0, len(movie_title)):
        havetocheck = False
        for x in Movie.objects.all():
            if (x.title == movie_title[i]):
                cine_id = x.id
                meta_rating.append('err')
                havetocheck = True
                break
        else:
            site = None
            if (movie_links[i] != ''):
                site = requests.get(movie_links[i])
            else:
                meta_rating.append('err')
                continue
            soup = BeautifulSoup(site.content, 'html5lib')
            xv = soup.find_all('img', attrs={'class': 'PhotosCarousel__image'})
            img_url = ""
            if (xv):
                img_url = xv[0].get('src')
                movie_images[i] = img_url

            movie_info = {}
            plot = soup.find('div', attrs={'id': 'movieSynopsis'}).text.strip()
            movie_info['plot:'] = plot
            y = soup.find('ul', attrs={'class': 'content-meta info'})
            z = y.find_all('li')
            t = z[0].find('div', attrs={'class': 'meta-label subtle'}).text
            if z[0].find('div', attrs={'class': 'meta-value genre'}) != None:
                t1 = z[0].find(
                    'div', attrs={'class': 'meta-value genre'}).text.strip()
                t1 = t1.replace("\n", "")
                t1 = t1.replace(" ", "")
                movie_info[t] = t1
            for j in range(1, len(z)):
                t = z[j].find('div', attrs={'class': 'meta-label subtle'}).text
                t1 = z[j].find(
                    'div', attrs={'class': 'meta-value'}).text.strip()
                t1 = t1.replace("\n", "")
                t1 = t1.replace(" ", "")
                if t == "Release Date (Theaters):" or t == "Release Date (Streaming):":
                    movie_info['Release Date:'] = t1
                else:
                    movie_info[t] = t1
            if 'Release Date:' not in movie_info.keys():
                movie_info['Release Date:'] = 'N/A'
            if 'Director:' not in movie_info.keys():
                movie_info['Director:'] = 'N/A'
            if 'Producer:' not in movie_info.keys():
                movie_info['Producer:'] = 'N/A'
            if 'Writer:' not in movie_info.keys():
                movie_info['Writer:'] = 'N/A'
            if 'Genre:' not in movie_info.keys():
                movie_info['Genre:'] = 'N/A'
            if 'Original Language:' not in movie_info.keys():
                movie_info['Original Language:'] = 'N/A'
            if 'Runtime:' not in movie_info.keys():
                movie_info['Runtime:'] = 'N/A'
            if 'Plot:' not in movie_info.keys():
                movie_info['Plot:'] = 'N/A'

            watch_dict = {}
            where = soup.find_all('where-to-watch-meta')
            x = soup.find_all('where-to-watch-bubble')
            for k in where:
                k.find('where-to-watch-bubble').find()
                watch_dict[k.get('href')] = k.find(
                    'where-to-watch-bubble').get('image')

            cast_dict = {}
            castsection = soup.find('div', attrs={'class': 'castSection'})
            cast_table = []
            if (castsection):
                cast_table = castsection.find_all(
                    'div', attrs={'class': 'cast-item media inlineBlock'})
            for l in cast_table:
                cast_dict[l.find_all('span')[0].text.strip()] = l.find_all('span')[
                    1].text.strip()

            ul = "{}/reviews"
            reviewsRT = {}
            print(movie_links[i])
            if (BeautifulSoup(requests.get(ul.format(movie_links[i])).content, 'html5lib').find('div', attrs={'class': 'review_table'})):
                crtRvwSite = BeautifulSoup(requests.get(ul.format(movie_links[i])).content, 'html5lib').find(
                    'div', attrs={'class': 'review_table'}).find_all('div', attrs={'class': 'row review_table_row'})
                reviewsRT[10] = (crtRvwSite[0].find(
                    'div', attrs={'class': 'the_review'}).text.strip())
                if (len(crtRvwSite) > 1):
                    reviewsRT[6] = (crtRvwSite[1].find(
                        'div', attrs={'class': 'the_review'}).text.strip())
            print(reviewsRT)

            se = meta_url.format(quote(movie_title[i]))
            got = requests.get(se, headers=headers)
            res = BeautifulSoup(got.content, 'html5lib')
            if (res.find('div', attrs={'class': 'main_stats'})):
                print("se")
                print(se)
                if (res.find('div', attrs={'class': 'main_stats'}).findChildren()):
                    meta_rating.append(
                        res.find('div', attrs={'class': 'main_stats'}).findChildren()[0].text)
                    print(meta_rating)
            else:
                print("se")
                print(se)
                meta_rating.append("N/A")
                print(meta_rating)

            searchMeta = "https://www.metacritic.com/search/movie/{}/results"
            movieMeta = "https://www.metacritic.com/{}"
            name = movie_title[i]
            s = requests.Session()
            s.headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
            search_results = s.get(searchMeta.format(quote(name)))
            soup = BeautifulSoup(search_results.content, 'html5lib')
            reviewsMC = {}
            if (soup.find('ul', attrs={'class': 'search_results module'})):
                firstsearch = soup.find(
                    'ul', attrs={'class': 'search_results module'}).find('a')
                m_url = movieMeta.format(firstsearch.get('href'))
                previews = "{}/user-reviews?dist=positive"
                nreviews = "{}/user-reviews?dist=negative"
                pr = previews.format(m_url)
                nr = nreviews.format(m_url)
                if (BeautifulSoup(s.get(pr).content, 'html5lib').find('div', attrs={'class': 'user_reviews'})):
                    psoup = BeautifulSoup(s.get(pr).content, 'html5lib').find('div', attrs={
                        'class': 'user_reviews'}).find('div', attrs={'class': 'review pad_top1'})
                    if psoup:
                        r=psoup.find('div', attrs={'class': 'right fl'}).find('div', attrs={'class': 'summary'}).find('span')
                        if psoup.find('div', attrs={'class': 'right fl'}).find('div', attrs={'class': 'summary'}).find('span', attrs={'class': 'blurb blurb_expanded'}):
                            reviewsMC['10'] = psoup.find('div', attrs={'class': 'right fl'}).find('div', attrs={
                                'class': 'summary'}).find('span', attrs={'class': 'blurb blurb_expanded'}).text
                        elif (r and r.text):
                            reviewsMC['10'] = r.text
                if (BeautifulSoup(s.get(nr).content, 'html5lib').find('div', attrs={'class': 'user_reviews'})):
                    nsoup = BeautifulSoup(s.get(nr).content, 'html5lib').find('div', attrs={
                        'class': 'user_reviews'}).find('div', attrs={'class': 'review pad_top1'})
                    if nsoup:
                        o=nsoup.find('div', attrs={'class': 'right fl'}).find('div', attrs={'class': 'summary'}).find('span')
                        if nsoup.find('div', attrs={'class': 'right fl'}).find('div', attrs={'class': 'summary'}).find('span', attrs={'class': 'blurb blurb_expanded'}):
                            reviewsMC['5'] = nsoup.find('div', attrs={'class': 'right fl'}).find('div', attrs={
                                'class': 'summary'}).find('span', attrs={'class': 'blurb blurb_expanded'}).text
                        elif o and o.text:
                            reviewsMC['5']=o.text



            soup = BeautifulSoup(site.content, 'html5lib')
            kwargs = []
            if (soup.find('section', attrs={'id': 'you-might-like'})):
                similar_names = []
                similar_names_tag = soup.find('section', attrs={
                                              'id': 'you-might-like'}).find_all('span', attrs={'class': 'p--small'})
                for m in similar_names_tag:
                    similar_names.append(m.text)
                print(similar_names)
                for n in range(0, len(similar_names)):
                    #    if (Movie.objects.filter(title=similar_names[n]).first()):
                    #       print(similar_names[n])
                    #       kwargs.append(Movie.objects.get(title=similar_names[n]))
                    for x in Movie.objects.all():
                        if (x.title == similar_names[n]):
                            simmovie_id = x.id
                            kwargs.append(Movie.objects.get(id=simmovie_id))
                            break
                    else:
                        temp = 2
            print(i)
            print(len(movie_title))
            print(len(meta_rating))
            print(meta_rating[i])

            if meta_rating[i] != 'err':
                m1 = Movie(title=movie_title[i], plot=movie_info['plot:'], language=movie_info['Original Language:'],
                           Director=movie_info['Director:'], Producer=movie_info['Producer:'], Writer=movie_info['Writer:'],
                           year=movie_info['Release Date:'], duration=movie_info['Runtime:'],
                           genre=movie_info['Genre:'], rating=movie_rating[i], platform=watch_dict,
                           cast=cast_dict, image=movie_images[i], meta_reviews=reviewsMC, m_rating=meta_rating[i])
                m1.save()
                m1.similar_movies.add(*kwargs)
            # m1.save()
                cine_id = m1.id
        if havetocheck:
            if len(movies_id) > 1:
                if cine_id not in movies_id:
                    movies_id.append(cine_id)
                    movie_obj.append(Movie.objects.get(id=cine_id))
                    s10bj.movieobjects.add(Movie.objects.get(id=cine_id))
        else:
            movies_id.append(cine_id)
            movie_obj.append(Movie.objects.get(id=cine_id))
            s10bj.movieobjects.add(Movie.objects.get(id=cine_id))
    s10bj.save()
    stuff = {
        'searched': moviename,
        'movie_obj': movie_obj,
        'show_obj': show_obj,
    }

    return render(response, "main/results.html", stuff)
#   else:
#     return


def wishlist(request):
    """ This function returns the rendered wishlist.html with data containing about the users wished movies/tv shows. Gets called when a request is sent to wishlist/ url
    """
    movies = Movie.objects.filter(users_wishlist=request.user)
    tvshws = tvshow.objects.filter(users_wishlist=request.user)
    return render(request, "main/watchlist.html", {"mwishlist": movies,"twishlist":tvshws})


def add_to_wishlist(request, id):
    """ Adds/removes the movie data from movie database to the user's wishlist using the ManyToManyField defined in movie class. returns the same page where the request was sent. This function
			gets called when a request is sent to wishlist/add_to_wishlist/<int:id> url with id as the movie id(primary key) in Movie database
    """
    product = get_object_or_404(Movie, id=id)
    if product.users_wishlist.filter(id=request.user.id).exists():
        product.users_wishlist.remove(request.user)
    else:
        if (product.users_watchedlist.filter(id=request.user.id).exists()):
            print("But you've already watched it!")
        else:
            product.users_wishlist.add(request.user)
    return HttpResponseRedirect(request.META["HTTP_REFERER"])

def add_to_tvwishlist(request, id):
    """ Adds/removes the tv show data from tvshow database to the user's wishlist using the ManyToManyField defined in tvshow class. returns the same page where the request was sent. This function
			gets called when a request is sent to wishlist/add_to_tvwishlist/<int:id> url with id as the tvshow id(primary key) in tvshow database
    """
    product = get_object_or_404(tvshow, id=id)
    if product.users_wishlist.filter(id=request.user.id).exists():
        product.users_wishlist.remove(request.user)
    else:
        if (product.users_watchedlist.filter(id=request.user.id).exists()):
            print("But you've already watched it!")
        else:
            product.users_wishlist.add(request.user)
    return HttpResponseRedirect(request.META["HTTP_REFERER"])

def favlist(request):
    """ This function returns the rendered favlist.html with data containing about the users favourite movies/tv shows. Gets called when a request is sent to favlist/ url
    """
    movies = Movie.objects.filter(users_favlist=request.user)
    tvshws = tvshow.objects.filter(users_favlist=request.user)
    return render(request, "main/favlist.html", {"favlist": movies, "tfavlist":tvshws})


def add_to_favlist(request, id):
    """ Adds/removes the movie data from movie database to the user's fav list using the ManyToManyField defined in movie class. returns the same page where the request was sent. This function
			gets called when a request is sent to favlist/add_to_favlist/<int:id> url with id as the movie id(primary key) in Movie database
    """
    product = get_object_or_404(Movie, id=id)
    if product.users_favlist.filter(id=request.user.id).exists():
        product.users_favlist.remove(request.user)
    else:
        product.users_favlist.add(request.user)
    return HttpResponseRedirect(request.META["HTTP_REFERER"])

def add_to_tvfavlist(request, id):
    """ Adds/removes the tv show data from tv show database to the user's favlist using the ManyToManyField defined in tvshow class. returns the same page where the request was sent. This function
			gets called when a request is sent to favlist/add_to_tvfavlist/<int:id> url with id as the tv show id(primary key) in tvshow database
    """
    product = get_object_or_404(tvshow, id=id)
    if product.users_favlist.filter(id=request.user.id).exists():
        product.users_favlist.remove(request.user)
    else:
        product.users_favlist.add(request.user)
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


def watchedlist(request):
    """ This function returns the rendered watchedlist.html with data containing about the user's already watched movies/tv shows. Gets called when a request is sent to watchedlist/ url
    """
    movies = Movie.objects.filter(users_watchedlist=request.user)
    tvshws = tvshow.objects.filter(users_watchedlist=request.user)
    return render(request, "main/watchedlist.html", {"watchedlist": movies, "twatchedlist":tvshws})


def add_to_watchedlist(request, id):
    """ Adds/removes the movie data from movie database to the user's watchedlist using the ManyToManyField defined in movie class. returns the same page where the request was sent. This function
			gets called when a request is sent to watchedlist/add_to_watchedlist/<int:id> url with id as the movie id(primary key) in Movie database
    """
    product = get_object_or_404(Movie, id=id)
    if product.users_watchedlist.filter(id=request.user.id).exists():
        product.users_watchedlist.remove(request.user)
    else:
        if (product.users_wishlist.filter(id=request.user.id).exists()):
            print("shifting movie from wishlist to watchedlist")
            product.users_wishlist.remove(request.user)
        product.users_watchedlist.add(request.user)
    return HttpResponseRedirect(request.META["HTTP_REFERER"])


def add_to_tvwatchedlist(request, id):
    """ Adds/removes the tv show data from tv show database to the user's watchedlist using the ManyToManyField defined in tvshow class. returns the same page where the request was sent. This function
			gets called when a request is sent to watchedlist/add_to_tvwatchedlist/<int:id> url with id as the tv show id(primary key) in tv show database
    """
    product = get_object_or_404(tvshow, id=id)
    if product.users_watchedlist.filter(id=request.user.id).exists():
        product.users_watchedlist.remove(request.user)
    else:
        if (product.users_wishlist.filter(id=request.user.id).exists()):
            print("shifting movie from wishlist to watchedlist")
            product.users_wishlist.remove(request.user)
        product.users_watchedlist.add(request.user)
    return HttpResponseRedirect(request.META["HTTP_REFERER"])
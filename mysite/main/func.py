from requests import get
from bs4 import BeautifulSoup

from time import sleep
from random import randint

from .models import Romancemovies
def sc():
 pages = [1]  # Last time I tried, I could only go to 10000 items because after that the URI has no discernable pattern to combat webcrawlers; I just did 4 pages for demonstration purposes. You can increase this for your own projects.
# If this is not specified, the default language is Mandarin
 headers = {'Accept-Language': 'en-US,en;q=0.8'}

# initialize empty lists to store the variables scraped
 titles = []
 movie_obj=[]
 years = []
 ratings = []
 genres = []
 runtimes = []
 metascores = []
 imdb_ratings=[]
 votes = []
 plots = []
 Directors = []
 castlist = {}
 images = []
# sci-fi
# Horror
 for page in pages:

    # get request for sci-fi
    response = get("https://www.imdb.com/search/title?genres=Romance&"
                   + "start="
                   + str(page)
                   + "&explore=title_type,genres&ref_=adv_prv", headers=headers)

    sleep(randint(8, 15))

    # throw warning for status codes that are not 200
#    if response.status_code != 200:
#        warn('Request: {}; Status code: {}'.format(requests, response.status_code))

    # parse the content of current iteration of request
    page_html = BeautifulSoup(response.text, 'html.parser')

    movie_containers = page_html.find_all(
        'div', class_='lister-item mode-advanced')
    idx=0
    # extract the 50 movies for that page
    for container in movie_containers:
        
        # conditional for all with metascore
        
        if container.find('div', class_='ratings-metascore') is not None:
            idx=idx+1

            # title
            tit = container.h3.a.text
            titles.append(tit)
            if container.find('div', class_='lister-item-image float-left') is not None:
              images.append(container.find(
                'div', class_='lister-item-image float-left').find('a').find('img').get('src'))
            else:
                images.append('')

            if container.h3.find('span', class_='lister-item-year text-muted unbold') is not None:

                # year released
                # remove the parentheses around the year and make it an integer
                ye = container.h3.find(
                    'span', class_='lister-item-year text-muted unbold').text
                years.append(ye)

            else:
                # each of the additional if clauses are to handle type None data, replacing it with an empty string so the arrays are of the same length at the end of the scraping
                years.append("N/A")

            if container.p.find('span', class_='certificate') is not None:

                # rating
                rati = container.p.find('span', class_='certificate').text
                ratings.append(rati)

            else:
                ratings.append("N/A")

            if container.p.find('span', class_='genre') is not None:

                # genre
                gen = container.p.find('span', class_='genre').text.replace("\n", "").rstrip().split(
                    ',')  # remove the whitespace character, strip, and split to create an array of genres
                genres.append(gen)

            else:
                genres.append("N/A")

            if container.p.find('span', class_='runtime') is not None:

                # runtime
                # remove the minute word from the runtime and make it an integer
                time = int(container.p.find(
                    'span', class_='runtime').text.replace(" min", ""))
                runtimes.append(time)

            else:
                runtimes.append("N/A")
            if container.find('p', class_='text-muted') is not None:
                if len(container.find_all('p', class_='text-muted')) > 1:
                    x = container.find_all(
                        'p', class_='text-muted')[1].text.strip()
                    plots.append(x)
            else:
                plots.append("N/A")

            if float(container.strong.text) is not None:

                # IMDB ratings
                # non-standardized variable
                imdb = float(container.strong.text)
                imdb_ratings.append(imdb)

            else:
                imdb_ratings.append("N/A")

            if container.find('p', attrs={'class': ''}):
                x = container.find('p', attrs={'class': ''})
                cast_mov = []
                if (x.find('span')):
                    Directors.append(x.find('a').text.strip())
                    for i in x.find_all('a')[1:]:
                        cast_mov.append(i.text.strip())
                else:
                    Directors.append("N/A")
                    if (x.find_all('a')):
                        for i in x.find_all('a'):
                            cast_mov.append(i.text.strip())
                castlist[titles[idx-1]]=cast_mov

            if container.find('span', class_='metascore').text is not None:

                # Metascore
                # make it an integer
                m_score = int(container.find('span', class_='metascore').text)
                metascores.append(m_score)

            else:
                metascores.append("N/A")

            if container.find('span', attrs={'name': 'nv'})['data-value'] is not None:

                # Number of votes
                vot = int(container.find('span', attrs={
                           'name': 'nv'})['data-value'])
                votes.append(vot)

            else:
                votes.append("N/A")
 for i in range(0,len(titles)):
    m = Romancemovies(title=titles[i],plot=plots[i],rating=imdb_ratings[i],
    genre=genres[i],cast=castlist,image=images[i],meta_rating=metascores[i],
    vote=votes[i],Director=Directors[i],runtime=runtimes[i],year=years[i])
    if i<6:
      m.save()
      movie_obj.append(m)
 
 return movie_obj




# titles = []
#  movie_obj=[]
#  years = []
#  ratings = []
#  genres = []
#  runtimes = []
#  imdb_ratings = []
#  metascores = []
#  votes = []
#  plots = []
#  Director = []
#  castlist = []
#  images = []
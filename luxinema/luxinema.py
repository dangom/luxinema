"""A personal web scrapper to gather LUX Cinema's schedule.

"""
import datetime
import re
from collections import namedtuple
from functools import lru_cache

import pandas as pd
import requests
from bs4 import BeautifulSoup

from luxinema.utils import levenshtein_distance

MOVIEINFO = ['Title', 'Showtime', 'Rating', 'URL', 'Description']
LUXAPI = "https://www.lux-nijmegen.nl/film/?filter={date}"
IMDBAPI = 'https://www.theimdbapi.org/api/movie?movie_id={movie_id}'
GOOGLEAPI = 'https://google.nl/search?q={query}'

HEADERS = {'User-Agent': 'Luxinema'}

Movie = namedtuple('Movie', MOVIEINFO)

def get_today():
    """Return today's date in isoformat without hyphens.

    :returns: Today's date in isoformat without hyphens.
    :rtype: String
    """
    today = datetime.date.today()
    return today.isoformat().replace('-', '')


def get_tomorrow():
    """Return tomorrow's date in isoformat without hyphens.

    :returns: Tomorrow's date in isoformat without hyphens.
    :rtype: String
    """
    tomorrow = datetime.date.today() + datetime.timedelta(days=1)
    return tomorrow.isoformat().replace('-', '')


def get_date(year, month, day):
    """Return arbitrary date in isoformat without hyphens.

    :returns: Arbitrary date in isoformat without hyphens.
    :rtype: String
    """
    return datetime.date(year, month, day).isoformat().replace('-', '')

def get_movie_id(title, api=GOOGLEAPI):
    """Search google for the movie in IMDB. Look at the URL
    to retrieve the movie ID. Assumes that the first IMDB entry
    that Google finds will be the movie we want.

    :param title: Title of the movie (a string)
    :param api: URL of search engine used to retrieve movie id.
    :returns: IMDB's movie ID
    :rtype: string
    """
    year = datetime.date.today().year
    query = title.replace(" ", "+") + '+imdb+' + str(year)
    for char in '!"#$%&\'()*,-./:;<=>?@[\\]^_`{|}~':
        query = query.replace(char, '')

    url = api.format(query=query)
    req = requests.get(url, headers=HEADERS)
    movie_id = re.search('imdb.com/title/(.*?)/', req.text).group(1)
    return movie_id


@lru_cache(maxsize=256)
def request_imdb_json(movie_id):
    """Query IMDB unofficial API for movie info.

    :param movie_id: IMDB movie ID
    :returns: movie data from JSON
    :rtype: dict
    """
    data = requests.get(IMDBAPI.format(movie_id=movie_id),
                        headers=HEADERS).json()
    return data


def verify_movie_id(title, movie_id):
    """Check that a movie_id truly corresponds to the movie we
    searched for.

    :param title: Title as given in the LUX schedule.
    :param movie_id: Movie ID retrieved from Google.
    :returns: movie id integrity
    :rtype: boolean
    """
    data = request_imdb_json(movie_id)
    title_id = data['title'].lower()
    name_ok = levenshtein_distance(title.lower(),
                                   title_id) < 3
    release_year = data['release_date'][:4]
    if release_year:
        year_ok = int(release_year) >= 2016
    else:
        year_ok = True
    return name_ok and year_ok


def get_movie_url(movie_id):
    """From a movie ID, generate it's IMDB URL.

    :param movie_id: String containing movie's IMDB ID.
    :returns: movie URL
    :rtype: string
    """
    return 'https://imdb.com/title/{movie_id}'.format(movie_id=movie_id)


def get_movie_rating_and_description(movie_id):
    """Use IMDB's unofficial API to retrieve a movie's rating and short
    description from it's IMDB movie_id.

    :param movie_id: String containing movie's IMDB ID.
    :returns: rating and description
    :rtype: string, string
    """
    data = request_imdb_json(movie_id)
    rating = data['rating']
    description = data['description']
    return rating, description


def get_lux_schedule(date=None):
    """Get LUX schedule for date. Returns a DataFrame, sorted by rating,
    of all movies still available to be seen.

    :param date: target date
    :returns: DataFrame with movies Title, times, Rating, URL and Description.
    :rtype: Pandas DataFrame
    """
    if date is None:
        date = get_today()

    moviedf = pd.DataFrame(columns=MOVIEINFO)

    luxrequest = requests.get(LUXAPI.format(date=date), headers=HEADERS)
    soup = BeautifulSoup(luxrequest.text, 'html.parser')
    # Ideally we'd query the LUXAPI passing the date and that would be it.
    # Unfortunately, the LUX website throws all info and uses classes to hide
    # dates outside of the filter. This means that we cannot rely on the
    # queryurl alone, but have to double check with data-date.
    movielist = soup.find('ul', {'class': 'items'}).findAll('li', {'data-date' : date})
    movies = [x.find('div', {'class' : 'content-wrap'}) for x in movielist]

    for item in movies:
        title = item.find('h3').text
        times = item.find('div', {'class': 'times'})
        showtime = [time.text for time in times.findAll('span')]
        if not showtime:
            continue
        movie_id = get_movie_id(title)
        if not verify_movie_id(title, movie_id):
            rating, description, movie_url = '-', '-', '-'
        else:
            rating, description = get_movie_rating_and_description(movie_id)
            movie_url = get_movie_url(movie_id)

        movie = Movie(title, showtime, rating, movie_url, description)
        # Append movie to pandas DataFrame
        moviedf.loc[len(moviedf)] = movie._asdict()

    return moviedf.sort_values('Rating', ascending=False).reset_index(drop=True)

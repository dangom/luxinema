"""A personal web scrapper to gather LUX Cinema's schedule.

"""
import datetime
import re
from collections import namedtuple

import pandas as pd
import requests
from bs4 import BeautifulSoup

MOVIEINFO = ['Title', 'Showtime', 'Rating', 'URL', 'Description']
LUXAPI = "https://www.lux-nijmegen.nl/film/?filter={date}"
IMDBAPI = 'https://www.theimdbapi.org/api/movie?movie_id={movie_id}'
GOOGLEAPI = 'https://google.nl/search?q={query}'

HEADERS = {'User-Agent': 'Luxinema/0.0.1 '}

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
    data = requests.get(IMDBAPI.format(movie_id=movie_id),
                        headers=HEADERS).json()
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
        rating, description = get_movie_rating_and_description(movie_id)
        movie_url = get_movie_url(movie_id)
        movie = Movie(title, showtime, rating, movie_url, description)
        # Append movie to pandas DataFrame
        moviedf.loc[len(moviedf)] = movie._asdict()

    return moviedf.sort_values('Rating', ascending=False).reset_index(drop=True)

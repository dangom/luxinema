luxinema
========

-----

Luxinema is a small tool that grabs the movie schedule information
from the LUX cinema in Nijmegen and displays it together with IMDB Ratings.
It is being developed more as a personal learning experience then for
robustness.

Disclaimer: I am not affiliated with the cinema in any way.

.. contents:: **Table of Contents**
    :backlinks: none

Installation
------------

luxinema supports python 3.5 and 3.6.
Either clone the project, or install it with:

.. code-block:: bash

    $ pip install git+https://github.com/dangom/luxinema.git

After installation, you'll need to generate an API key to access the `OMDB API <https://www.omdbapi.com/>`_ and write it as a JSON entry into a file called .luxinema in your home directory. Example *.luxinema* file content:

.. code-block:: json

    {"apikey": "01234567"}


Usage
-------
After installation, running :code:`luxinema` will display the LUX schedule for the current day.
That is currently the only functionality implemented. When running for the first time,
the program may take about 15 seconds to show results, because it has to create a cache
and request the IMDB information for each movie.


Roadmap
-------

- Create a usable CLI Tool.
- Query for specific movie.
- Query for date range, instead of single day.
- Add support for proper caching (redis? Interesting, but easier and simpler with requests_cache).
- Twilio to query infos per SMS.


License
-------

luxinema is distributed under the terms of both

- `MIT License <https://choosealicense.com/licenses/mit>`_
- `Apache License, Version 2.0 <https://choosealicense.com/licenses/apache-2.0>`_

at your option.

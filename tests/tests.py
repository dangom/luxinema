import re

import hypothesis.strategies as st
from hypothesis import given
from luxinema.luxinema import get_movie_id


# Test against symbols, different languages, different letters.
@given(st.sampled_from(('Thelma & Louise', 'Apocalypse Now!',
                        'De Boezemvriend', 'Fack ju Göhte')))
def test_get_movie_id(s):
    movie_id = get_movie_id(s)
    assert re.search(r'tt\d{7}', movie_id)

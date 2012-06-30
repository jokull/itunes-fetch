itunes-fetch: Add URL’s to iTunes
=================================

Because `wget` and drag–n–drop is too much effort. And progress bars.

Prerequisites
-------------

Install the requirements: python-requests, clint and rfc6266.

    $ mkvirtualenv itunes-fetch # Optional but wise
    $ pip install requests clint rfc6266

Usage
-----

Put itunes_fetch.py somewhere on your `$PATH`. Make sure to `chmod +x` it (make
it executable).

    $ workon itunes-fetch
    $ itunes_fetch.py http://www.tld.com/song.mp3

Features
--------

  + Follows redirects
  + Download progress bar
  + Built on python-requests
  + Prints the Content-Disposition’s filename for convenience

#!/usr/bin/env python
# encoding=utf-8

import re
import sys
import tempfile
import mimetypes
import subprocess

from clint.textui import progress, colored
from clint.textui.core import puts, puts_err

import requests
from requests.compat import urlparse
from rfc6266 import parse_requests_response

_itunes_stdout_re = re.compile("file track id (\d+) of library playlist id (\d+) of source id (\d+)")

add_to_itunes = u"""
set new_file to posix file "{path}" as alias
tell application "iTunes" to add new_file
"""

CHUNK_SIZE = 1024 * 10


def fetch(url):

    response = requests.get(url)
    url = urlparse(response.url)  # Follow redirects

    if response.status_code not in range(200, 299):
        sys.exit("Bad response {}".format(response.status_code))

    # If Content-Type header is not found we assume MP3
    content_type = response.headers.get('content-type', 'audio/mpeg')
    if not content_type.startswith("audio/"):
        puts_err("Bad content-type")

    extension = mimetypes.guess_extension(content_type)
    content_disposition = parse_requests_response(response)
    filename = content_disposition.filename_sanitized(extension.lstrip('.'))

    expected_ittimes = None
    content_length = response.headers.get('content-length')
    iter_content = response.iter_content(CHUNK_SIZE)

    puts(colored.blue(u"Downloading {}\n".format(filename)))

    # Display progress bar if content-length is set
    if content_length is not None:
        expected_ittimes = int(content_length) / CHUNK_SIZE
        iter_content = progress.bar(iter_content, expected_size=expected_ittimes)

    with tempfile.NamedTemporaryFile(prefix='song-', suffix=extension, delete=False) \
             as fp:
        for chunk in iter_content:
            fp.write(chunk)

    proc = subprocess.Popen(['osascript', '-'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    out, err = proc.communicate(add_to_itunes.format(path=fp.name))

    if proc.returncode:
        puts_err("Couldn't add to iTunes ({})".format(err))
        sys.exit(proc.returncode)

    match = re.match(_itunes_stdout_re, out)
    if match is not None:
        song, playlist, source = match.groups()
        puts(colored.cyan("Added {} to iTunes!".format(song)))

        # TODO offer to play
        # if prompt.yn(u"Play song? ♬ "):
        #     pass


if __name__ == "__main__":
    if len(sys.argv) > 0:
        url = sys.argv[1]
        fetch(url)

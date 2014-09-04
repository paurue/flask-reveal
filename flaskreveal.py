# -*- coding: utf-8 -*-
"""flask-reveal

Usage:
    flaskreveal start [-d | --debug]
    flaskreveal start [-d | --debug] PATH
    flaskreveal installreveal
    flaskreveal installreveal -f FILE
    flaskreveal installreveal -u URL
    flaskreveal -h | --help

Options:
    -d --debug              Start flask with debug mode on.
    -f FILE --file=FILE     Reveal.js .tar.gz or .zip release file.
    -u URL --url=URL        Url of reveal.js .tar.gz or .zip release file.
    -h --help               Show this help.

"""

import os
import shutil
import tarfile
import zipfile
from urllib import request, error

from docopt import docopt

from flask_reveal.app import create_app


def start(presentation_path, debug_flag):
    """
    Starting flask app function

    :param presentation_path: path to the presentation folder
    :param debug_flag: flag to enable or disable debug
    """

    if os.path.isdir(presentation_path):
        app = create_app(presentation_path)

        app.run(debug=debug_flag)
    else:
        print('This is not a valid directory')


def move_and_replace(src, dst):
    """
    Helper function used to move files from one place to another, creating os replacing them if needed

    :param src: source directory
    :param dst: destination directory
    """

    src = os.path.abspath(src)
    dst = os.path.abspath(dst)

    for src_dir, dirs, files in os.walk(src):  # using os walk to navigate through the directory tree
        # keep te dir structure by replacing the source root to the destination on walked path
        dst_dir = src_dir.replace(src, dst)

        if not os.path.exists(dst_dir):
            os.mkdir(dst_dir)  # to copy not fail, create the not existing dirs

        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)

            if os.path.exists(dst_file):
                os.remove(dst_file)  # to copy not fail, create existing files

            shutil.move(src_file, dst_dir)  # move the files

    shutil.rmtree(src)  # remove the dir structure from the source


def install_reveal_from_file(release_file):
    """
    Install reveal from a given .tar.gz or .zip file

    :param release_file: reveal.js distribution file
    """

    static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), 'flask_reveal/static/'))

    if os.path.isfile(release_file):
        if tarfile.is_tarfile(release_file):
            with tarfile.open(release_file, 'r:gz') as tfile:
                basename = tfile.members[0].name
                tfile.extractall()

            move_and_replace(basename, static_folder)
        elif zipfile.is_zipfile(release_file):
            with zipfile.ZipFile(release_file, 'r') as zfile:
                basename = zfile.namelist()[0]
                zfile.extractall()

            move_and_replace(basename, static_folder)
        else:
            print('File type not supported')
    else:
        print('This is not a valid file')


def install_from_web(release_url):
    """
    Installs reveal.js from a given url

    :param release_url: url of a reveal.js release file
    """

    response = None

    try:
        response = request.urlretrieve(release_url)
    except error.HTTPError as e:
        print('Error while trying to get reveal.js file:\n  {0}'.format(e))
    except ValueError as e:
        print('Value Error:\n  {0}'.format(e))

    if response:
        install_reveal_from_file(response[0])


if __name__ == '__main__':
    arguments = docopt(__doc__)

    if arguments['start']:
        path, debug = arguments['PATH'], arguments['--debug']

        if path:
            start(path, debug)
        else:
            start('./', debug)
    elif arguments['installreveal']:
        file, url = arguments['--file'], arguments['--url']

        if file:
            print('Installing reveal.js from file...')
            install_reveal_from_file(file)
        elif url:
            print('Installing reveal.js from web...')
            install_from_web(url)
        else:
            print('Installing reveal.js from default url...')
            install_from_web('https://github.com/hakimel/reveal.js/archive/2.6.2.tar.gz')

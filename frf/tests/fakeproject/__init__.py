import os

from frf import app

settingsfile = 'frf.tests.fakeproject.settings'
basedir = os.path.abspath(
    os.path.join(os.path.dirname(__file__)))

app.init('fakeproject', settingsfile, basedir)

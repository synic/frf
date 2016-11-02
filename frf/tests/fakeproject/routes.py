from frf.routes import include


routes = [
    ('/api/', include('frf.tests.fakemodule.routes')),
    ]

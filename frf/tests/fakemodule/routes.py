from frf.tests.fakemodule import viewsets

book_viewset = viewsets.BookViewSet()
author_viewset = viewsets.AuthorViewSet()
company_viewset = viewsets.CompanyViewSet()


routes = [
    ('/companies/', company_viewset),
    ('/companies/{id}/', company_viewset),
    ('/books/', book_viewset),
    ('/books/{id}/', book_viewset),
    ('/authors/', author_viewset),
    ('/authors/{uuid1}/{uuid2}/', author_viewset),
    ]

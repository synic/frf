import uuid

from frf import models


class Company(models.Model):
    id = models.Column(models.Integer, primary_key=True)
    name = models.Column(models.String)

    __tablename__ = 'company'


class Author(models.Model):
    uuid1 = models.Column(models.GUID, default=uuid.uuid4, primary_key=True)
    uuid2 = models.Column(models.GUID, default=uuid.uuid4, primary_key=True)
    name = models.Column(models.String)

    company_id = models.Column(
        models.Integer, models.ForeignKey('company.id'))
    company = models.relationship(
        'Company', backref=models.backref('authors'),
        primaryjoin='Author.company_id==Company.id')

    __tablename__ = 'author'


class Book(models.Model):
    id = models.Column(models.Integer, primary_key=True)
    title = models.Column(models.String)
    author_uuid1 = models.Column(
        models.GUID, models.ForeignKey('author.uuid1'))
    author_uuid2 = models.Column(
        models.GUID, models.ForeignKey('author.uuid2'))
    author = models.relationship(
        'Author', backref=models.backref('books'),
        primaryjoin='and_(Book.author_uuid1==Author.uuid1, '
        'Book.author_uuid2==Author.uuid2)')

    __tablename__ = 'book'

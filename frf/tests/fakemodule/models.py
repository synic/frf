# Copyright 2016 by Teem, and other contributors,
# as noted in the individual source code files.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# By contributing to this project, you agree to also license your source
# code under the terms of the Apache License, Version 2.0, as described
# above.

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

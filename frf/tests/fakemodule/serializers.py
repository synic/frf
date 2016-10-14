from frf import serializers

from frf.tests.fakemodule import models


class CompanySerializer(serializers.ModelSerializer):
    id = serializers.IntField()
    name = serializers.StringField()
    authors = serializers.PrimaryKeyRelatedField(
        model=models.Author, many=True)

    class Meta:
        model = models.Author


class AuthorSerializer(serializers.ModelSerializer):
    uuid1 = serializers.UUIDField()
    uuid2 = serializers.UUIDField()
    name = serializers.StringField()
    company = serializers.PrimaryKeyRelatedField(
        model=models.Company)

    books = serializers.PrimaryKeyRelatedField(
        model=models.Book, many=True)

    class Meta:
        model = models.Author


class BookSerialzier(serializers.ModelSerializer):
    id = serializers.IntField()
    title = serializers.StringField()
    author = serializers.PrimaryKeyRelatedField(
        model=models.Author)

    class Meta:
        model = models.Book

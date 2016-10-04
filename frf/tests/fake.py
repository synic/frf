import random
import datetime
import time
import pytz
import hashlib
from dateutil.relativedelta import relativedelta

from faker import Faker
from faker.providers import BaseProvider
from faker.providers.date_time import datetime_to_timestamp

faker = Faker()


class CommonProvider(BaseProvider):
    """
    Misc functions
    """
    def percent(self):
        return random.randint(0, 100) / 100.0

    def version(self):
        return "{0}.{1}.{2}".format(
            random.randint(0, 20), random.randint(0, 5), random.randint(0, 5))


class DateProvider(BaseProvider):
    """
    Various random date functions
    """
    def date_time_in_next_two_weeks(self):
        """
        Provides a day that will occur in the next two weeks.
        """
        now = pytz.utc.localize(datetime.datetime.now())
        start = now + relativedelta(hours=1)
        end = start + relativedelta(days=13)

        return pytz.utc.localize(faker.date_time_between(start, end),
                                 is_dst=True)

    def date_time_in_next_30_days(self):
        """
        Returns a localized datetime that occurs within the next 30 days
        """
        now = pytz.utc.localize(datetime.datetime.now())
        days = random.randint(1, 30)
        start = now + relativedelta(days=days)
        return start


class NameProvider(BaseProvider):
    """
    Different functions for creating names.
    """
    def _create_name(self):
        name = faker.first_name()
        return "%s %s" % (name, hashlib.md5(str(time.time())).hexdigest()[0:7])

    def random_name(self, model_class=None, field='name'):
        """
        Creates a random name.

        Essentially calls 'first_name' +
        md5(str(time.time())).substr(0, 7)

        Can check a model_class for uniqueness if desired.

        Args:
            model_class (django.db.model_classs.Model_Class): Optional
                model_class to check against.
            field (str): If `model_class` is passed, use this field to check
                for uniqueness.
        """
        name = self._create_name()
        if model_class:
            while True:
                try:
                    model_class.objects.get(**{field: name})
                    name = self._create_name()
                except model_class.DoesNotExist:
                    return name

        return name


faker.add_provider(NameProvider)
faker.add_provider(CommonProvider)
faker.add_provider(DateProvider)

import uuid
import datetime
import functools
import json

CONVERSION_MAP = {
    uuid.UUID: lambda x: str(x),
    datetime.datetime: lambda x: x.isoformat(),
}


class EnderJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        for type_, converter in CONVERSION_MAP.items():
            if isinstance(obj, type_):
                return converter(obj)

        return super().default(obj)


class EnderJSONDecoder(json.JSONDecoder):
    pass


serialize = functools.partial(json.dumps, cls=EnderJSONEncoder)
deserialize = functools.partial(json.loads, cls=EnderJSONDecoder)

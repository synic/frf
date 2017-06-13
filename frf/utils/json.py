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

import datetime
import functools
import json
import uuid

CONVERSION_MAP = {
    uuid.UUID: lambda x: str(x),
    datetime.datetime: lambda x: x.isoformat(),
}


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        for type_, converter in CONVERSION_MAP.items():
            if isinstance(obj, type_):
                return converter(obj)

        return super().default(obj)


class JSONDecoder(json.JSONDecoder):
    pass


serialize = functools.partial(json.dumps, cls=JSONEncoder)
deserialize = functools.partial(json.loads, cls=JSONDecoder)

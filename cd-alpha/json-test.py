import json
from collections import OrderedDict

PROTOCOL_FILE_NAME = "cda-protocol-v01.json"

with open(PROTOCOL_FILE_NAME, 'r') as f:
    d = json.loads(f.read(), object_pairs_hook=OrderedDict)

for k, v in d.items():
    print(k, v)
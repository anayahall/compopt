import json

foo = {
	'key1': 'val1',
	'key2': {
		'subkey1': 'subval1'
	}
}

with open('foo.json', 'w') as fp:
    json.dump(foo, fp)
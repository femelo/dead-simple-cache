# Dead Simple Cache

A dead simple thread-safe caching lib powered by [shelve](https://docs.python.org/3/library/shelve.html).

## Usage

Include the plugin as dependency and use it as:

```python
>>> from dead_simple_cache import SimpleCache
>>> cache = SimpleCache(file_path="~/.cache/cache")
>>> cache.add(key="tsf jazz", data={"name": "tsf jazz", "url": "http://tsfjazz.ice.infomaniak.ch/tsfjazz-high.mp3"})
>>> cache.get(query="tsf jazz")
  {'tsf jazz': [{'name': 'tsf jazz',
    'url': 'http://tsfjazz.ice.infomaniak.ch/tsfjazz-high.mp3'}]}
>>> cache.get(query="tsf jas")
    {}
>>> cache.get(query="tsf jas", fuzzy=True)
  {'tsf jazz': [{'name': 'tsf jazz',
    'url': 'http://tsfjazz.ice.infomaniak.ch/tsfjazz-high.mp3'}]}
```

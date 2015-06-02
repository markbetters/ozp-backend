"""
Model (data) access methods

Should support memcache. Basically stuff like:

data = cache.get('stuff')
if data is None:
    data = list(Stuff.objects.all())
    cache.set('stuff', data)
return data
"""
pass
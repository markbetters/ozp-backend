ozp-v3
=====================
Django-based prototype for new OZP backend

## Getting Started
First, install python. You probably want to use a virtualenv, but it's not
required. The app is being developed for Python 3.3+, though it should work with
Python 2.7.6+ as well.

With Python installed (and optionally using a virtualenv), install the
dependencies: `pip install -r requirements.txt`

Now run the server: `./restart_clean_dev_server.sh`

Swagger documentation for the api is available at `http://localhost:8000/docs/`
Use username `wsmith` password `password` when promted for authentication info

There's also the admin interface at `http://localhost:8000/admin`
(username: `admin`, password: `password`)


## For Developers

### Serializers
Serialization = Python obj -> JSON

Deserialization = JSON -> Python obj

DRF does not have a built-in, defacto way of specifying different serializers
for handling input on a request vs output on a Response. Sometimes this is
acceptable, but often times the two structures are not the same. For instance,
some fields may be auto-generated on the server when a POST is made (so they
shouldn't be part of the POST Request data that will be deserialized), but a
GET request should return a Response that includes this information. For
simple cases like this, Serializer fields can be marked as `read_only` or
`write_only` (read_only fields will not become part of the serializer's
validated_data). If more control than this is needed (e.g. very different input
and output formats), the `get_serializer_class()` method can be overridden
in the View and selected dynamically based on request.method (`POST`, `GET`,
etc).

For details regarding input vs output serializers:
* https://github.com/tomchristie/django-rest-framework/issues/1563
* http://stackoverflow.com/questions/17551380/python-rest-framwork-different-serializers-for-input-and-output-of-service

### Model Access
`model_access.py` files should be used to encapsulate database queries. When
reasonable, methods in these files should support a cache:
```
data = cache.get('stuff')
if data is None:
    data = list(Stuff.objects.all())
    cache.set('stuff', data)
return data
```

### Models
Regarding `__str__()`:
It’s important to add `__str__()` methods to your models, not only for your own
convenience when dealing with the interactive prompt, but also because objects’
representations are used throughout Django’s automatically-generated admin.
Note that on Python 2, `__unicode__()` should be defined instead.

By default, fields cannot be null or blank

- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
A note on model validation:
- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
There are three steps involved in validating a model:

1. Validate the model fields - `Model.clean_fields()`
2. Validate the model as a whole - `Model.clean()`
3. Validate the field uniqueness - `Model.validate_unique()`

All three steps are performed when you call a model's `full_clean()` methods.

When you use a `ModelForm`, the call to `is_valid()` will perform these validation
steps for all the fields that are included on the form.

Note that `full_clean()` will NOT be called automatically when you call your
model's `save()` method. You can invoke that method manually when you want to
run one-step model validation for your own models.

Details: https://docs.djangoproject.com/en/1.8/ref/models/instances/#django.db.models.Model.validate_unique

It seems odd at first that Django doesn't enforce model validations at the
'model' level, but there are good reasons for it. Mainly - it's very hard.

* not all ORM methods invoke `Model.save()` (e.g. `bulk_create` and `update`)
* if you use defaults in your models, they will not be set even after
	`Model.save()` returns, thus raising false validation errors
* many things (like Django Admin) don't expect validation errors to occur when
	invoking `Model.save()`, so apps may get 500 errors if you simply call
	`Model.full_clean()` before each `Model.save()`

* http://stackoverflow.com/questions/22587019/how-to-use-full-clean-for-data-validation-before-saving-in-django-1-5-graceful
* http://stackoverflow.com/questions/4441539/why-doesnt-djangos-model-save-call-full-clean/4441740#4441740
* http://stackoverflow.com/questions/13036315/correct-way-to-validate-django-model-objects/13039057#13039057

The recommendation in the last link is to use the `ModelForm` abstraction for
model validation, even if you never display the form in a template.

Also note that although the `max_length` constraint is enforced at both the
database and validation levels, SQLite does not enforce the length of a
VARCHAR

### Views
TODO

### Urls
TODO

### Tests
TODO

### Database
TODO

### Documentation
TODO


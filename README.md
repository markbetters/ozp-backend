ozp-backend
=====================
Django-based backend for OZP

## Getting Started
1. Install Python 3.4.3. Python can be installed by downloading the appropriate
	files [here](https://www.python.org/downloads/release/python-343/). Note
	that Python 3.4 includes both `pip` and `venv`, a built-in replacement
	for the `virtualenv` package
2. Create a new python environment using python 3.4.x. First, create a new
	directory where this environment will live, for example, in
	`~/python_envs/ozp`. Now create a new environment there:
	`python3.4 -m venv ENV` (where `ENV` is the path you used above)
3. Active the new environment: `source ENV/bin/activate`
4. Install the necessary dependencies into this python environment:
	`pip install -r requirements.txt`
5. Run the server: `./restart_clean_dev_server.sh`

Swagger documentation for the api is available at `http://localhost:8000/docs/`
Use username `wsmith` password `password` when prompted for authentication info

There's also the admin interface at `http://localhost:8000/admin`
(username: `wsmith`, password: `password`)


## For Developers
Understanding this project requires knowing a small-medium amount of Django and
a large amount of Django Rest Framework (DRF). From Django itself:
* Object-relational mapper (ORM)
* Authentication
* `manage.py` utility (testing, database migration)
* Caching
* Logging
* Settings

Most of the URLs and Views are done with DRF, and very little is done with
templating, forms, and the admin site

### Serializers
Serialization = Python obj -> JSON

Deserialization = JSON -> Python obj

DRF does not have a built-in, defacto way of specifying different serializers
for handling input on a request vs output on a Response. Sometimes this is
acceptable, but often times the two structures are not the same. For instance,
some fields may be auto-generated on the server when a `POST` is made (so they
shouldn't be part of the `POST` Request data that will be deserialized), but a
`GET` request should return a Response that includes this information. For
simple cases like this, Serializer fields can be marked as `read_only` or
`write_only` (`read_only` fields will not become part of the serializer's
`validated_data`). If more control than this is needed (e.g. very different input
and output formats), the `get_serializer_class()` method can be overridden
in the View and selected dynamically based on request.method (`POST`, `GET`,
etc).

For details regarding input vs output serializers:
* https://github.com/tomchristie/django-rest-framework/issues/1563
* http://stackoverflow.com/questions/17551380/python-rest-framwork-different-serializers-for-input-and-output-of-service

Sometimes it might not be clear where the Serializer classes should live for
nested objects. For example, the listing resource needs to serialize the nested
Agency model - should that Agency serializer live in the listing resource
package or in the agency package? Generally speaking, if the serializer is
very generic, it should live in its respective resource package. If instead
it's highly customized (and thus unlikely to be used by other resources), it
should live with its nested resource.

One annoyance with nested serializers is that, if doing a create/POST, DRF
assumes that each nested resource should also be created. This causes validation
errors to be raised when doing things like creating a new listing with an
existing category, listing type, etc. The way around that problem is to
explicitly remove all validation on any nested serializer fields that have
unique constraints. For example, for a serializer with a `title` field:
```
extra_kwargs = {
            'title': {'validators': []}
        }
```
Because we don't want to remove the validator for the base resource (only when
it's used in a nested fashion), some of the more complicated resources (namely
Listing) have lots of nested serializers that are identical to their non-nested
counterparts save for the removal of the unique field validators

### Model Access and Caching
`model_access.py` files should be used to encapsulate more complex database
queries and business logic (as opposed to placing it in Views and Serializers).
These methods are easier to use in sample data generators, and allows the
complexity of Django Rest Framework to stay largely separate from the core
application logic

This is also the layer to implement object/query caching, such as:
```
data = cache.get('stuff')
if data is None:
    data = list(Stuff.objects.all())
    cache.set('stuff', data)
return data
```
Note that we also need logic to invalidate specific caches when resources are
modified. For example, if a Listing is updated, all cached items referring/using
that listing's data should be invalidated. By far and large, this logic is not
yet in place, so enabling the cache will likely lead to unexpected results

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
Nothing much special to say about views, except that we generally prefer to
use class-based views and `ViewSet`s (`ModelViewSet`s in particular) just
because it's less code (assuming you don't require a significant amount of
customization)

The use of the convenience method `get_object_or_404` breaks the encapsulation
of database queries in the `model_access` files (and prevents caching). That
might be something to look at later on.

### URLs
All resource endpoints are defined in the resource's respective `urls.py` in
`ozpcenter/api/`. `ozpcenter.urls` collects all of these endpoints, where they
are given the `api/` prefix in the global `urls.py`

DRF uses a browsable API, meaning that you can go to
`localhost:8000/api/metadata` (for instance) in your browser. In general, the
Swagger documentation is the recommended way to view and interact with the API

### Authentication and Authorization
Authentication and authorization is based on the default `django.contrib.auth`
system built into Django, with numerous customizations.

The default User model is extended by giving the `Profile` model a one-to-one
relationship with the `django.contrib.auth.models.User` model, as described
[here](https://docs.djangoproject.com/en/1.8/topics/auth/customizing/#extending-the-existing-user-model)

The default [User](https://docs.djangoproject.com/en/1.8/ref/contrib/auth/#user)
model has the following fields:

* username
* first_name
* last_name
* email
* password
* groups (many-to-many relationship to Group)
* user_permissions (many-to-many relationship to Permission)
* is_staff (Boolean. Designates whether this user can access the admin site)
* is_active (Boolean. Designates whether this user account should be considered
	active)
* is_superuser (Boolean. Designates that this user has all permissions without
	explicitly assigning them)
* last_login (a datetime of the user's last login)
* date_joined (a datetime designating when the account was created)

Of these fields:

* first_name and last_name are not used
* is_superuser is always set to False
* is_staff is set to True for Org Stewards and Apps Mall Stewards
* password is only used in development. On production, client SSL certs are
	used, and so password is set to TODO: TBD

[Groups](https://docs.djangoproject.com/en/1.8/topics/auth/default/#groups) are
used to categorize users as Users, Org Stewards, Apps Mall Stewards, etc. These
groups are used to partially control access to various resources (for example,
Users cannot make modifications to the Categories). That said, the majority
of 'access control' cannot be accomplished by creating generic permissions
and groups. For example, an Org Steward should be able to approve a Listing only
for organizations to which they belong. Furthermore, any resources (Listings,
Images) that have a specific access_control associated with them must be
hidden from users (regardless of role/group) without the appropriate level
of access.

Django Permissions are used to control access to the Admin site. By default,
add, change, and delete permissions are added to each model in the application.
The notion of separate permissions for these three operations don't make much
sense for this application - for now, the default permissions will be left
alone, but the Permissions infrastructure won't be used much beyond that. As
previously stated, it is not possible to create generic permissions that can
be statically assigned to users, like 'can_approve_listing', since the
allowance of such an action depends on the object (model instance), not just the
model type. Therefore, custom object-level permissions will typically be used
to control access to specific resource instances (for both read and write
operations). For list queries where multiple resources are returned, these
object-level permission checks are not used. Instead, filters and custom
querysets are used to ensure only the appropriate data is returned.


In production, `django-ssl-client-auth` is used for the authentication backend
to support PKI

### Tests
Generally speaking, each resource (listing, agency, profile, etc) may have
two types of tests: business logic tests and API tests. The former typically
tests code in `model_access.py` files, which is pure Python code and independent
of Django or any "web stuff". The latter API tests, on the other hand, actually
make HTTP requests using special testing clients and factories, and are more
like end-to-end or integration tests

### Database
TODO

### Documentation
There are a number of different documentation resources available, depending
on what you're looking for.

DRF's Web Browsable API can be accessed by entering an endpoint in the browser,
for example, `<rootUrl>/api/profile/`.  Limitations:
 * the API Root doesn't have a list of all endpoints, so you need to know
 what you're looking for
 * although these pages include forms that could potentially support POST
 requests, they don't work very well, making the browsable API mostly useless
 for non-GET requests

 Swagger docs are created via Django REST Swagger and served at
 `<rootUrl>/docs/`. Swagger makes it easy to see all of the endpoints available.
 Unlike the Browsable API docs, Swagger supports POST, PUT, and DELETE for most
 of the endpoints as well. Limitations:
  * POST api/image/ doesn't work from Swagger
  * some of the more complicated endpoints (like POST api/listing/) might not
  have forms that show all of the required and/or optional data that must or
  could be included in the request

 Postman was used extensively during the API's development, and perhaps someday
 a Postman Collection of requests will be added to this repo

### Logging
Currently, a single logger (`ozp-center`) is used throughout the application.
See `settings.py` for details

### Static and Media Files
Static files: JS, CSS, fonts, etc. Media files: images uploaded during app
usage. Good explanation [here](http://timmyomahony.com/blog/static-vs-media-and-root-vs-path-in-django/)

Production static file server: Nginx (TBD)

NOTE: We can't serve /media files statically, as access control must be enforced
on each of them

### Scripts
The `runscript` command is installed via the django-extensions package and used
to run scripts in the django context, just as you would get by running a set
of commands in the shell using `python manage.py shell`. This can be used
to run the script to populate the database with sample data:
`python manage.py runscript sample_data_generator`. See the
[docs](http://django-extensions.readthedocs.org/en/latest/runscript.html) for
details

### API Input
All POST, PUT, and PATCH endpoints should use JSON encoded input as per
[this](http://www.vinaysahni.com/best-practices-for-a-pragmatic-restful-api#json-requests)

### Django Admin Site
The admin site is currently enabled in development (but will likely be
disabled in production). It is accessible by both Apps Mall Stewards and
Org Stewards. It has a number of limitations, including the inability to upload
images (since images aren't stored in the database), and the fact that many
operations (like editing reviews, approving listings, etc) should result in
additional operations (like creating ListingActivity entries), but using
the Admin interface directly bypasses that logic


## Controlling Access
Anonymous users have no access - all must have a valid username/password (dev)
or valid certificate (production) to be granted any access

A few endpoints only provide READ access:

* storefront
* metadata

Several resources allow global READ access with WRITE access restricted to
Apps Mall Stewards:

* access_control
* agency
* category
* contact_type
* listing_type

image

* global READ
* WRITE access allowed for all users, but the associated access_control level
	cannot exceed that of the current user

intent

* global READ and WRITE allowed, but associated intent.icon.access_control
	cannot exceed that of the current user

library

* READ access for ORG stewards and above
* no WRITE access
* READ and WRITE access to /self/library for the current user

notification

* global READ access
* WRITE access restricted to Org Stewards and above, unless the notification
	is associated with a Listing owned by this user
* READ and WRITE access to /self/notification for the current user

profile

* READ access restricted to Org Stewards and above
* WRITE access restricted to the associated user (users cannot create, modify,
	or delete users other than themselves)
* READ and WRITE access to /self/profile for the current user


listing

* READ access restricted by agency (if listing is private) and by access_control
	level
* WRITE access:
	* global WRITE access to create/modify/delete a listing in the draft or
		pending state ONLY
	* Org Stewards and above can change the state to published/approved or
		rejected, and change state to enabled/disabled, but must respect
		Organization (an Org Steward cannot modify
		a listing for which they are not the owner and/or not a member of
		the listing's agency)
	* global WRITE access to create/modify/delete reviews (item_comment) for
		any listing (must respect organization (if private) and access_control
		)
* READ access to /self/listing to return listings that current user owns (?)






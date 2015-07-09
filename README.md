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

### Model Access and Caching
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
Nothing much special to say about views, except that we generally prefer to
use class-based views and `ViewSet`s (`ModelViewSet`s in particular) just
because it's less code (assuming you don't require a significant amount of
customization)

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
TODO

### Database
TODO

### Documentation
TODO

### Logging
TODO

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






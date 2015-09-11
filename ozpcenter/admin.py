"""
Models for use with the Admin interface

Available at /admin

run python manage.py createsuperuser to create an admin user/password
"""
from django.contrib import admin
import ozpcenter.models as models

# Register models for admin interface
admin.site.register(models.AccessControl)
admin.site.register(models.Agency)
admin.site.register(models.ApplicationLibraryEntry)
admin.site.register(models.Category)
admin.site.register(models.ChangeDetail)
admin.site.register(models.Contact)
admin.site.register(models.ContactType)
admin.site.register(models.DocUrl)
admin.site.register(models.Image)
admin.site.register(models.ImageType)
admin.site.register(models.Intent)
admin.site.register(models.Review)
admin.site.register(models.Profile)
admin.site.register(models.Listing)
admin.site.register(models.ListingActivity)
admin.site.register(models.Screenshot)
admin.site.register(models.ListingType)
admin.site.register(models.Tag)
admin.site.register(models.Notification)

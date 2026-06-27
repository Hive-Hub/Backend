from django.contrib import admin
from .models import Resource, StoredFile, ResourceLibrary

admin.site.register(Resource)
admin.site.register(StoredFile)
admin.site.register(ResourceLibrary)


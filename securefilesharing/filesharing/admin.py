from django.contrib import admin
from .models import UploadedFile
from .models import SharedFile
from .models import hashTable
from .models import UserProfile

# Register your models here.
admin.site.register(UploadedFile)
admin.site.register(SharedFile)
admin.site.register(hashTable)
admin.site.register(UserProfile)


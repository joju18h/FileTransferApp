"""
This module contains the models for the file sharing application. It defines the following models:
- UserProfile: extends the User model provided by Django's authentication framework
- UploadedFile: represents a file uploaded by a user
- SharedFile: represents a file shared by one user to another
- hashTable: represents a hash table for file integrity (not actively used, the values are still stored in the database)
"""
from django.db import models
from django.contrib.auth.models import User

#extension of user model
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    class Meta:
        #django was having trouble with the UserProfile model, this fixed it. We dont have mutliple apps in the project 
        #so this should not normally be needed
        app_label = 'filesharing'

#uploaded file model, auth tag discarded since we are using fernet. Kept in case we want to switch back to GCM
class UploadedFile(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads/')
    file_key = models.BinaryField() #AES key
    file_name = models.CharField(max_length=255)
    file_size = models.BigIntegerField() #In bytes
    upload_date = models.DateTimeField(auto_now_add=True)
    auth_tag = models.BinaryField(default=b'') # was GCM authentication tag is now redundant since we are using fernet

    #for faciliating file remove view
    def delete_file(self):
        # Delete the file from storage
        self.file.delete()

        # Delete the UploadedFile instance
        self.delete()
        
        def __str__(self):
            return self.name
        

#shared file model
class SharedFile(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    shared = models.ForeignKey(UploadedFile, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True) #Timestamp of share creation

#hash table model was included in case we wanted to implement a hash table for file integrity but was not actively used, kept in case we want to implement it later
class hashTable(models.Model):
    file = models.ForeignKey(UploadedFile, on_delete=models.CASCADE)
    hash_value = models.CharField(max_length=64) #SHA256 hash
    timestamp = models.DateTimeField(auto_now_add=True) #Timestamp of hash creation

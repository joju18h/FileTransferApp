"""
This module contains forms for file sharing app. It includes forms for user registration, file upload and file sharing.
Default django form classes (some were extended to modify the output) were used to create the forms.
UserRegistrationForm: A form for user registration that inherits from UserCreationForm.
FileUploadForm: A form for file upload that uses UploadedFile model.
FileShareForm: A form for file sharing that uses SharedFile model. It has two fields, 'to_user' and 'shared'. 
The 'to_user' field is a dropdown list of users excluding the current user. The 'shared' field is a dropdown list of files uploaded by the current user.
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import UploadedFile, SharedFile

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = UploadedFile
        fields = ['file']

class FileShareForm(forms.ModelForm):
    class Meta:
        model = SharedFile
        fields = ['to_user', 'shared']

    #customizes the behavior of the FileShareForm based on the provided 'user' parameter
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(FileShareForm, self).__init__(*args, **kwargs)

        #was seeing other users, this fixed it
        if user:
            self.fields['to_user'].queryset = User.objects.exclude(id=user.id)

        # was seeing other users file and object string reps. this fixed it
        if user:
            self.fields['shared'].queryset = UploadedFile.objects.filter(owner=user)
            self.fields['shared'].label_from_instance = lambda obj: f"{obj.file_name}"
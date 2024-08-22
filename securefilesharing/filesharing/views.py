"""
This module contains views for the file sharing application. It allows users to upload, share, and download files securely.

Dependencies:
- django
- cryptography
- hashlib

Functions:
- home(request): Renders the home page with user profile, uploaded files, and shared files.
- upload_file(request): Handles file upload and encryption.
- share_file(request): Handles file sharing with other users.
- download_file(request, file_id): Handles file download and decryption for files uploaded by the user.
- download_shared_file(request, shared_file_id): Handles file download and decryption for files shared with the user.
- signup_view(request): Handles user signup.
- delete_file(request, file_id): Handles file deletion for files uploaded by the user.
"""

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import UserProfile, UploadedFile, SharedFile, hashTable
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from .forms import FileUploadForm
from django.core.files.base import ContentFile
from .forms import FileShareForm
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

#encryption
from cryptography.fernet import Fernet
import os

#hashing
import hashlib

from django.http import HttpResponse
from django.core.exceptions import PermissionDenied


#login required decorator used to ensure that only logged in users can access the views
@login_required
def home(request):
    try:
        userprofile = UserProfile.objects.get(user=request.user)
        uploadedfiles = UploadedFile.objects.filter(owner=request.user)
        sharedfiles = SharedFile.objects.filter(to_user=request.user)
        context = {
            'userprofile': userprofile,
            'uploadedfiles': uploadedfiles,
            'sharedfiles': sharedfiles
        }
    except UserProfile.DoesNotExist:
        userprofile = UserProfile(user=request.user)
        userprofile.save()
        context = {
        'userprofile': userprofile,
        'uploadedfiles': None,
        'sharedfiles': None
        }

    return render(request,'home.html',context)

@login_required
def upload_file(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)

        if form.is_valid():
            file = form.cleaned_data['file']
            owner = request.user
            file_name = file.name
            file_size = file.size

            # Encryption
            key = Fernet.generate_key()  # Generate a new Fernet key
            cipher_suite = Fernet(key) # Create a fernet key object

            # Encrypt file
            encrypted_file = cipher_suite.encrypt(file.read())

            # Save file
            uploadedfile = UploadedFile(owner=owner, file_name=file_name, file_size=file_size, file_key=key)
            uploadedfile.file.save(file_name, ContentFile(encrypted_file))  # Save the ContentFile to the FileField
            uploadedfile.save()

            # Hash file
            hash_object = hashlib.sha256()
            hash_object.update(encrypted_file)
            hash_value = hash_object.hexdigest()

            # Save hash
            file_hash = hashTable(file=uploadedfile, hash_value=hash_value)
            file_hash.save()

            messages.success(request, 'File uploaded successfully')
            return redirect('home')
        else:
            messages.error(request, 'Form submission failed. Please check the form.')
    else:
        form = FileUploadForm()

    return render(request, 'upload_file.html', {'form': form})



@login_required
def share_file(request):
    if request.method == 'POST':
        #Create the form with request.POST
        form = FileShareForm(request.POST, user=request.user)

        if form.is_valid():
            # Retrieve the cleaned data from the form
            to_user_id = form.cleaned_data['to_user']
            uploadedfile_id = form.cleaned_data['shared']

            try:
                to_user = User.objects.get(pk=to_user_id.id)
                uploadedfile = UploadedFile.objects.get(pk=uploadedfile_id.id, owner=request.user)

                # shared file object
                sharedfile = SharedFile(from_user=request.user, to_user=to_user, shared=uploadedfile)
                sharedfile.save()

                messages.success(request, 'File shared successfully')
                return redirect('home')

            except User.DoesNotExist:
                messages.error(request, 'User does not exist')
            except UploadedFile.DoesNotExist:
                messages.error(request, 'File does not exist')

    else:
        form = FileShareForm(user=request.user)

    # form to get the list of users except the current user
    users = User.objects.exclude(id=request.user.id)

    return render(request, 'share_file.html', {'form': form, 'users': users})


@login_required
def download_file(request, file_id):
    try:
        uploaded_file = UploadedFile.objects.get(pk=file_id, owner=request.user)

        # Check if the user has permission to download the file
        if request.user != uploaded_file.owner:
            raise PermissionDenied

        # Decrypt
        cipher_suite = Fernet(uploaded_file.file_key)

        # Read the content of the file
        file_content = uploaded_file.file.read()

        # Decrypt the content
        decrypted_file = cipher_suite.decrypt(file_content)

        # Provide the file for download
        response = HttpResponse(decrypted_file, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{uploaded_file.file_name}"'
        return response
    except UploadedFile.DoesNotExist:
        messages.error(request, 'File does not exist')
        return redirect('home')
    except PermissionDenied:
        messages.error(request, 'Permission Denied. You do not have access to this file.')
        return redirect('home')

def download_shared_file(request, shared_file_id):
    try:
        shared_file = SharedFile.objects.get(pk=shared_file_id, to_user=request.user)

        # Check if the user has permission to download the shared file
        if request.user != shared_file.to_user:
            raise PermissionDenied

        # Decrypt the shared file content
        cipher_suite = Fernet(shared_file.shared.file_key)
        file_content = shared_file.shared.file.read()
        decrypted_file = cipher_suite.decrypt(file_content)

        # Provide the file for download
        response = HttpResponse(decrypted_file, content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{shared_file.shared.file_name}"'
        return response
    except SharedFile.DoesNotExist:
        messages.error(request, 'Shared file does not exist')
        return redirect('home')
    except PermissionDenied:
        messages.error(request, 'Permission Denied. You do not have access to this shared file.')
        return redirect('home')



def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Log in the user after successful signup
            return redirect('home')  # Redirect to the home page or any other desired page
    else:
        form = UserCreationForm()

    return render(request, 'signup.html', {'form': form})

@login_required
def delete_file(request, file_id):
    file_instance = get_object_or_404(UploadedFile, pk=file_id, owner=request.user)

    # Check if the user has permission to delete the file
    if request.user != file_instance.owner:
        return JsonResponse({'error': 'Permission Denied'}, status=403)

    # Delete the file
    file_instance.delete_file()

    return redirect('home')

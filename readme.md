# Secure File Sharing App

# Models.py
- UserProfile:
    extends the User model provided by Django's authentication framework. Has a field user that has a one-to-one relationship with the django user class.
- UploadedFile:
    represents a file uploaded by a user.
    Contains a foreign key to the user model used to store the name of the owner of the file. Has a FileField attribute that stores the file itself. It also stores the AES encryption key used to encrypt the file. Also stores file name and file size as well as the upload date.(not really displayed on the front end). Has a redundant attribute called auth_tag. Since we were initially using AES-GCM, we needed to store the authentication tag. We later switched to AES-Fernet, but we kept the attribute just not to break the code. Contains delete file function that is linked with our remove_file view. It deletes the file from the database and from the file system.
- SharedFile:
    represents a file shared by one user to another. Contains a FK to sender, reciever (User class) and shared (Uploaded file class) and a timestamp(not really displayed on the front end). Decided to leave the control to delete the file to the sender. The receiver can only see the file and download it. The sender can delete the file from the database and from the file system.
- hashTable:
    represents a hash table for file integrity (not actively used, the values are still stored in the database)
    has a fk to uploaded file , a hash value 256sha hash and a timestamp for creation of the hash. The hash is created when the file is uploaded and stored in the database. The hash is used to check the integrity of the file when it is downloaded. The hash is created using the file name, file size and the AES key used to encrypt the file the hashlib library.


# Views.py
Dependencies:
- django - for the web framework. (version 4.2.5)
- cryptography - for encryption and decryption. Fernet module is used
- hashlib - for hashing. sha256 is used

Views:
- home(request):
    Renders the home page with user profile, uploaded files, and shared files. locked behind login authentication decorator provided by django. Fetches the user profile, uploaded files and shared files from the database and passes them to the template. If user doesnt have a profile, it makes a userprofile object and sets files to none. Since we have a signup page, we should probaly redirect to the signup page but this was a later addition. Could be simplified in a future release.
- upload_file(request):
    Handles file upload and encryption. Gets the form request ie. POST method. Checks if the form is valid. Cleans the form using the cleaned_data attribute of form and stores the owner name, file name and file size. Generates a random 32 byte key using the Fernet.generate_key() function. Encrypts the file using the key and stores it in the file system. Stores the key in the database. Creates a hash of the file using the hashlib library and stores it in the database. Creates an UploadedFile object and stores it in the database. Redirects to the home page. Has error messages for failed form submission. If a GET request is accidentaly sent, it creates an empty form object.
- share_file(request):
    Handles file sharing with other users. Similiar to upload file. with appropriate changes. Gets the form request ie. POST method. Checks if the form is valid. Cleans the form using the cleaned_data attribute of form and stores the sender name, receiver name and file name. Gets the file object from the database. Creates a SharedFile object and stores it in the database. Redirects to the home page. Has error messages for failed form submission.
- download_file(request, file_id):
    Handles file download and decryption for files uploaded by the user. Checks for access perms. decyphers the contents of the file and provides a download link as an HTTP response.
- download_shared_file(request, shared_file_id):
    Handles file download and decryption for files shared with the user. Checks for access perms. decyphers the contents of the file and provides a download link as an HTTP response. Had to create because both objects are different. Could be simplified in a future release.
- signup_view(request):
    Handles user signup. Uses djangos user creation form which has all the required security features.
- delete_file(request, file_id):
    Handles file deletion for files uploaded by the user. Uses the uploaded file models delete function to delete the file from the database and the file system. Redirects to the home page.

# urls.py
- home:
    url for home page. Connects to the home view.
- upload_file:
    url for upload file page. Connects to the upload_file view.
- share_file:
    url for share file page. Connects to the share_file view.
- download_file:
    connects to the download file view. Takes a file id as an argument.
- download_shared_file:
    connects to the download shared file view. Takes a shared file id as an argument.
- signup_view:
    url for signup page. Connects to the signup_view view.
- delete_file:
    connects to the delete file view. Takes a file id as an argument.
- login:
    url for login page. Uses djangos auth_views.login view.
- logout:
    url for logout page. Uses djangos auth_views.logout view.

# forms.py - read the docstring in the file for information on the forms

# templates:
- base.html:
    base template for all the other templates. Contains the navbar and the footer.
- home.html:
    template for the home page. Displays the user profile, uploaded files and shared files. has a download button(linked to the view through form) and a remove button(linked to the view through form) for each file.
- upload_file.html:
    template for the upload file page. Contains the upload file form, and upload file button.
- share_file.html:
    template for the share file page. Contains the share file form.
- signup.html:
    template for the signup page. Contains the signup form with instructions.
- login.html:
    template for the login page. Contains the login form with instructions. Uses django's default auth page.
- logout.html:
    template for the logout page. Contains the logout button.

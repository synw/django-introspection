# Django Introspection

Introspection tools for Django

## Install

`pip install django-introspection`

## Usage

   ```python
   from introspection.inspector import inspect
   
   # get a list of apps objects:
   apps = inspect.apps()
   # get a list of models objects:
   models, err = inspect.models("auth")
   
   # get info about an app:
   app_info, err = inspect.app("auth")
   
   # get info about a model:
   model_info, err = inspect.model("auth", "User")
   
   # go style error handling
   if err != None:
       print("ERROR:", err)
   ```

## Management command

Print details about a model or app

   ```python
   # inspect an app
   python3 manage.py inspect auth
   # or for a model
   python3 manage.py inspect auth.User
   ```
   
Output:

   ```bash
   Found 13 fields: 
   id AutoField 
   password CharField 
   last_login DateTimeField 
   is_superuser BooleanField 
   username CharField 
   first_name CharField 
   last_name CharField 
   email CharField 
   is_staff BooleanField 
   is_active BooleanField 
   date_joined DateTimeField 
   groups ManyToManyField with related name user 
   user_permissions ManyToManyField with related name user 
   Found 5 external relations : 
   admin.LogEntry.user from auth.User.id ManyToOneRel  
   account.EmailAddress.user from auth.User.id ManyToOneRel  
   socialaccount.SocialAccount.user from auth.User.id ManyToOneRel  
   reversion.Revision.user from auth.User.id ManyToOneRel  
   alapage.Page.users_only from auth.User.id ManyToManyRel  
   Found 11 instances of User
   ```
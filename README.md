# Django Introspection

Introspection tools for Django

## Install

Clone and add `"introspection",` to installed apps

## Usage

   ```python
   from introspection.inspector import inspect
   
   # get a list of apps objects:
   apps = inspect.apps()
   # get a list of models objects:
   models, err = inspect("auth")
   
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
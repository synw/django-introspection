from django.contrib.auth.models import Permission, User
from goerr import err


class UserInspector:

    def get_user(self, username):
        user = None
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            err.new(e, self.get_user, "Can not find user " + username)
        return user

    def user_info(self, username):
        user = self.get_user(username)
        if err.exists:
            err.new(self.user_class, "Can not retrieve user, aborting")
            return None
        sup = user.is_superuser
        staff = user.is_staff
        active = user.is_active
        date_joined = user.date_joined
        return sup, staff, active, date_joined

    def user_perms(self, username):
        user_perms = []
        group_perms = []
        app_perms = []
        apps = self.app_names()
        user = self.get_user(username)
        if err.exists:
            return user_perms, group_perms, app_perms
        if user.is_superuser:
            perms = Permission.objects.all()
            for perm in perms:
                user_perms.append(perm.name)
            return user_perms, group_perms, app_perms
        # user perms
        perms = Permission.objects.filter(user=user)
        if len(perms) > 0:
            for perm in perms:
                user_perms.append(perm.name)
        # group perms
        perms = Permission.objects.filter(group__user=user)
        if len(perms) > 0:
            for perm in perms:
                group_perms.append(perm.name)
        # Modules perms
        for app in apps:
            appname = app.split(".")[-1]
            if user.has_module_perms(appname):
                app_perms.append(appname)
        return user_perms, group_perms, app_perms

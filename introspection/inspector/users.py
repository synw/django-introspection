from typing import List, Tuple
from datetime import datetime

from django.contrib.auth.models import Permission, User


class UserInspector:
    def get_user(self, username: str) -> User:
        user: User
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist as e:
            raise User.DoesNotExist(f"Can not find user {username} {e}")
        return user

    def user_info(self, username: str) -> Tuple[bool, bool, bool, datetime]:
        try:
            user = self.get_user(username)
        except Exception as e:
            raise Exception("Can not retrieve user, aborting", e)
        sup = user.is_superuser
        staff = user.is_staff
        active = user.is_active
        date_joined = user.date_joined
        return sup, staff, active, date_joined

    def user_perms(
        self,
        username: str,
        app_names: List[str],
    ) -> Tuple[List[str], List[str], List[str]]:
        user_perms: List[str] = []
        group_perms: List[str] = []
        app_perms: List[str] = []
        user = self.get_user(username)
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
        for app in app_names:
            appname = app.split(".")[-1]
            if user.has_module_perms(appname):
                app_perms.append(appname)
        return user_perms, group_perms, app_perms

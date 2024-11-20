from rest_framework.generics import GenericAPIView
from rest_framework.permissions import AllowAny

from .utils import check_perm

class GeneratePermissions(GenericAPIView):
    def generate_permissions(self, *args, **kwargs):
        if getattr(self, "action", None) and self.action in kwargs.keys():
            return kwargs[self.action]
        if self.request.method and str(self.request.method).lower() in kwargs.keys():
            return kwargs[str(self.request.method).lower()]
        queryset = self.get_queryset()
        codename = queryset.model.name.lower()
        app_name = getattr(queryset.model, "_meta").app_label
        if self.request.method == "POST":
            prefix = "add"
        elif self.request.method == "DELETE":
            prefix = "delete"
        elif self.request.method in ["PUT", "PATCH"]:
            prefix = "change"
        elif self.request.method == "GET":
            prefix = "view"
        else:
            prefix = None
        if not prefix:
            return None
        perm = f"{app_name}.{prefix}_{codename}"
        return perm

def get_permissions(self, *args, kwargs):
    if len(self.permission_classes) == 1 and AllowAny not in self.permission_classes:
        return [permission() for permission in self.permission_classes]
    perm = self.generate_permissions(*args, kwargs)
    if not perm:
        return self.permission_classes
    permission_classes = [check_perm(perm)]
    return [permission() for permission in permission_classes]


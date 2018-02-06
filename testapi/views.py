from django.conf import settings
from django.http import HttpResponseNotFound
from rest_framework.generics import RetrieveAPIView, get_object_or_404
from rest_framework.response import Response

from config.signature import SignatureCheckPermission
from sso.user import models


class UserByEmailAPIView(RetrieveAPIView):
    permission_classes = [SignatureCheckPermission]
    authentication_classes = []
    queryset = models.User.objects.all()
    lookup_field = 'email'
    http_method_names = ("get", )

    def dispatch(self, *args, **kwargs):
        if not settings.TEST_API_ENABLE:
            return HttpResponseNotFound()
        return super().dispatch(*args, **kwargs)

    def get(self, request, email, **kwargs):
        user = get_object_or_404(models.User, email=email)
        response_data = {
            "sso_id": user.id,
            "is_verified": user.is_active
        }
        return Response(response_data)

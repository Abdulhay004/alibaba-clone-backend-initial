from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from django.contrib.auth.decorators import user_passes_test
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# schema_view = get_schema_view(
#        openapi.Info(
#            title="My API",
#            default_version='v1',
#            description="Test description",
#            terms_of_service="https://www.google.com/policies/terms/",
#            contact=openapi.Contact(email="contact@myapi.local"),
#            license=openapi.License(name="BSD License"),
#        ),
#        public=True,
#        permission_classes=(permissions.AllowAny,),
#    )




def is_superuser(user):
    # return user.is_superuser    # faqat superuserlar ko'ra oladi
    return user.is_authenticated
    # return True qilinsa istalgan user kira oladi

# urllarninig classlarini to'g'irlab chiqing schema, swagger, redoc

urlpatterns = [
    path("admin/", admin.site.urls),
    path('', lambda _: JsonResponse({'detail': 'Healthy'}), name='health'),
    path('api/', include(
        [
            path('users/', include('user.urls')),
            # another apps
            path('schema/', SpectacularAPIView.as_view(), name='schema'),
            path('swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
            path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
            ]))
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
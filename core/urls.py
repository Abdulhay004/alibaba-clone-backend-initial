from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def index(request):
    my_dictionary = {"a": 1, "b": 2}
    return JsonResponse(my_dictionary)

def index2(request):
    my_array = [("a", 1), ("b", 2)]
    return JsonResponse(my_array, safe=False)


from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from django.contrib.auth.decorators import user_passes_test

def is_superuser(user):
    return True

urlpatterns = [
    path("admin/", admin.site.urls),

    path('', lambda _: JsonResponse({'detail': 'Healthy'}), name='health'),
    path('api/', include(
        [   # local apps
            path('users/', include('user.urls')),
            path('products/', include('product.urls')),
            path('cart/', include('cart.urls')),
            path('orders/', include('order.urls')),
            path('payment/', include('payment.urls')),
            path('notifications/', include('notification.urls')),
            path('coupons/', include('coupon.urls')),
            path('wishlist/', include('wishlist.urls')),
            # another apps
            path('schema/', user_passes_test(is_superuser)(SpectacularAPIView.as_view()), name='schema'),
            path('swagger/', user_passes_test(is_superuser)(SpectacularSwaggerView.as_view()), name='swagger-ui'),
            path('redoc/', user_passes_test(is_superuser)(SpectacularRedocView.as_view()), name='redoc'),
            ]))

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
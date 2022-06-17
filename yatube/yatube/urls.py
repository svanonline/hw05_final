from django.contrib import admin
from django.urls import include, path

from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler404, handler403, handler500

handler404 = 'core.views.page_not_found'
handler403 = "posts.views.server_error"
handler500 = "posts.views.server_error"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls', namespace='users')),
    path('about/', include('about.urls', namespace='about')),
    path('auth/', include('django.contrib.auth.urls')),
    path('', include('posts.urls', namespace='posts')),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
    import debug_toolbar

    urlpatterns += (path('__debug__/', include(debug_toolbar.urls)),)

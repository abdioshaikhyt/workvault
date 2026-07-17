from django.urls import path
from .views import JobSearchAPIView, LogoutAndStoreTokenView

# Defines the urls
urlpatterns = [
    path('search/jobs/', JobSearchAPIView.as_view(), name='job_search'),
    path('logout/', LogoutAndStoreTokenView.as_view(), name='logout_and_store'),
]

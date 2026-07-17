from django.urls import path
from . import views
from .views import LogoutAndStoreTokenView, CoursesAPIView

urlpatterns = [
    path('logout/', LogoutAndStoreTokenView.as_view(), name='logout_and_store_token'),
    path('courses/', CoursesAPIView.as_view(), name='courses'),
]

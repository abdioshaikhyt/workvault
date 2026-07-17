from django.urls import path
from . import views

urlpatterns = [
    path('jobs/create/', views.JobCreateView.as_view(), name='job-create'),
    path("jobs/<int:pk>/advance/", views.JobAdvanceStageAPI.as_view(), name="job-advance"),
    path('clients/create/', views.ClientCreateView.as_view(), name='client-create'),
    path('clients/droplist/', views.ClientListAPI.as_view(), name='client-list'),
    path('staff/list/', views.StaffListAPI.as_view(), name='staff-list'),
    path('jobs/choices/', views.JobChoicesAPI.as_view(), name='job-choices'),
    path('jobs/<int:pk>/', views.JobDetailAPI.as_view(), name='job-detail'),
    path('job_list/', views.JobListView.as_view(), name='job-list'),
    path('clients/list/', views.ClientListView.as_view(), name='client-list'),
    path('logout/', views.LogoutAndStoreTokenView.as_view(), name='logout_and_store_token'),
]
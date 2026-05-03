# ingestion/urls.py
from django.urls import path
from .views import UploadStoresView, UploadUsersView, UploadMappingView

urlpatterns = [
    path('upload/stores/',  UploadStoresView.as_view()),
    path('upload/users/',   UploadUsersView.as_view()),
    path('upload/mapping/', UploadMappingView.as_view()),
]
from django.urls import path
from .views import CompanyInfoView

urlpatterns = [
    path("", CompanyInfoView.as_view(), name="company-info"),
]

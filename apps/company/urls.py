from django.urls import path
from .views import CompanyInfoView, FooterNavigationListView

urlpatterns = [
    path("", CompanyInfoView.as_view(), name="company-info"),
    path("footer/", FooterNavigationListView.as_view(), name="footer-nav"),
]

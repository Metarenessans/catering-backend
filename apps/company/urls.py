from django.urls import path
from .views import (
    CompanyInfoView,
    FooterNavigationListView,
    LegalDocumentListView,
    LegalDocumentDetailView,
    PrivacyPolicyView,
)

urlpatterns = [
    path("", CompanyInfoView.as_view(), name="company-info"),
    path("footer/", FooterNavigationListView.as_view(), name="footer-nav"),
    path("documents/", LegalDocumentListView.as_view(), name="legal-documents"),
    path("documents/<slug:slug>/", LegalDocumentDetailView.as_view(), name="legal-document-detail"),
    path("privacy-policy/", PrivacyPolicyView.as_view(), name="privacy-policy"),
]



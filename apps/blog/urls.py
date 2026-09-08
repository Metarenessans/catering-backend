from django.urls import path
from .views import BlogArticleListAPIView, BlogArticleDetailAPIView

app_name = "blog"

urlpatterns = [
    path("articles/", BlogArticleListAPIView.as_view(), name="article-list"),
    path("articles/<slug:slug>/", BlogArticleDetailAPIView.as_view(), name="article-detail"),
]

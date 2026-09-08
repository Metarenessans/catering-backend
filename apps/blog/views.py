from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema

from .models import BlogArticle
from .serializers import BlogArticleSerializer, SimpleBlogArticleSerializer


class BlogArticleListAPIView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        summary="Список статей блога",
        responses=SimpleBlogArticleSerializer(many=True),
    )
    def get(self, request):
        articles = BlogArticle.objects.filter(is_published=True).order_by(
            "-created_date", "-created_at"
        )
        serializer = SimpleBlogArticleSerializer(
            articles, many=True, context={"request": request}
        )
        return Response(serializer.data)


class BlogArticleDetailAPIView(APIView):
    permission_classes = (AllowAny,)

    @extend_schema(
        summary="Детальная страница статьи блога",
        responses=BlogArticleSerializer,
    )
    def get(self, request, slug):
        article = get_object_or_404(
            BlogArticle.objects.prefetch_related(
                "blocks",
                "article_products__product",
                "related_articles_association__related_article",
            ),
            slug=slug,
            is_published=True,
        )
        serializer = BlogArticleSerializer(article, context={"request": request})
        return Response(serializer.data)

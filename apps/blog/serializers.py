from rest_framework import serializers
from .models import BlogArticle, BlogArticleBlock
from apps.catalog.serializers import ProductSerializer


class BlogArticleBlockSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogArticleBlock
        fields = (
            "id",
            "image",
            "image_height_unlimited",
            "image_alt",
            "image_source_link",
            "text",
            "order",
        )


class SimpleBlogArticleSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="slug", read_only=True)

    class Meta:
        model = BlogArticle
        fields = (
            "id",
            "slug",
            "title",
            "cover",
            "is_cover_like_block_image",
            "cover_alt",
            "cover_source_link",
            "created_date",
            "created_at",
            "seo_title",
            "seo_description",
        )


class BlogArticleSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source="slug", read_only=True)
    blocks = BlogArticleBlockSerializer(many=True, read_only=True)
    products = serializers.SerializerMethodField()
    related_articles = serializers.SerializerMethodField()

    class Meta:
        model = BlogArticle
        fields = (
            "id",
            "slug",
            "title",
            "cover",
            "is_cover_like_block_image",
            "cover_alt",
            "cover_source_link",
            "created_date",
            "blocks",
            "created_at",
            "updated_at",
            "seo_title",
            "seo_description",
            "products",
            "related_articles",
        )

    def get_products(self, obj):
        article_products = (
            obj.article_products.select_related("product")
            .filter(product__is_active=True)
            .order_by("order")
        )
        products = [ap.product for ap in article_products]
        return ProductSerializer(products, many=True, context=self.context).data

    def get_related_articles(self, obj):
        related_articles_assoc = (
            obj.related_articles_association.select_related("related_article")
            .filter(related_article__is_published=True)
            .order_by("order")
        )
        articles = [ra.related_article for ra in related_articles_assoc]
        return SimpleBlogArticleSerializer(articles, many=True, context=self.context).data

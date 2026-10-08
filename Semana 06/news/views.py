from django.shortcuts import get_object_or_404, render

from .models import Article, Category


def home(request):
    articles = Article.objects.filter(is_published=True).select_related("author")
    return render(request, "news/home.html", {"articles": articles})


def article_detail(request, slug):
    article = get_object_or_404(
        Article.objects.select_related("author").prefetch_related("categories"),
        slug=slug,
        is_published=True,
    )
    return render(request, "news/article_detail.html", {"article": article})


def category_list(request, slug):
    category = get_object_or_404(Category, slug=slug)
    articles = category.articles.filter(is_published=True).select_related("author")
    return render(
        request,
        "news/category_list.html",
        {"category": category, "articles": articles},
    )

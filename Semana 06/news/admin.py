from django.contrib import admin

from .models import Article, Author, Category, SiteSetting


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ("site_name", "tagline", "announcement")
    fieldsets = (
        ("Portal", {"fields": ("site_name", "tagline")}),
        ("Banner", {"fields": ("announcement",)}),
    )


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "articles_count")
    search_fields = ("name", "description")
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="Articles")
    def articles_count(self, obj):
        return obj.articles.count()


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "website")
    search_fields = ("user__first_name", "user__last_name", "user__username", "bio")
    list_filter = ("user__is_staff",)


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "published_at", "is_published", "category_list")
    list_filter = ("is_published", "categories", "published_at")
    search_fields = ("title", "summary", "body", "author__user__first_name")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_at"
    filter_horizontal = ("categories",)
    ordering = ("-published_at",)

    @admin.display(description="Categories")
    def category_list(self, obj):
        return ", ".join(category.name for category in obj.categories.all())

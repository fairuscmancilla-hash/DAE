from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from .models import Article, Author, Category, SiteSetting


def create_article(title, category, days_ago=0, body="Body text.", **kwargs):
    author, _ = Author.objects.get_or_create(
        user=User.objects.create_user(username=f"user-{slugify(title)}"),
    )
    article = Article.objects.create(
        title=title,
        summary=f"Resumen de {title}",
        body=body,
        published_at=timezone.now() - timedelta(days=days_ago),
        author=author,
        **kwargs,
    )
    article.categories.add(category)
    return article


class TemplateEngineTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Tecnología")
        self.article = create_article("Noticia de prueba", self.category, days_ago=2)

    def test_home_extends_the_base_template(self):
        response = self.client.get(reverse("news:home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "news/home.html")
        self.assertTemplateUsed(response, "base.html")
        self.assertContains(response, 'class="site-header"')
        self.assertContains(response, 'class="card article-card"')

    def test_empty_block_when_there_are_no_articles(self):
        Article.objects.all().delete()
        response = self.client.get(reverse("news:home"))
        self.assertContains(response, "Todavía no hay noticias publicadas")

    def test_variables_control_tags_and_filters(self):
        response = self.client.get(reverse("news:home"))
        expected_date = timezone.localtime(self.article.published_at).strftime("%d/%m/%Y")
        self.assertContains(response, "Noticia de prueba")
        self.assertContains(response, "Resumen de")
        self.assertContains(response, expected_date)

    def test_card_fragment_is_reused_on_the_category_page(self):
        response = self.client.get(reverse("news:category_list", args=[self.category.slug]))
        self.assertTemplateUsed(response, "news/category_list.html")
        self.assertContains(response, 'class="card article-card"')
        self.assertContains(response, "Noticia de prueba")

    def test_detail_page_shows_author_and_categories(self):
        response = self.client.get(reverse("news:article_detail", args=[self.article.slug]))
        self.assertTemplateUsed(response, "news/article_detail.html")
        self.assertContains(response, self.article.author.full_name)
        self.assertContains(response, "Tecnología")

    def test_html_in_the_body_is_escaped(self):
        article = create_article(
            "Noticia con HTML",
            self.category,
            body='Texto con <b>etiqueta HTML</b> y <script>alert(1)</script>.',
        )
        response = self.client.get(reverse("news:article_detail", args=[article.slug]))
        self.assertContains(response, "&lt;b&gt;etiqueta HTML&lt;/b&gt;")
        self.assertNotContains(response, "<b>etiqueta HTML</b>")

    def test_urls_are_linked_with_the_url_tag(self):
        response = self.client.get(reverse("news:home"))
        self.assertContains(response, f'href="{self.article.get_absolute_url()}"')
        self.assertContains(response, f'href="{self.category.get_absolute_url()}"')


class AdminPublishingTests(TestCase):
    def setUp(self):
        User.objects.create_superuser(username="admin", password="secret")
        SiteSetting.current()
        self.category = Category.objects.create(name="Deportes")
        self.article = create_article("Goles de la jornada", self.category)

    def test_article_is_listed_with_the_custom_admin_options(self):
        self.client.login(username="admin", password="secret")
        response = self.client.get(reverse("admin:news_article_changelist"))
        self.assertContains(response, "Goles de la jornada")
        self.assertContains(response, "Categories")

    def test_site_content_changes_reach_the_site_without_showing_announcement(self):
        self.client.login(username="admin", password="secret")
        response = self.client.post(
            reverse("admin:news_sitesetting_change", args=[1]),
            {
                "site_name": "Portal Editado",
                "tagline": "Bajada cambiada desde el panel",
                "announcement": "Aviso publicado desde el administrador",
                "_save": "Save",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.client.logout()

        html = self.client.get(reverse("news:home")).content.decode()
        self.assertIn("Portal Editado", html)
        self.assertNotIn("Aviso publicado desde el administrador", html)

    def test_unpublished_articles_are_hidden_from_the_site(self):
        create_article("Borrador oculto", self.category, is_published=False)
        response = self.client.get(reverse("news:home"))
        self.assertNotContains(response, "Borrador oculto")
        self.assertEqual(SiteSetting.current().pk, 1)

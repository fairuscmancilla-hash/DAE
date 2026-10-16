"""YOUR answers. One function per question, no arguments.

Write the ORM query that answers each question and return it (a QuerySet or a
list). Do not write SQL and do not filter in Python what the database can
filter. Check yourself with:

    python manage.py duel                 # all of them
    python manage.py duel --question q4   # just one

Question 5 asks for two numbers per post: annotate them as `n_comments` and
`n_tags`.
"""
from datetime import date  # noqa: F401  (you will need it in question 3)

from django.db.models import Count, Q  # noqa: F401

from blog.models import Author, Category, Comment, Post, Profile, Tag  # noqa: F401


def q1():
    """Los artículos que ya están publicados."""
    # `published` is a BooleanField: filter with the exact value True.
    # The WHERE clause becomes: WHERE "blog_post"."published" = True
    return Post.objects.filter(published=True)


def q2():
    """Los artículos que no tienen categoría asignada."""
    # `category` is a nullable ForeignKey. In the ORM, "empty" is not a
    # comparison with `=`: it is the dedicated `__isnull` lookup, which the
    # database renders as IS NULL. (Filtering in Python would be an extra
    # query plus a loop.)
    return Post.objects.filter(category__isnull=True)


def q3():
    """Los artículos publicados entre el 1 de marzo y el 31 de mayo de 2026, ambos días incluidos."""
    # The question says "ambos días incluidos", so the bounds are INCLUSIVE:
    # `__gte` / `__lte` (>=, <=), not `__gt` / `__lt` (>, <).
    # Two posts sit exactly on 2026-03-01 and 2026-05-31 on purpose.
    # (The AI used the strict lookups and lost exactly those two.)
    # Drafts have published_at = NULL, and NULL never satisfies a range
    # comparison, so they are excluded automatically.
    return Post.objects.filter(
        published_at__gte=date(2026, 3, 1),
        published_at__lte=date(2026, 5, 31),
    )


def q4():
    """Los artículos con más de dos comentarios."""
    # Comments point at the post (FK on Comment), so the count must be
    # computed BY THE DATABASE: `annotate` adds an aggregate to each row.
    # Then filter ON THE ANNOTATION with `__gt` (greater than).
    # One single query; the AI's version (loop + .count() per post) costs 16.
    return Post.objects.annotate(n_comments=Count("comments")).filter(n_comments__gt=2)


def q5():
    """Los tres artículos publicados con más comentarios; de cada uno, cuántos comentarios
    (`n_comments`) y cuántas etiquetas (`n_tags`)."""
    # Both counts over two different multi-valued relations in ONE query.
    # Crossing two one-to-many joins multiplies the rows (6 comments x 3 tags
    # = 18 in the AI's answer): `distinct=True` counts each comment/tag once.
    # Both annotations must live in the SAME annotate() call so the whole
    # answer costs one query, then order by the annotation and slice.
    return (
        Post.objects.filter(published=True)
        .annotate(
            n_comments=Count("comments", distinct=True),
            n_tags=Count("tags", distinct=True),
        )
        .order_by("-n_comments")[:3]
    )


def q6():
    """Los artículos escritos por autores de Perú (publicados o no)."""
    # The country is NOT on Author; it lives on Profile (one-to-one,
    # related_name="profile"). Walk the relations with `__`:
    # author -> profile -> country. (The AI invented `author__country`.)
    return Post.objects.filter(author__profile__country="Perú")


def q7():
    """Los comentarios de los artículos de la categoría «Tecnología»."""
    # A Comment knows nothing about categories: walk comment -> post ->
    # category -> name. Django turns traversals into INNER JOINs, so
    # comments of posts without category are simply not returned.
    return Comment.objects.filter(post__category__name="Tecnología")


def q8():
    """Los autores que nunca han publicado un artículo."""
    # "Never published" = has NO post with published=True. Careful:
    # this is NOT the same as "has no posts at all" (`posts__isnull=True`),
    # which would drop Carla (she has drafts) and keep only Diego.
    # `exclude` with a multi-valued relation asks for the complement:
    # every author who is NOT in the set of authors of published posts.
    return Author.objects.exclude(posts__published=True)

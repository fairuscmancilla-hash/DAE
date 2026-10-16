"""Queries behind the views. Part 2 of the lab happens in this file."""
from blog.models import Post


def posts_for_front_page():
    # The template walks `post.author` and `post.tags` once per post, so a
    # plain QuerySet costs 1 query for the posts + 11 for the authors + 11 for
    # the tags (23 in total). Each relation needs its own mechanism:
    #
    #   * author  is a ForeignKey: the row already carries `author_id`, so
    #     `select_related` adds the author to the SAME query with a JOIN.
    #   * tags    is ManyToManyField: a JOIN would multiply the post rows,
    #     so `prefetch_related` fetches every tag of every post in ONE extra
    #     query and joins them in Python.
    #
    # Result: 1 query for posts+author, 1 for all the tags = 2.
    return (
        Post.objects.filter(published=True)
        .select_related("author")
        .prefetch_related("tags")
        .order_by("-published_at")
    )

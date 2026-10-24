from rest_framework.permissions import BasePermission

AGENT_GROUP = "agente"


class AgentPermission(BasePermission):
    """Who may do what. This is the SERVER's rule: it holds even if a client misbehaves.

    The rule the lab asks for:
      - a person (user with is_staff) can do anything;
      - a member of the group «agente» can read, create and modify, but NEVER delete;
      - anybody else who is logged in can only read;
      - an unknown method is denied (deny by default).

    TODO(team): implement it. As it stands, `return True` lets everything through, so the
    agent's token can delete and `python manage.py test quiz.tests.test_permissions` fails.
    """

    READ_METHODS = ("GET", "HEAD", "OPTIONS")
    WRITE_METHODS = ("POST", "PUT", "PATCH")

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        if user.is_staff:
            return True
        method = request.method.upper()
        if method in self.READ_METHODS:
            return True
        is_agent = user.groups.filter(name=AGENT_GROUP).exists()
        if is_agent and method in self.WRITE_METHODS:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)

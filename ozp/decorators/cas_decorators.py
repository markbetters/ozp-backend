from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.http import HttpRequest, HttpResponseForbidden
from django.shortcuts import resolve_url
from django.utils.decorators import available_attrs
from functools import wraps


def redirecting_login_required(view_func=None):
    """
    Decorator for views that serves as an ajax-aware, drop-in replacement
    for login_required. Unauthenticated AJAX requests are rejected as 403
    Forbidden and non-AJAX requests are redirected to a login page.
    """

    @wraps(view_func, assigned=available_attrs(view_func))
    def _wrapped_view(request: HttpRequest, *args, **kwargs):
        if request.user.is_authenticated():
            return view_func(request, *args, **kwargs)
        if request.is_ajax():
            return HttpResponseForbidden()
        path = request.build_absolute_uri()
        resolved_login_url = resolve_url(settings.LOGIN_URL)
        return redirect_to_login(path, resolved_login_url, 'renamed_next')
    return _wrapped_view



"""View for handling logout requests."""

import pyramid.httpexceptions as http_exc
from pyramid.security import forget
from pyramid.view import view_config


@view_config(route_name='logout', renderer='employees:templates/login.pt')
def logout(request):
    headers = forget(request)
    return http_exc.HTTPFound(location=request.route_url("login"),
                              headers=headers)

"""View for handling the login form.

This is also the view that is shown when the user does not have access to a
particular resource."""

import logging

import pyramid.httpexceptions as http_exc
from pyramid.security import remember
from pyramid.view import view_config, forbidden_view_config

from .. import exceptions
from ..models import DBSession
from ..models.employee import Employee

LOG = logging.getLogger(__name__)


def _target(request, emp_no, dept_no=None, **kwargs):
    if dept_no:
        # is manager of this department, go to department page
        target = request.route_url('show_dept', dept_no=dept_no)
    else:
        # non-manager
        target = request.route_url('show_empl', emp_no=emp_no)
    return http_exc.HTTPFound(location=target, **kwargs)


@view_config(route_name='login', renderer='employees:templates/login.pt')
@forbidden_view_config(renderer='employees:templates/login.pt')
def login(request):
    username = ''
    password = ''
    err_msg = ''
    auth_engine = request.registry.settings['auth_engine']

    login_url = request.route_url('login')
    coming_from = request.url
    curr_userid = request.authenticated_userid
    if curr_userid and 'submitted' not in request.params:
        LOG.debug("User:{} already authenticated".format(username))
        # Already authenticated user directly accessing login page - either a
        # redirect to jump to suitable "home" page or requesting permission to
        # view another page
        username = curr_userid
        dept_no = auth_engine.dept_managed(request.effective_principals)
        if coming_from == login_url:
            # redirect to the user's "home" page
            return _target(request, username, dept_no)
        else:
            LOG.debug("User:{} forbidden from accessing:{}".format(username, coming_from))
            # trying to access a forbidden resource - login again
            employee = Employee.get_by_number(curr_userid)
            username = '{}.{}'.format(employee.first_name, employee.last_name)
            password =  curr_userid
            err_msg = ('You do not have permission to access this page. '
                       'Please log in again with suitable credentials.')
    elif 'submitted' in request.params:
        username = request.params['login']
        password = request.params['password']
        LOG.debug("Authenticating User:{}".format(username))

        try:
            auth_engine.authenticate(username, password)
        except ValueError:
            message = "Incorrect username format:{}".format(username)
            LOG.warning(message)
            raise http_exc.HTTPBadRequest(detail=message)
        except exceptions.AuthFail as e:
            LOG.warning(e)
            err_msg = "Unknown username/password combination."
        else:
            first_name, last_name = username.split('.')
            employee = DBSession.query(Employee).\
                           filter(Employee.first_name == first_name).\
                           filter(Employee.last_name == last_name).\
                           first()
            curr_mgd_dept = employee.curr_managed_dept
            headers = remember(request, str(employee.emp_no))
            dept_no = curr_mgd_dept.dept_no if curr_mgd_dept else None
            if coming_from == login_url:
                return _target(request, employee.emp_no,
                               curr_mgd_dept.dept_no if curr_mgd_dept else None,
                               headers=headers)
            else:
                return http_exc.HTTPFound(location=coming_from, headers=headers)

    return {'url': request.url, 'login': username, 'password': password,
            'err_msg': err_msg}

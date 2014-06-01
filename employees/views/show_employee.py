"""View for handling display of employee details."""

import logging

import pyramid.httpexceptions as http_exc
from pyramid.view import view_config

from ..models.employee import Employee


LOG = logging.getLogger(__name__)


@view_config(route_name='show_empl', renderer='employees:templates/employee.pt',
             permission='view')
def show_empl(request):
    auth_engine = request.registry.settings['auth_engine']
    mgr_context = bool([p for p in request.effective_principals
                            if p.startswith(auth_engine.dept_mgr_pfx)])
    emp_no = int(request.matchdict['emp_no'])
    employee = Employee.get_by_number(emp_no)
    LOG.debug("Displaying employee:{}".format(str(employee)))
    if not employee:
        LOG.debug("employee:{} not found".format(str(employee)))
        raise http_exc.HTTPNotFound
    curr_dept = employee.curr_dept
    manage = employee.curr_dept.dept_no if mgr_context else ''

    return {'emp': employee, 'manage': manage}

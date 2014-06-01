"""View for handling display and search of department employee list."""

import logging

import pyramid.httpexceptions as http_exc
from pyramid.view import view_config

from ..models import DBSession
from ..models.department import Department


LOG = logging.getLogger(__name__)


def _get_next_prev(request, obj_list, limit, curr_offset, other_offset,
                   offset_val, extra_query_vars=[]):
    """Compute the next/prev links (if any)."""
    query_vars = [(other_offset, 0)]
    query_vars.extend(extra_query_vars)
    if len(obj_list) > limit:
        query_vars.append((curr_offset, offset_val + limit))
        next_pg = request.current_route_url(_query=query_vars)
    else:
        next_pg = None

    if offset_val != 0:
        query_vars.append((curr_offset, offset_val - limit))
        prev_pg = request.current_route_url(_query=query_vars)
    else:
        prev_pg = None

    return (prev_pg, next_pg)


def _search(request, dept, limit, offset):
    """Search based on the criteria provided by the user.
    
    ATM we support only a simple AND of the fields. A more complete query
    language can be built on top later if required."""
    LOG.debug("Searching department:{}".format(str(dept)))
    parser = request.registry.settings['query_parser']
    query_tups = [(k,request.params[k]) for k in parser.valid_fields
                     if k in request.params and request.params[k]]
    query_d = dict(query_tups)
    LOG.debug("Query fields:{}".format(query_d))
    db_query = None
    if parser.parse(**query_d):
        db_query = parser.search(DBSession, dept.dept_no)
    if not db_query:
        # Nothing to search for - go to list instead
        LOG.debug("Nothing to search for - jumping to 'show_dept'")
        target = request.route_url('show_dept', dept_no=dept.dept_no)
        return http_exc.HTTPFound(location=target)

    # read one more than the limit to see if this is the last page
    curr_emps = db_query.offset(offset).limit(limit+1).all()
    query_vars = query_tups + [('search', 'Search')]
    prev_pg, next_pg = _get_next_prev(request, curr_emps, limit,
                                      curr_offset='s_offset',
                                      other_offset='l_offset',
                                      offset_val=offset,
                                      extra_query_vars=query_vars)
    if next_pg:
        # we fetched one extra record for checking for last page
        curr_emps = curr_emps[:-1]

    return {'dept': dept,
            'next_pg': next_pg,
            'prev_pg': prev_pg,
            'query': query_d,
            'emp_list': curr_emps,
            'curr_user_id': request.authenticated_userid}


def _list(request, dept, limit, offset):
    """List current employees of a deparment."""
    LOG.debug("Listing department:{}".format(str(dept)))

    # read one more than the limit to see if this is the last page
    emp_refs = dept.curr_employee_refs.offset(offset).limit(limit+1).all()
    prev_pg, next_pg = _get_next_prev(request, emp_refs, limit,
                                      curr_offset='l_offset',
                                      other_offset='s_offset',
                                      offset_val=offset)
    if next_pg:
        curr_emps = [ref.employee for ref in emp_refs[:-1]]
    else:
        curr_emps = [ref.employee for ref in emp_refs]

    return {'dept': dept,
            'next_pg': next_pg,
            'prev_pg': prev_pg,
            'query': {},
            'emp_list': curr_emps,
            'curr_user_id': request.authenticated_userid}


@view_config(route_name='show_dept', renderer='employees:templates/department.pt',
             permission='view')
def show_dept(request):
    dept_no = request.matchdict['dept_no']
    limit = int(request.registry.settings.get('page_size', 10))
    dept = Department.get_by_number(dept_no)
    if not dept:
        raise http_exc.HTTPNotFound

    if (request.params.get("clear", None) or
        request.params.get('search', None) is None):
        offset = int(request.params.get("l_offset", 0))
        return _list(request, dept, limit, offset)
    else:
        offset = int(request.params.get("s_offset", 0))
        return _search(request, dept, limit, offset)

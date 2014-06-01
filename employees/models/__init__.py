"""The application domain model.

Table definitions have been copied from the original MySQL employees_db package."""

import logging

from pyramid.security import Allow, Deny, Everyone
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from zope.sqlalchemy import ZopeTransactionExtension


DBSession = scoped_session(sessionmaker(extension=ZopeTransactionExtension()))
Base = declarative_base()
LOG = logging.getLogger(__name__)


# root factories for access control to employee and department resources.
class EmployeeRootFactory(object):
    """A "resource factory" to generate the root node resource for an employee.

    Used for defining ACLs on an employee resource. The ACL allows (view)
    access only to the employee and the employee's department manager"""

    def __init__(self, request):
        # Allow only user and group manager to view an employee node
        LOG.debug("Creating root employee resource for:{}".format(request.url))
        auth_engine = request.registry.settings['auth_engine']
        emp_no = request.matchdict['emp_no']
        self.__acl__ = [(Allow, auth_engine.emp_p(emp_no), 'view'),
                        (Allow, auth_engine.emp_mgr_p(emp_no), 'view'),
                        (Deny, Everyone, 'view')]
        LOG.debug("{}: set acls to:{}".format(request.url, self.__acl__))


class DeptRootFactory(object):
    """Resource factory to generate the root node resource for department
       employee list.

    Used for defining ACLs on a department employee list. A department employee
    list is viewable only by a department manager"""

    def __init__(self, request):
        # Allow only group manager to view the employee list
        LOG.debug("Creating root dept resource for:{}".format(request.url))
        dept_no = request.matchdict['dept_no']

        # TODO: We should probably check if the target department exists, but
        # that would mean a DB lookup and then a 404 error (if it doesn't). By
        # blindly constructing the ACL below we won't get a 404 but a
        # "forbidden" error. Given that it cuts down on DB access per request I
        # think that's acceptable.
        auth_engine = request.registry.settings['auth_engine']
        self.__acl__ = [(Allow, auth_engine.dept_mgr_p(dept_no), 'view'),
                        (Deny, Everyone, 'view')]
        LOG.debug("{}: set acls to:{}".format(request.url, self.__acl__))

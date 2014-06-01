"""A simple authorization driver.

The username is of the form "FirstName.LastName" and the password should be the
employee ID of that employee."""

import logging

import exceptions
from models import DBSession
from models.employee import Employee


LOG = logging.getLogger(__name__)


class AuthEngine(object):
    dept_mgr_pfx = 'dept_mgr:'
    emp_mgr_pfx = 'emp_mgr:'
    employee_pfx = 'emp:'

    def authenticate(self, username, passwd):
        """Authenticate username/password pair.

        Raise exceptions.AuthFail if auth fails.
        Return nothing if OK."""
        LOG.debug("Authenticating:{}".format(username))
        session = DBSession
        first_name, last_name = username.split('.')

        empno_rec = session.query(Employee.emp_no).\
                        filter(Employee.first_name == first_name).\
                        filter(Employee.last_name == last_name).\
                        first()
        if not empno_rec or str(empno_rec.emp_no) != passwd:
            reason = "Unknown username/password combination"
            raise exceptions.AuthFail(login=username, reason=reason)

    def emp_mgr_p(self, emp_no):
        """Generate the principal for a manager of an employee.
        
        This principal will allow the manager access to the employee record."""
        return "{}{}".format(self.emp_mgr_pfx, emp_no)

    def dept_mgr_p(self, dept_no):
        """Generate the principal for a manager of a department.
        
        This principal will allow the manager access to the list of employees
        of the department."""
        return "{}{}".format(self.dept_mgr_pfx, dept_no)

    def emp_p(self, emp_no):
        """Generate the principal for an employee.
        
        This principal will allow an employees to access their own records."""
        return "{}{}".format(self.employee_pfx, emp_no)

    def dept_managed(self, principals):
        """Return department which current user may access.

        Convenience function."""
        mgr_p = [p for p in principals if p.startswith(self.dept_mgr_pfx)]
        return mgr_p[0][len(self.dept_mgr_pfx):] if mgr_p else None

    def get_groups(self, userid, request):
        """Return a list of principals for userid.

        If userid represents a non-manager then the list of principals returned
        is emp:<userid>

        If the user is a manager then the list of principals returned further
        includes principals of the form:
            emp_mgr:FOO.emp_no
        for each FOO employee in the dept. managed by the user AND
            dept_mgr:DEPT.dept_no
        where DEPT is the dept_no of the dept. managed by the user.

        This results in a larger number of principals but avoids having to look
        up the DB (to resolve department-manager relationships) each time a
        request to an employee or department resource is made.
        """
        LOG.debug("Getting principal info for:{}".format(userid))
        employee = Employee.get_by_number(userid)
        if employee.curr_managed_dept is not None:
            principals = [self.dept_mgr_p(employee.curr_managed_dept.dept_no)]
            curr_emps = employee.curr_managed_dept.curr_employee_refs.all()
            # curr_emps will include userid too
            principals.extend([self.emp_mgr_p(emp_ref.emp_no)
                                 for emp_ref in curr_emps])
            LOG.debug("Returning principals:{}".format(principals))
            return principals
        else:
            principals = [self.emp_p(userid)]
            LOG.debug("Returning principals:[{}]".format(principals))
            return principals

"""Model for the Department object."""

import datetime
import logging

from sqlalchemy import Column, String, CHAR
from sqlalchemy.orm import relationship, backref

from . import DBSession, Base
from .dept_employee import DeptEmployee


LOG = logging.getLogger(__name__)


# CREATE TABLE departments (
#     dept_no     CHAR(4)         NOT NULL,
#     dept_name   VARCHAR(40)     NOT NULL,
#     PRIMARY KEY (dept_no),
#     UNIQUE  KEY (dept_name)
# );
class Department(Base):
    __tablename__ = 'departments'
    dept_no = Column(CHAR(4), primary_key=True)
    dept_name = Column(String(40), nullable=False, unique=True, index=True)

    @property
    def curr_employee_refs(self):
        """List of (references to) employees currently in the dept.

        Further queries can be made against this query object."""
        today = datetime.date.today()
        emp_refs = self.employee_refs.filter(DeptEmployee.to_date >= today)
        LOG.debug("emp_refs:{}".format(map(str, emp_refs)))
        return emp_refs

    @classmethod
    def get_by_number(cls, dept_no):
        """Get a department object by the dept number.

        Convenience function."""
        return DBSession.query(cls).filter(cls.dept_no == dept_no).first()

    def __str__(self):
        return "{}({})".format(self.dept_no, self.dept_name)

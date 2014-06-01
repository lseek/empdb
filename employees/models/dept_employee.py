"""Model for the Department-Employee association."""

import logging

from sqlalchemy import Column, CHAR, Date, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref

from . import Base


LOG = logging.getLogger(__name__)

# CREATE TABLE dept_emp (
#     emp_no      INT             NOT NULL,
#     dept_no     CHAR(4)         NOT NULL,
#     from_date   DATE            NOT NULL,
#     to_date     DATE            NOT NULL,
#     KEY         (emp_no),
#     KEY         (dept_no),
#     FOREIGN KEY (emp_no)  REFERENCES employees   (emp_no)  ON DELETE CASCADE,
#     FOREIGN KEY (dept_no) REFERENCES departments (dept_no) ON DELETE CASCADE,
#     PRIMARY KEY (emp_no,dept_no)
# );
class DeptEmployee(Base):
    __tablename__ = 'dept_emp'
    emp_no = Column(Integer, ForeignKey('employees.emp_no'),
                    index=True, primary_key=True)
    dept_no = Column(CHAR(4), ForeignKey('departments.dept_no'),
                     index=True, primary_key=True)
    from_date = Column(Date, nullable=False)
    to_date = Column(Date, nullable=False)

    dept = relationship('Department',
                        backref=backref('employee_refs', lazy='dynamic'))

    def __str__(self):
        return "({}, {})".format(self.dept_no, self.emp_no)



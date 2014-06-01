"""Model definition of an Employee object."""

import datetime
import logging

from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    Enum,
    or_,
    desc,
    )
from sqlalchemy.orm import relationship, backref

from . import DBSession, Base
from dept_employee import DeptEmployee
from dept_manager import DeptManager
from salary import Salary
from title import Title
from .. import exceptions


LOG = logging.getLogger(__name__)


# CREATE TABLE employees (
#     emp_no      INT             NOT NULL,
#     birth_date  DATE            NOT NULL,
#     first_name  VARCHAR(14)     NOT NULL,
#     last_name   VARCHAR(16)     NOT NULL,
#     gender      ENUM ('M','F')  NOT NULL,
#     hire_date   DATE            NOT NULL,
#     PRIMARY KEY (emp_no)
# );
class Employee(Base):
    __tablename__ = 'employees'
    emp_no = Column(Integer, primary_key=True)
    birth_date = Column(Date)
    first_name = Column(String(14), nullable=False)
    last_name = Column(String(16), nullable=False)
    gender = Column(Enum('M','F'), nullable=False)
    hire_date = Column(Date)

    depts_managed = relationship('DeptManager', lazy='dynamic',
                                 backref='employee')
    depts_worked = relationship('DeptEmployee', lazy='dynamic',
                                 backref='employee')
    titles = relationship('Title', lazy='dynamic',
                          backref='employee')
    salaries = relationship('Salary', lazy='dynamic',
                            backref='employee')

    @property
    def curr_dept(self):
        """Department the employee is currently in"""
        today = datetime.date.today()
        dept_assocs = self.depts_worked.\
                          filter(DeptEmployee.to_date >= today).all()
        if len(dept_assocs) == 0:
            LOG.error("Employee:{} not found in any dept".format(self.emp_no))
            raise exceptions.InconsistentDB
        if len(dept_assocs) > 1:
            LOG.error("Employee:{} is in more than 1 dept".format(self.emp_no))
            raise exceptions.InconsistentDB
        return dept_assocs[0].dept

    @property
    def curr_managed_dept(self):
        """Department the employee currently manages (if any)"""
        today = datetime.date.today()
        managed_assocs = self.depts_managed.\
                             filter(DeptManager.to_date >= today).all()
        if len(managed_assocs) == 1:
            return self.depts_managed[0].dept
        else:
            LOG.debug("{} is not a manager".format(self.emp_no))
            return None

    @property
    def curr_title(self):
        """Titles currently held by the employee."""
        today = datetime.date.today()
        # to_date may be NULL for titles. Therefore a current title may
        # have a NULL to_date)
        titles = self.titles.filter(or_(Title.to_date == None,
                                        Title.to_date >= today)).\
                             order_by(desc(Title.from_date)).all()
        LOG.debug("titles for:{}:{}".format(self.emp_no, map(str, titles)))
        if len(titles) == 0:
            LOG.error("No title info found for:{}".format(self.emp_no))
            raise exceptions.InconsistentDB
        if len(titles) > 1:
            msg = ("Multiple titles found for:{}, "
                   "returning latest".format(self.emp_no))
            LOG.warning(msg)
        return titles[0]

    @property
    def curr_salary(self):
        """Current salary drawn by the employee."""
        today = datetime.date.today()
        salaries = self.salaries.filter(Salary.to_date >= today).\
                               order_by(desc(Salary.from_date)).all()
        if len(salaries) == 0:
            LOG.error("No salary info found for:{}".format(self.emp_no))
            raise exceptions.InconsistentDB
        if len(salaries) > 1:
            msg = ("Multiple salary records found for:{}, "
                   "returning latest:{}".format(self.emp_no))
            LOG.warning(msg)
        return salaries[0]

    @classmethod
    def get_by_number(cls, emp_no):
        """Get an employee object by the employee number.

        Just for convenience"""
        return DBSession.query(cls).filter(cls.emp_no == emp_no).first()

    def __str__(self):
        return "{}({} {})".format(self.emp_no, self.first_name, self.last_name)

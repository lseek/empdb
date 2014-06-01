"""Model for the Salary object."""

from sqlalchemy import Column, Date, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref

from . import Base


# CREATE TABLE salaries (
#     emp_no      INT             NOT NULL,
#     salary      INT             NOT NULL,
#     from_date   DATE            NOT NULL,
#     to_date     DATE            NOT NULL,
#     KEY         (emp_no),
#     FOREIGN KEY (emp_no) REFERENCES employees (emp_no) ON DELETE CASCADE,
#     PRIMARY KEY (emp_no, from_date)
# );
class Salary(Base):
    __tablename__ = 'salaries'
    emp_no = Column(Integer, ForeignKey('employees.emp_no'),
                    index=True, primary_key=True)
    salary = Column(Integer, nullable=False)
    from_date = Column(Date, primary_key=True, nullable=False)
    to_date = Column(Date, nullable=False)

    def __str__(self):
        return str(self.salary)

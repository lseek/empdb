"""Model for the Title object."""

from sqlalchemy import Column, Date, Integer, String, ForeignKey
from sqlalchemy.orm import relationship, backref

from . import Base


# CREATE TABLE titles (
#     emp_no      INT             NOT NULL,
#     title       VARCHAR(50)     NOT NULL,
#     from_date   DATE            NOT NULL,
#     to_date     DATE,
#     KEY         (emp_no),
#     FOREIGN KEY (emp_no) REFERENCES employees (emp_no) ON DELETE CASCADE,
#     PRIMARY KEY (emp_no,title, from_date)
# );
class Title(Base):
    __tablename__ = 'titles'
    emp_no = Column(Integer, ForeignKey('employees.emp_no'),
                    index=True, primary_key=True)
    title = Column(String(50), primary_key=True, nullable=False)
    from_date = Column(Date, primary_key=True, nullable=False)
    to_date = Column(Date)

    def __str__(self):
        return str(self.title)

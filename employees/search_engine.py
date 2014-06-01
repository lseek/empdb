"""Module for supporting searching/filtering of department employee lists.

In a logical sense this module implements:
    select <fixed_fields> from <model> where <filter_conditions>
where:
    - fixed_fields is the fixed list of fields mentioned above
    - model is automatically determined by the module
    - filter_conditions is provided by the user (and needs to be parsed by the
            query string parser).

For simplicity ATM we only support a simple AND of the fields (first_name=foo
AND department=bar). In future a more elaborate query language can be
implemented.

Note that the only fields which can be queried are:
    first_name
    last_name
    gender
    job_title
    hire_date
it is only the filter conditions that change.

If the field being filtered is a string type then we treat the value as a
substring to match against else we try to match the exact value."""

import datetime
import logging
import sqlalchemy as sqla

from models.employee import Employee
from models.dept_employee import DeptEmployee
from models.title import Title
import exceptions


LOG = logging.getLogger(__name__)


class FilterExpr(object):
    """Query string parsers must ultimately return a filter expression object."""

    def to_sqla(self):
        """Return the SQLAlchemy object corresponding to this expression.

        Subclasses must override this"""
        return None


class EqualExpr(FilterExpr):
    """Match a value exactly."""
    def __init__(self, field, val):
        self.field = field
        self.val = val

    def to_sqla(self):
        LOG.debug("converting: {} = {}".format(self.field, self.val))
        return (self.field == self.val)


class LikeExpr(FilterExpr):
    """Match a pattern (case insensitive)."""
    def __init__(self, field, pattern):
        self.field = field
        self.pattern = pattern

    def to_sqla(self):
        LOG.debug("converting: {} ILIKE {}".format(self.field, self.pattern))
        return self.field.ilike(self.pattern)


class NotExpr(FilterExpr):
    """Negate an expression."""
    sqla_operator = sqla.not_

    def __init__(self, expr):
        self.expr = expr

    def to_sqla(self):
        LOG.debug("converting: NOT({})".format(self.expr))
        return sqla.not_(self.expr.to_sqla())


class AndExpr(FilterExpr):
    def __init__(self, *exprs):
        self.exprs = exprs

    def __init__(self, *exprs):
        self.exprs = exprs

    def to_sqla(self):
        sqla_exprs = [expr_obj.to_sqla() for expr_obj in self.exprs]
        LOG.debug("converting: AND({})".format(sqla_exprs))
        return sqla.and_(*sqla_exprs)


class OrExpr(FilterExpr):
    def __init__(self, *exprs):
        self.exprs = exprs

    def __init__(self, *exprs):
        self.exprs = exprs

    def to_sqla(self):
        sqla_exprs = [expr_obj.to_sqla() for expr_obj in self.exprs]
        LOG.debug("converting: OR({})".format(sqla_exprs))
        return sqla.or_(*sqla_exprs)


class QueryParser(object):
    """Base class for parsing query strings.
    
    This class should be used in the following manner:
        1. Global config instantiates a QueryParser (sub)class instance during
           startup.
        2. Caller calls gets parser instance from request.registry.settings
        3. Caller calls instance.parse(<query args>)
        4. Caller calls instance.search(session, dept_no) where session is a DB
           session instance.
        5. Search view passes on the result to the template."""

    valid_fields = {
        "first_name": Employee.first_name,
        "last_name": Employee.last_name,
        "gender": Employee.gender,
        "hire_date": Employee.hire_date,
        "curr_title": Title.title,
    }

    def __init__(self):
        self.expr = None

    def parse(self):
        """Parse the query inputs and set 'expr' to the corresponding
        FilterExpr object.

        If the query input was parsed successfully then return True else False

        Subclasses must override this. In particular, the arguments to the
        parse method must be defined by each subclass. Subclasses should set
        the 'expr' attribute to the appropriate FilterExpr instance
        representing the parsed query"""
        return False

    def search(self, session, dept_no):
        """Perform the actual search.

        'session' is the SQLAlchemy session object.
        'dept_no' is the department number to which the search should be
        limited.

        This method returns the query object. The caller can make further
        modifications to the query (e.g. add limit and offset)

        Subclasses should not need to override this"""
        # always implicitly add dept_no and filters to select current title
        today = datetime.date.today()
        title_is_curr = sqla.or_(Title.to_date == None, Title.to_date >= today)
        return session.query(Employee.emp_no,
                             Employee.first_name,
                             Employee.last_name,
                             Employee.gender,
                             Employee.hire_date,
                             Title.title.label('curr_title')).\
                   filter(DeptEmployee.dept_no == dept_no).\
                   filter(DeptEmployee.emp_no == Employee.emp_no).\
                   filter(DeptEmployee.to_date >= today).\
                   filter(Title.emp_no == Employee.emp_no).\
                   filter(title_is_curr).\
                   filter(self.expr.to_sqla())


class FormQueryParser(QueryParser):
    """A simple query parser.

    All the fields are ANDed. If a field is of string type then a substring
    match is performed else an exact match is performed."""

    def parse(self, **kwargs):
        """Build a filter expression out of the arguments

        kwargs contains the fields to be queried (e.g. {"first_name": "foo"})."""
        if not kwargs:
            self.expr = None
            return self
        expr_list = []
        for field, value in kwargs.items():
            try:
                field_obj = self.valid_fields[field]
            except KeyError:
                raise exceptions.UnknownField(field=field)

            pat_types = (sqla.String, sqla.CHAR, sqla.VARCHAR)
            if isinstance(field_obj.type, pat_types):
                expr = LikeExpr(field_obj, '%{}%'.format(value))
            else:
                expr = EqualExpr(field_obj, value)
            expr_list.append(expr)
        self.expr = AndExpr(*expr_list) if len(expr_list) > 1 else expr_list[0]
        return self

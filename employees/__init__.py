import logging

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.config import Configurator
from sqlalchemy import engine_from_config

from auth import AuthEngine
from models import DBSession, Base, EmployeeRootFactory, DeptRootFactory
from search_engine import FormQueryParser


LOG = logging.getLogger(__name__)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    LOG.debug("settings:{}".format(settings))
    engine = engine_from_config(settings, 'sqlalchemy.')
    DBSession.configure(bind=engine)
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include('pyramid_chameleon')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('jasny-css', 'static/jasny-bootstrap/css', cache_max_age=3600)
    config.add_static_view('jasny-js', 'static/jasny-bootstrap/js', cache_max_age=3600)
    config.add_route('login', '/')
    config.add_route('logout', '/logout')
    config.add_route('show_empl', '/employee/{emp_no}',
                     factory=EmployeeRootFactory)
    config.add_route('show_dept', '/department/{dept_no}',
                     factory=DeptRootFactory)

    auth_engine = AuthEngine()
    config.add_settings(auth_engine=auth_engine)
    authn_policy = AuthTktAuthenticationPolicy(settings['secret_key'],
                                               callback=auth_engine.get_groups,
                                               hashalg='sha512')
    config.set_authentication_policy(authn_policy)
    config.set_authorization_policy(ACLAuthorizationPolicy())

    query_parser = FormQueryParser()
    config.add_settings(query_parser=query_parser)

    config.scan()

    return config.make_wsgi_app()

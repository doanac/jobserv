# Copyright (C) 2017 Linaro Limited
# Author: Andy Doan <andy.doan@linaro.org>

import datetime

from importlib import import_module

from flask import Flask, request
from flask.json import JSONEncoder
from flask_migrate import Migrate

import json_logging
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.routing import UnicodeConverter

from jobserv.settings import PROJECT_NAME_REGEX

from jobserv.jsend import jsendify
from jobserv.settings import PERMISSIONS_MODULE

permissions = import_module(PERMISSIONS_MODULE)


class ISO8601_JSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime.datetime):
            return obj.isoformat() + "+00:00"
        return super().default(obj)


class ProjectConverter(UnicodeConverter):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, *kwargs)
        if PROJECT_NAME_REGEX:
            self.regex = PROJECT_NAME_REGEX


class RequestIdMiddleware(ProxyFix):
    def __call__(self, environ, start_response) -> Flask:
        corid = json_logging.get_correlation_id()

        def new_start_response(status, response_headers, exc_info=None):
            response_headers.append(("x-correlation-id", corid))
            return start_response(status, response_headers, exc_info)

        return ProxyFix.__call__(self, environ, new_start_response)


def _user_has_permission():
    # These are secured by "authenticate_runner" and "assert_internal_user"
    if request.method in ("POST", "PATCH", "PUT"):
        return

    if request.path.startswith("/projects/") and len(request.path) > 10:
        path = request.path[10:]
        if path and not permissions.project_can_access(path):
            return jsendify("Object does not exist: " + request.path, 404)

    if request.path.startswith("/health/"):
        path = request.path[8:]
        if not permissions.health_can_access(path):
            return jsendify("Object does not exist: " + request.path, 404)


def _handle_404(e):
    return jsendify("Not Found", 404)


def create_app(settings_object="jobserv.settings"):
    app = Flask(__name__)
    app.wsgi_app = RequestIdMiddleware(app.wsgi_app)
    app.config.from_object(settings_object)

    # json_logging can only be initialized *once*. When running with gunicorn,
    # this gets called a couple times.
    if not getattr(create_app, "__logging_hack_initialized", None):
        json_logging.init_flask(enable_json=True)
        json_logging.init_request_instrument(app, exclude_url_patterns=["/healthz"])
        json_logging.config_root_logger()
        create_app.__logging_hack_initialized = True

    ProjectConverter.settings = settings_object
    app.url_map.converters["project"] = ProjectConverter

    from jobserv.models import db

    db.init_app(app)
    Migrate(app, db)

    import jobserv.api

    jobserv.api.register_blueprints(app)

    from jobserv.storage import Storage

    if Storage.blueprint:
        app.register_blueprint(Storage.blueprint)

    app.json_encoder = ISO8601_JSONEncoder
    app.before_request(_user_has_permission)
    app.register_error_handler(404, _handle_404)
    return app

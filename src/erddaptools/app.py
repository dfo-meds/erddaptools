import flask
from autoinject import injector
from erddaptools.dsm import DatasetFileManager, DatasetError
from erddaptools.keys import APIKeyManager
import logging


dsm = flask.Blueprint("dsm", __name__)


@injector.inject
def _authenticate_request(akm: APIKeyManager = None):
    return akm.verify_key(flask.request.headers.get("Authentication"))


@dsm.route("/update-dataset", methods=["POST"])
@injector.inject
def update_dataset(dfm: DatasetFileManager = None):
    body = flask.request.get_json()
    api_key_name = _authenticate_request()
    if not api_key_name:
        return flask.abort(403)
    if "id" not in body:
        logging.getLogger("erddaptools.app").error("Missing ID from request")
        return flask.Response("Missing ID", status=400)
    if "xml" not in body:
        logging.getLogger("erddaptools.app").error("Missing XML content from request")
        return flask.Response("Missing XML", status=400)
    is_active = None
    if "is_active" in body:
        is_active = body['is_active']
    try:
        dfm.update_dataset(body["id"], body["xml"], is_active, api_key_name=api_key_name)
        return flask.Response("Dataset updated", status=200)
    except DatasetError as ex:
        logging.getLogger("erddaptools.app").exception(ex)
        return flask.Response(str(ex), status=400)


@dsm.route("/create-dataset", methods=["POST"])
@injector.inject
def create_dataset(dfm: DatasetFileManager = None):
    body = flask.request.get_json()
    api_key_name = _authenticate_request()
    if not api_key_name:
        return flask.abort(403)
    if "id" not in body:
        logging.getLogger("erddaptools.app").error("Missing ID from request")
        return flask.Response("Missing ID", status=400)
    if "type" not in body:
        logging.getLogger("erddaptools.app").error("Missing dataset type from request")
        return flask.Response("Missing dataset type", status=400)
    if "xml" not in body:
        logging.getLogger("erddaptools.app").error("Missing XML content from request")
        return flask.Response("Missing XML", status=400)
    is_active = True
    if "is_active" in body:
        is_active = body['is_active']
    try:
        dfm.add_dataset(body['type'], body["id"], body["xml"], is_active, api_key_name=api_key_name)
        return flask.Response("Dataset created", status=200)
    except DatasetError as ex:
        logging.getLogger("erddaptools.app").exception(ex)
        return flask.Response(str(ex), status=400)


@dsm.route("/deactivate-dataset", methods=["POST"])
@injector.inject
def deactivate_dataset(dfm: DatasetFileManager = None):
    body = flask.request.get_json()
    api_key_name = _authenticate_request()
    if not api_key_name:
        return flask.abort(403)
    if "id" not in body:
        print("missing ID")
        logging.getLogger("erddaptools.app").error("Missing ID from request")
        return flask.Response("Missing ID", status=400)
    try:
        dfm.deactivate_dataset(body["id"], api_key_name=api_key_name)
        return flask.Response("Dataset deactivated", status=200)
    except DatasetError as ex:
        print(ex)
        logging.getLogger("erddaptools.app").exception(ex)
        return flask.Response(str(ex), status=400)


@dsm.route("/activate-dataset", methods=["POST"])
@injector.inject
def activate_dataset(dfm: DatasetFileManager = None):
    body = flask.request.get_json()
    api_key_name = _authenticate_request()
    if not api_key_name:
        return flask.abort(403)
    print(body)
    if "id" not in body:
        logging.getLogger("erddaptools.app").error("Missing ID from request")
        return flask.Response("Missing ID", status=400)
    try:
        dfm.activate_dataset(body["id"], api_key_name=api_key_name)
        return flask.Response("Dataset activated", status=200)
    except DatasetError as ex:
        print(ex)
        logging.getLogger("erddaptools.app").exception(ex)
        return flask.Response(str(ex), status=400)

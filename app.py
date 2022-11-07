import pathlib
import sys
import flask
import zirconium as zr
from autoinject import injector
import zrlog

sys.path.append(str(pathlib.Path(__file__).parent / "src"))


@zr.configure
def configure_zirconium(config: zr.ApplicationConfig):
    config.register_default_file("./.erddaptools.defaults.yaml")
    config.register_default_file("./.erddaptools.defaults.toml")
    config.register_file("~/.erddaptools.yaml")
    config.register_file("~/.erddaptools.toml")
    config.register_file("./.erddaptools.yaml")
    config.register_file("./.erddaptools.toml")


@injector.inject
def create_app(config: zr.ApplicationConfig = None):
    zrlog.init_logging()
    app = flask.Flask(__name__)
    if "flask" in config:
        app.config.update(config["flask"])

    from erddaptools.app import dsm
    app.register_blueprint(dsm)

    return app


app = create_app()

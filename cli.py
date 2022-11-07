import pathlib
import sys
import logging
import zirconium as zr

sys.path.append(str(pathlib.Path(__file__).parent / "src"))


@zr.configure
def configure_zirconium(config: zr.ApplicationConfig):
    config.register_default_file("./.erddaptools.defaults.yaml")
    config.register_default_file("./.erddaptools.defaults.toml")
    config.register_file("~/.erddaptools.yaml")
    config.register_file("~/.erddaptools.toml")
    config.register_file("./.erddaptools.yaml")
    config.register_file("./.erddaptools.toml")


try:
    from erddaptools.cli import base
    base()
except Exception as ex:
    logging.getLogger("erddaptools.cli").exception(ex)
    print(ex)

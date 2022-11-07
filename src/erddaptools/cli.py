import click
from .dsm import DatasetFileManager
from autoinject import injector
import zrlog
from .keys import APIKeyManager


@click.group
def base():
    zrlog.init_logging()


@base.command
@click.argument("dataset_id")
@click.argument("xml_file")
@click.option("--active", "is_active", flag_value="1")
@click.option("--inactive", "is_active", flag_value="0")
@click.option("--preserve-active", "is_active", flag_value="N", default=True)
@injector.inject
def update(dataset_id, xml_file, is_active, dfm: DatasetFileManager = None):
    if is_active == "1":
        is_active = True
    elif is_active == "0":
        is_active = False
    else:
        is_active = None
    with open(xml_file, "r") as h:
        dfm.update_dataset(dataset_id, xml_file, is_active)
        print("Dataset updated")


@base.command
@click.argument("dataset_type")
@click.argument("dataset_id")
@click.argument("xml_file")
@click.option("--active", "is_active", flag_value="1")
@click.option("--inactive", "is_active", flag_value="0")
@click.option("--preserve-active", "is_active", flag_value="N", default=True)
@injector.inject
def update(dataset_type, dataset_id, xml_file, is_active, dfm: DatasetFileManager = None):
    if is_active == "1":
        is_active = True
    elif is_active == "0":
        is_active = False
    else:
        is_active = None
    with open(xml_file, "r") as h:
        dfm.add_dataset(dataset_type, dataset_id, xml_file, is_active)
        print("Dataset created")


@base.command
@click.argument("dataset_id")
@injector.inject
def deactivate(dataset_id, dfm: DatasetFileManager = None):
    dfm.deactivate_dataset(dataset_id)
    print("Dataset deactivated")


@base.command
@click.argument("dataset_id")
@injector.inject
def activate(dataset_id, dfm: DatasetFileManager = None):
    dfm.activate_dataset(dataset_id)
    print("Dataset activated")


@base.group
def keys():
    pass


@keys.command
@click.argument("name")
@click.argument("description")
@click.option("--expiry-weeks", default=12)
@injector.inject
def generate(name, description, expiry_weeks, akm: APIKeyManager = None):
    akm.generate_key(name, description, int(expiry_weeks))
    print("Key generated")


@keys.command
@click.argument("name")
@click.option("--expiry-weeks", default=12)
@click.option("--old-expiry-weeks", default=4)
@injector.inject
def rotate(name, expiry_weeks, old_expiry_weeks, akm: APIKeyManager = None):
    akm.rotate_key(name, int(expiry_weeks), int(old_expiry_weeks))
    print("Key rotated")


@keys.command
@click.argument("name")
@injector.inject
def expire(name, akm: APIKeyManager = None):
    akm.expire_key(name)
    print("Key removed")

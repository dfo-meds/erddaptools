from autoinject import injector
import zirconium as zr
import pathlib
from .lfile import LockedFile
from lxml import etree
import typing as t
import logging


class DatasetError(Exception):
    pass


@injector.injectable
class DatasetFileManager:

    config: zr.ApplicationConfig = None

    @injector.construct
    def __init__(self):
        pass

    def update_dataset(self, dataset_id: str, xml_config: str, is_active: t.Optional[bool] = None, api_key_name: str = "..CLI.."):
        with self._build_lock_file() as file:
            xml_content = self._parse_dataset_file(file)
            root = xml_content.getroot()
            for dataset in root.findall("dataset"):
                ds_id = dataset.attrib.get("datasetID")
                if ds_id == dataset_id:
                    new_ds = etree.fromstring('<dataset>' + xml_config + '</dataset>')
                    if is_active is not None:
                        new_ds.attrib["active"] = "true" if is_active else "false"
                    else:
                        new_ds.attrib['active'] = dataset.attrib['active']
                    new_ds.attrib["datasetID"] = dataset.attrib['datasetID']
                    new_ds.attrib["type"] = dataset.attrib['type']
                    root.remove(dataset)
                    root.append(new_ds)
                    break
            else:
                raise DatasetError(f"No such dataset {dataset_id}")
            self._write_dataset_file(file, xml_content)
            logging.getLogger("erddaptools.dsm").info(f"Dataset {dataset_id} updated by {api_key_name}")

    def add_dataset(self, dataset_type: str, dataset_id: str, xml_config: str, is_active: bool = True, api_key_name: str = ".cli"):
        with self._build_lock_file() as file:
            xml_content = self._parse_dataset_file(file)
            root = xml_content.getroot()
            for dataset in root.findall("dataset"):
                ds_id = dataset.attrib.get("datasetID")
                if ds_id == dataset_id:
                    raise DatasetError(f"Dataset {dataset_id} already exists")
            xml_element = etree.fromstring('<dataset>' + xml_config + '</dataset>')
            xml_element.attrib["active"] = "true" if is_active else "false"
            xml_element.attrib["datasetID"] = dataset_id
            xml_element.attrib["type"] = dataset_type
            root.append(xml_element)
            self._write_dataset_file(file, xml_content)
            logging.getLogger("erddaptools.dsm").info(f"Dataset {dataset_id} added by {api_key_name}")

    def deactivate_dataset(self, dataset_id: str, api_key_name: str = ".cli"):
        self._set_dataset_active_flag(dataset_id, False, api_key_name=api_key_name)

    def activate_dataset(self, dataset_id: str, api_key_name: str = ".cli"):
        self._set_dataset_active_flag(dataset_id, True, api_key_name=api_key_name)

    def _set_dataset_active_flag(self, dataset_id: str, is_active: bool, api_key_name: str = ".cli"):
        with self._build_lock_file() as file:
            xml_content = self._parse_dataset_file(file)
            root = xml_content.getroot()
            for dataset in root.findall("dataset"):
                ds_id = dataset.attrib.get("datasetID")
                if ds_id == dataset_id:
                    dataset.attrib['active'] = 'true' if is_active else 'false'
                    break
            else:
                raise DatasetError(f"No such dataset {dataset_id}")
            self._write_dataset_file(file, xml_content)
            logging.getLogger("erddaptools.dsm").info(f"Dataset {dataset_id}'s active flag updated to {is_active} by {api_key_name}")

    def _parse_dataset_file(self, file: t.Union[str, pathlib.Path]) -> etree._ElementTree:
        return etree.parse(file)

    def _write_dataset_file(self, file: t.Union[str, pathlib.Path], tree: etree._ElementTree):
        tree.write(file, encoding="ISO-8859-1")

    def _build_lock_file(self):
        path = self.config.as_path(("erddaptools", "dsm", "dataset_file"))
        if (not path) or not path.exists():
            raise DatasetError("Dataset file does not exist")
        retries = self.config.as_int(("erddaptools", "dsm", "lock_retries"), default=5)
        delay = self.config.as_float(("erddaptools", "dsm", "lock_retry_delay"), default=0.5)
        return LockedFile(path, retries, delay)

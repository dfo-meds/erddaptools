from autoinject import injector
import zirconium as zr
import csv
import datetime
from .lfile import LockedFile
import hashlib
import secrets
import logging
import re


@injector.injectable
class APIKeyManager:

    config: zr.ApplicationConfig = None

    @injector.construct
    def __init__(self):
        pass

    def verify_key(self, bearer_token):
        if bearer_token is None or not bearer_token.startswith("Bearer "):
            raise ValueError("Invalid authentication header")
        path = self.config.as_path(("erddaptools", "key_file"))
        if not path:
            raise ValueError("Key file not defined")
        key_list = self._build_key_list(path)
        name, api_key = bearer_token[7:].strip(" ").split(".", maxsplit=1)
        if name not in key_list:
            raise ValueError("Invalid key name")
        n = datetime.datetime.now()
        if key_list[name]["expiry"] > n:
            if secrets.compare_digest(self._hash_api_key(api_key, key_list[name]["salt"]), key_list[name]["hash"]):
                logging.getLogger("erddaptools.app").info(f"Access granted to {name}")
                return name
        if key_list[name]["old_expiry"] and key_list[name]["old_expiry"] > n:
            if secrets.compare_digest(self._hash_api_key(api_key, key_list[name]["old_salt"]), key_list[name]["old_hash"]):
                logging.getLogger("erddaptools.app").info(f"Access granted to {name} using older key")
                return name
        raise ValueError("Invalid API key")

    def generate_key(self, name, description, expiry_weeks):
        if not re.fullmatch('[A-Za-z0-9_-]+', name):
            raise ValueError(f"Invalid key name: {name}")
        with self._build_file() as file:
            key_list = self._build_key_list(file)
            if name in key_list:
                raise ValueError(f"Key list already contains an entry named {name}")
            api_key, salt = self._generate_secure_api_key()
            key_list[name] = {
                "description": description,
                "hash": self._hash_api_key(api_key, salt),
                "salt": salt,
                "expiry": datetime.datetime.now() + datetime.timedelta(weeks=expiry_weeks),
                "old_hash": "",
                "old_expiry": "",
                "old_salt": ""
            }
            self._write_key_list(file, key_list)
            print(f"New API key: {name}.{api_key}")
            logging.getLogger("erddaptools.admin").info(f"API key {name} created")

    def rotate_key(self, name, expiry_weeks, old_expiry_weeks):
        with self._build_file() as file:
            key_list = self._build_key_list(file)
            if name not in key_list:
                raise ValueError(f"Key list does not contain an entry named {name}")
            api_key, salt = self._generate_secure_api_key()
            key_list[name].update({
                "hash": self._hash_api_key(api_key, salt),
                "salt": salt,
                "expiry": datetime.datetime.now() + datetime.timedelta(weeks=expiry_weeks),
                "old_hash": key_list[name]["hash"],
                "old_salt": key_list[name]["salt"],
                "old_expiry": datetime.datetime.now() + datetime.timedelta(weeks=old_expiry_weeks)
            })
            self._write_key_list(file, key_list)
            print(f"Updated API key: {name}.{api_key}")
            logging.getLogger("erddaptools.admin").info(f"API key {name} rotated")

    def expire_key(self, name):
        with self._build_file() as file:
            key_list = self._build_key_list(file)
            if name not in key_list:
                raise ValueError(f"Key list does not contain an entry named {name}")
            key_list[name].update({
                "hash": "",
                "expiry": datetime.datetime.now(),
                "old_hash": "",
                "old_expiry": ""
            })
            self._write_key_list(file, key_list)
            logging.getLogger("erddaptools.admin").info(f"API key {name} expired.")

    def _build_key_list(self, file):
        key_list = {}
        if file.exists():
            with open(file, "r") as h:
                reader = csv.reader(h)
                for line in reader:
                    if line:
                        key_list[line[0]] = self._parse_key_entry(line)
        return key_list

    def _write_key_list(self, file, key_list):
        with open(file, "w") as h:
            writer = csv.writer(h)
            for key in key_list:
                row = [key]
                row.extend(self._build_key_entry(key_list[key]))
                writer.writerow(row)

    def _parse_key_entry(self, row):
        return {
            "hash": row[1],
            "expiry": datetime.datetime.strptime(row[2], "%Y-%m-%d %H:%M:%S"),
            "salt": row[3],
            "old_hash": row[4],
            "old_expiry": datetime.datetime.strptime(row[5], "%Y-%m-%d %H:%M:%S") if row[5] else None,
            "old_salt": row[7],
            "description": row[6]
        }

    def _build_key_entry(self, entry):
        return [
            entry["hash"],
            entry["expiry"].strftime("%Y-%m-%d %H:%M:%S"),
            entry["salt"],
            entry["old_hash"] if entry["old_hash"] else "",
            entry["old_expiry"].strftime("%Y-%m-%d %H:%M:%S") if entry["old_expiry"] else "",
            entry["old_salt"] if entry["old_salt"] else "",
            entry["description"]
        ]

    def _hash_api_key(self, api_key, salt):
        return hashlib.pbkdf2_hmac("sha256", api_key.encode("utf-8"), salt.encode("utf-8"), 301502).hex()

    def _generate_secure_api_key(self):
        return secrets.token_urlsafe(64), secrets.token_hex(32)

    def _build_file(self):
        path = self.config.as_path(("erddaptools", "key_file"))
        if not path:
            raise ValueError("Key file not defined")
        return LockedFile(path, 1, 1)


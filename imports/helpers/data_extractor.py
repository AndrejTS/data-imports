import json
from abc import ABC, abstractmethod
from typing import Iterable, Dict, Any

import xmltodict
import pandas as pd


class DataExtractor(ABC):
    """Extracts data from a specific format into a general structure (a list of dictionaries)."""

    @abstractmethod
    def extract(self, file_obj, config: dict) -> Iterable[Dict[str, Any]]:
        pass


class XMLExtractor(DataExtractor):
    def extract(self, file_obj, config: dict) -> Iterable[Dict[str, Any]]:
        xml_data = xmltodict.parse(
            file_obj, process_namespaces=True, namespaces=config.get("xml_namespaces")
        )
        items = self._get_items(xml_data, config["xml_item_path"])
        return items

    def _get_items(self, data: dict, path: str) -> list:
        keys = path.split(".")
        current = data

        for key in keys:
            if isinstance(current, dict):
                current = current.get(key, {})
            else:
                return []

        return current if isinstance(current, list) else [current]


class CSVExtractor(DataExtractor):
    def extract(self, file_obj, config: dict) -> Iterable[Dict[str, Any]]:
        df = pd.read_csv(file_obj, sep=";")
        return df.to_dict("records")


class JSONExtractor(DataExtractor):
    def extract(self, file_obj, config: dict) -> Iterable[Dict[str, Any]]:
        data = json.load(file_obj)
        return data[config["json_root_key"]]

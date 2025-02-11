from typing import Dict

from helpers.base_import import BaseImport
from helpers.file_fetchers import LocalFileFetcher
from helpers.data_extractor import XMLExtractor


CONFIG = {
    "website_id": "electronics-shop.com",
    "file_path": "/app/electronics_shop.xml",
    "xml_item_path": "Products.Product",  # Path to items in XML
    "xml_namespaces": None,  # Use if XML contains namespaces
    "mapping": {
        "sku": "Identifiers.SKU",
        "price": "Pricing.Price.#text",
        "currency": "Pricing.Price.@currency",
        "name": "BasicInfo.Name",
    },
}


class ElectronicsShop(BaseImport):
    def __init__(self, config: Dict):
        self.config = config
        self.fetcher = LocalFileFetcher()
        self.extractor = XMLExtractor()


def run_import():
    import_obj = ElectronicsShop(CONFIG)
    import_obj.import_data()

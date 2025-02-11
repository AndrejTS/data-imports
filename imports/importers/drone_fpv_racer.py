from typing import Dict

from helpers.base_import import BaseImport
from helpers.file_fetchers import LocalFileFetcher
from helpers.data_extractor import CSVExtractor


CONFIG = {
    "website_id": "drone-fpv-racer.com",
    "file_path": "/app/drone-fpv-racer.csv",
    "mapping": {
        "sku": "ProductCode",
        "name": "ProductName",
        "price": "Price",
        "product_url": "ProductURL",
    },
    "matcher": {
        "use_url": True,
    },
}


class DroneFPVRacer(BaseImport):
    def __init__(self, config: Dict):
        self.config = config
        self.fetcher = LocalFileFetcher()
        self.extractor = CSVExtractor()


def run_import():
    import_obj = DroneFPVRacer(CONFIG)
    import_obj.import_data()

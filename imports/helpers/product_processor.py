from typing import Dict
from datetime import datetime

from pymongo import MongoClient

from helpers.product_matcher import ProductMatcher


class ProductProcessor:
    def __init__(self, config: Dict):
        mongo_client = MongoClient("mongodb://mongodb:27017/")
        self.db = mongo_client["my_mongo_db"]
        self.matcher = ProductMatcher(self.db, config)

    def upsert_enhanced_product(self, product_data: Dict):
        filter_ = {"sku": product_data.get("sku")}
        utc_time = datetime.utcnow()
        update = {
            "$set": {
                **product_data,
                "updated_at": utc_time,
            },
            "$setOnInsert": {
                "created_at": utc_time,
            },
        }

        return self.db.enhanced_products.update_one(filter_, update, upsert=True)

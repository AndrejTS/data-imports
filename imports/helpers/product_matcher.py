from typing import Optional, Dict
import logging

from pymongo import MongoClient


logger = logging.getLogger(__name__)


class ProductMatcher:
    """A class for finding product matches in database."""

    def __init__(self, db: MongoClient, config: Optional[Dict] = None):
        self.db = db
        self.website_id = config["website_id"]
        self.config = config.get("matcher") or {}

    def find_match(self, product_data: Dict) -> Optional[Dict]:
        conditions = []
        if self.config.get("use_sku") and product_data.get("sku"):
            conditions.append({"sku": product_data["sku"]})
        if self.config.get("use_url") and product_data.get("product_url"):
            conditions.append({"product_url": product_data["product_url"]})

        if not conditions:
            return None

        query = {"website_id": self.website_id}

        if len(conditions) > 1:
            query["$or"] = conditions
        else:
            query.update(conditions[0])

        match = self.db.products.find_one(query)
        if match:
            logger.info(f"Matched with query: {query}")
        return match

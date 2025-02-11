import importlib
import sys
import os
import logging
from typing import Dict

from celery import Celery

from helpers.product_processor import ProductProcessor


logger = logging.getLogger(__name__)

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = Celery(
    "tasks", broker="redis://redis:6379/0", backend="redis://redis:6379/1"
)

app.config_from_object("celeryconfig")


@app.task(name="import_data")
def import_data(website_id: str):
    WEBSITE_ID2MODULE_NAME = {
        "drone-fpv-racer.com": "drone_fpv_racer",
        "electronics-shop.com": "electronics_shop",
    }

    try:
        logger.info(f"Starting import for website: {website_id}")

        website_module = importlib.import_module(
            ".".join(["importers", WEBSITE_ID2MODULE_NAME[website_id]])
        )

        website_module.run_import()

        logger.info(f"Import for website {website_id} completed successfully.")

    except ImportError as e:
        logger.error(f"Module for website {website_id} not found: {str(e)}")
        raise
    except Exception as e:
        logger.exception(f"Error during import for website {website_id}: {str(e)}")
        raise


@app.task(name="process_product")
def process_product(product_data: Dict, config: Dict):
    try:
        processor = ProductProcessor(config)

        match_product = processor.matcher.find_match(product_data)
        if match_product:
            product_data["product_id"] = match_product["product_id"]
        else:
            product_data["product_id"] = None

        processor.upsert_enhanced_product(product_data)
        logger.info(f"Upsert enhanced product: {product_data}")

    except Exception as ex:
        logger.error(
            f"Error processing product {product_data.get('sku', 'unknown')}: {str(ex)}"
        )

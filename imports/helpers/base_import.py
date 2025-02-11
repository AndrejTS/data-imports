import logging

from helpers.data_loader import DataLoader
from helpers.data_mapper import DataMapper
from tasks import process_product


logger = logging.getLogger(__name__)


class BaseImport:
    def import_data(self):
        try:
            loader = DataLoader(fetcher=self.fetcher, extractor=self.extractor)
            raw_data = loader.load(self.config)

            mapper = DataMapper(mapping_config=self.config["mapping"])

            for item in raw_data:
                try:
                    product_data = mapper.map(item)
                    product_data["website_id"] = self.config["website_id"]

                    # Send to Celery task
                    process_product.delay(product_data, self.config)
                    logger.info(f"Sent to processing: {product_data['sku']}")

                except Exception as e:
                    logger.error(f"Error processing item {item}: {str(e)}")
                    continue

        except Exception as e:
            logger.critical(f"Import failed: {str(e)}")
            raise

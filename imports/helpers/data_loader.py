from typing import Dict, Any, Iterable


class DataLoader:
    def __init__(self, fetcher, extractor):
        self.fetcher = fetcher
        self.extractor = extractor

    def load(self, config: Dict[str, Any]) -> Iterable[Dict[str, Any]]:
        file_obj = self.fetcher.fetch(config)

        try:
            yield from self.extractor.extract(file_obj, config)
        finally:
            if hasattr(file_obj, "close"):
                file_obj.close()

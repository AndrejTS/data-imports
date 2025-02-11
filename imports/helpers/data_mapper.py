from typing import Dict


class DataMapper:
    def __init__(self, mapping_config: Dict, transformers: Dict = None):
        self.mapping = mapping_config
        self.transformers = transformers or {}

    def map(self, raw_data: Dict) -> Dict:
        mapped_data = {}

        for field, path in self.mapping.items():
            value = self._get_value(raw_data, path)

            # Apply transformation if defined
            if field in self.transformers:
                value = self.transformers[field](value)

            mapped_data[field] = value

        return mapped_data

    def _get_value(self, data: Dict, path: str) -> Dict:
        """Retrieves values ​​from nested structures using dot notation and indices."""
        keys = path.split(".")
        current = data

        try:
            for key in keys:
                if "[" in key and "]" in key:
                    # ex. images[0]
                    key_part, index = key[:-1].split("[")
                    index = int(index)
                    current = current.get(key_part, [])[index]
                else:
                    current = current.get(key, {})

            return current if current != {} else None
        except Exception:
            raise


# example transformers
# transformers = {
#     "price": lambda x: float(x.replace(" Kč", "")),
#     "categories": lambda x: x.split("/"),
# }

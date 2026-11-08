import tempfile
import unittest
from pathlib import Path

from scripts.setup_project_board import product_values


class ProductStageTests(unittest.TestCase):
    def test_retired_product_remains_decommissioned_when_board_is_seeded(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "retired.yaml"
            path.write_text(
                'sku: ADS1115\nname: Retired module\nactive: false\n'
                'listing_state: retired\nstock: 0\ntindie_product_id: "6476"\n',
                encoding="utf-8",
            )
            _, _, values = product_values(path)
            self.assertEqual(values["Status"], "Decommission")


if __name__ == "__main__":
    unittest.main()

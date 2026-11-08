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

    def test_business_case_fields_are_exposed_to_the_board(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "candidate.yaml"
            path.write_text(
                'sku: OLD-BOARD\nname: Old board\nactive: true\nstock: 0\n'
                'lifecycle:\n'
                '  stage: Sustaining\n'
                '  review_date: "2027-02-08"\n'
                'business_case:\n'
                '  decision: Retirement candidate\n'
                '  approval_state: Proposed\n'
                '  confidence: High\n'
                '  analysis_url: https://example.com/analysis\n'
                '  tindie_sales:\n'
                '    lifetime_units: 1\n'
                '    last_sale: "2020-01-01"\n',
                encoding="utf-8",
            )
            _, body, values = product_values(path)
            self.assertEqual(values["Decision"], "Retirement candidate")
            self.assertEqual(values["Approval state"], "Proposed")
            self.assertEqual(values["Lifetime units"], 1)
            self.assertEqual(values["Last sale"], "2020-01-01")
            self.assertIn("https://example.com/analysis", body)


if __name__ == "__main__":
    unittest.main()

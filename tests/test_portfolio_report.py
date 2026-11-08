import tempfile
import unittest
from pathlib import Path

from scripts.portfolio_report import validate


class PortfolioReportTests(unittest.TestCase):
    def test_retirement_candidate_requires_approval(self):
        product = {
            "listing_state": "draft",
            "lifecycle": {
                "stage": "Sustaining",
                "product_line": "Energy monitoring",
                "interest_area": "Electronics",
                "channel": "Tindie",
                "review_date": "2027-02-08",
            },
            "business_case": {
                "decision": "Retirement candidate",
                "approval_state": "Approved",
                "confidence": "High",
                "analysis_url": "https://example.com",
                "tindie_sales": {"lifetime_units": 0, "lifetime_orders": 0},
            },
        }
        errors = validate(Path("candidate.yaml"), product)
        self.assertIn(
            "candidate.yaml: retirement candidates must remain Proposed",
            errors,
        )

    def test_complete_product_passes(self):
        product = {
            "listing_state": "draft",
            "lifecycle": {
                "stage": "Prototype",
                "product_line": "Energy monitoring",
                "interest_area": "Electronics",
                "channel": "None",
                "review_date": "2027-02-08",
            },
            "business_case": {
                "decision": "Invest",
                "approval_state": "Approved",
                "confidence": "High",
                "analysis_url": "https://example.com",
                "tindie_sales": {"lifetime_units": 0, "lifetime_orders": 0},
            },
        }
        self.assertEqual(validate(Path("product.yaml"), product), [])


if __name__ == "__main__":
    unittest.main()

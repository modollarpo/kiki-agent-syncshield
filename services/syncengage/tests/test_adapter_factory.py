import unittest
from app.adapter_factory import get_crm_adapter, KlaviyoAdapter, HubSpotAdapter, SalesforceAdapter

class TestAdapterFactory(unittest.TestCase):
    def test_get_klaviyo(self):
        adapter = get_crm_adapter("klaviyo")
        self.assertIsInstance(adapter, KlaviyoAdapter)

    def test_get_hubspot(self):
        adapter = get_crm_adapter("hubspot")
        self.assertIsInstance(adapter, HubSpotAdapter)

    def test_get_salesforce(self):
        adapter = get_crm_adapter("salesforce")
        self.assertIsInstance(adapter, SalesforceAdapter)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            get_crm_adapter("unknown")

if __name__ == "__main__":
    unittest.main()
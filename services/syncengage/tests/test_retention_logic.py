import unittest
from app.retention_logic import RetentionEngine

class TestRetentionEngine(unittest.TestCase):
    def setUp(self):
        self.engine = RetentionEngine("klaviyo")
        self.brand_dna_luxury = {"voice": "Elegant, exclusive, understated", "tone": "Sophisticated"}
        self.brand_dna_discount = {"voice": "Energetic, friendly, value-driven", "tone": "Fun"}
        self.customer = {"id": "123", "name": "Alex"}

    def test_generate_winback_message_luxury(self):
        subject, body = self.engine.generate_winback_message(self.brand_dna_luxury, self.customer)
        self.assertIn("Elegant", body)
        self.assertIn("Sophisticated", body)

    def test_generate_winback_message_discount(self):
        subject, body = self.engine.generate_winback_message(self.brand_dna_discount, self.customer)
        self.assertIn("Energetic", body)
        self.assertIn("Fun", body)

    def test_send_retention_flow(self):
        # Should not raise
        self.engine.send_retention_flow(self.brand_dna_luxury, self.customer, "email")

if __name__ == "__main__":
    unittest.main()
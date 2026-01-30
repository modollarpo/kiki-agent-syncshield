import unittest
from services.syncshield.audit.roi_engine import calculate_roi

class TestROICalculation(unittest.TestCase):
    def test_extreme_values(self):
        # Extreme positive ROI
        self.assertEqual(calculate_roi(1000000, 10000, 100), 989900.0)
        # Zero AI revenue
        self.assertEqual(calculate_roi(0, 10000, 100), -10100.0)
        # Negative net gain
        self.assertEqual(calculate_roi(5000, 10000, 100), -5100.0)
        # AI op cost zero (should handle div by zero)
        with self.assertRaises(ZeroDivisionError):
            calculate_roi(10000, 10000, 0)

if __name__ == "__main__":
    unittest.main()

# SyncBill Logic

This directory contains the core billing and settlement logic for the KIKI Agent™ OaaS platform.

## Files
- `settlement.js`: Calculates OaaS settlement and KIKI success fee for each billing cycle.
- `qbr_report.py`: Generates Quarterly Business Review (QBR) PDF reports for clients, summarizing uplift, fees, and net benefit.

## Usage
- Integrate `settlement.js` in the billing API to compute fees and net benefit.
- Use `qbr_report.py` to generate PDF reports for QBR automation.

All logic is production-ready, typed, and documented.

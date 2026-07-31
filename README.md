# Land Bids Automation - Public

Daily automation that scans Israel's land tender site for selected settlements and emails a clean summary table of active bids.

## What it does

- Opens [apps.land.gov.il](https://apps.land.gov.il/MichrazimSite/#/homePage)
- Searches a configurable list of Hebrew settlement names
- Collects tender ID, settlement, publish date, open status, and deadline
- Sends one deduplicated HTML email summary

Runs locally or on a daily GitHub Actions schedule.

## Example output

![Daily land tenders email summary](docs/email-summary-example.png)

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. Set environment variables:
   ```bash
   export GMAIL_USER="your@gmail.com"
   export GMAIL_PASS="your-gmail-app-password"
   export TARGET_EMAIL="recipient@gmail.com"
   ```

3. Run:
   ```bash
   python shuki_auto.py
   ```

## GitHub Actions

Add these repository secrets:

- `GMAIL_USER`
- `GMAIL_PASS`
- `TARGET_EMAIL`

Then use **Actions → Daily Land Tender Scan → Run workflow** to test, or wait for the daily cron run.

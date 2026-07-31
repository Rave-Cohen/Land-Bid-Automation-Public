from playwright.sync_api import sync_playwright
import time
import pandas as pd
import smtplib
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# --- CONFIGURATION ---
GMAIL_USER = os.environ.get("GMAIL_USER", "")
GMAIL_PASS = os.environ.get("GMAIL_PASS")
TARGET_EMAIL = os.environ.get("TARGET_EMAIL", "")

SETTLEMENTS = [
    "בית עובד", "בצרה", "שריגים", "אדרת", "גנות", "כפר הרא״ה", "כפר מונש", "משמר אילון", "מכמרת",
    "מבואות ים", "בית ינאי", "שדות ים", "בת חפר", "בנימינה",
    "בית מאיר", "נס הרים", "צובה", "בית זית", "גבעות עדן"
]

def send_summary_email(data_list):
    if not data_list:
        return
    if not GMAIL_USER or not TARGET_EMAIL or not GMAIL_PASS:
        print("Email skipped: set GMAIL_USER, TARGET_EMAIL, and GMAIL_PASS.")
        return

    df = pd.DataFrame(data_list)
    msg = MIMEMultipart()
    msg['Subject'] = f"Land Tenders Update - {time.strftime('%d/%m/%Y')}"
    msg['From'] = GMAIL_USER
    msg['To'] = TARGET_EMAIL

    html_table = df.to_html(index=False, justify='center')
    html_body = f"""
    <html dir="rtl">
      <body style="text-align: right; font-family: Arial, sans-serif;">
        <h2 style="color: #2c3e50;">Active Tenders Summary</h2>
        {html_table}
      </body>
    </html>
    """
    msg.attach(MIMEText(html_body, 'html'))
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, TARGET_EMAIL, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print(f"Email error: {e}")

def run():
    unique_tenders = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, slow_mo=600)
        page = browser.new_page()

        print("Navigating to site...")
        page.goto("https://apps.land.gov.il/MichrazimSite/#/homePage", wait_until="networkidle")

        page.wait_for_selector("div.card.first button.button-enter")
        page.click("div.card.first button.button-enter")

        input_selector = "input.p-autocomplete-input"
        page.wait_for_selector(input_selector)

        for city in SETTLEMENTS:
            print(f"Searching: {city}")

            page.click(input_selector)
            page.fill(input_selector, "")
            page.type(input_selector, city, delay=100)

            try:
                dropdown_item = page.wait_for_selector(f"li:has-text('{city}')", timeout=5000)
                dropdown_item.click()

                page.click("button.icon-search")
                time.sleep(2)

                results = page.locator("app-michraz-details").all()
                for item in results:
                    t_num_el = item.locator(".mis-michraz").first
                    t_num = t_num_el.inner_text().strip() if t_num_el.count() > 0 else "N/A"

                    if t_num not in unique_tenders:
                        full_text = item.inner_text()

                        def clean_val(raw, label):
                            val = raw.replace(label, "").replace(":", "").replace("\t", " ")
                            for filler in ("תאריך", "להגשת הצעות"):
                                val = val.replace(filler, "")
                            return " ".join(val.split()) or "N/A"

                        def get_val(label):
                            for line in full_text.split('\n'):
                                if label in line:
                                    return clean_val(line, label)
                            return "N/A"

                        unique_tenders[t_num] = {
                            "Tender": t_num,
                            "Settlement": city,
                            "Publish": get_val("פרסום"),
                            "Open": get_val("פתיחה"),
                            "Close": get_val("מועד אחרון")
                        }
                        print(f"  [+] Found: {t_num}")
            except Exception:
                print(f"  [-] Suggestion for {city} didn't appear in time.")

        if unique_tenders:
            send_summary_email(list(unique_tenders.values()))
        else:
            print("No results found.")

        browser.close()

if __name__ == "__main__":
    run()

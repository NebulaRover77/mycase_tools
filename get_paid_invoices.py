import pandas as pd
from datetime import datetime, timedelta, timezone
from dateutil import parser
from fetch_and_save import fetch_and_save_data

client_cache = {}

def get_client_name(client_id):
    if not client_id:
        return "N/A"
    
    if client_id in client_cache:
        return client_cache[client_id]
    
    client_data = fetch_and_save_data("v1", "clients", id=client_id, verbose=False)
    
    if client_data:
        client_name = client_data.get("first_name", "") + " " + client_data.get("last_name", "")
        client_cache[client_id] = client_name  # Cache the result
        return client_name
    else:
        return "Unknown Client"

def filter_payments(payments, start_date):
    filtered = []
    for p in payments:
        if "date" in p:
            try:
                payment_date = parser.parse(p["date"]).astimezone(timezone.utc)
                if payment_date >= start_date:
                    filtered.append(p)
            except Exception as e:
                print(f"Error parsing date {p['date']}: {e}")
    return filtered

def fetch_invoice_payments():
    today = datetime.now(timezone.utc).replace(hour=23, minute=59, second=59, microsecond=999999)
    last_week = today - timedelta(days=13)
    start_date = last_week.replace(hour=0, minute=0, second=0, microsecond=0)
    
    print(f"Start date: {start_date.isoformat()}")
    
    payments = fetch_and_save_data("v1","invoice_payments")
    payments = filter_payments(payments, start_date)
    
    # Extract relevant fields
    data = [
        {
            "date": p.get("date", "N/A"),
            "amount": p.get("amount", "N/A"),
            "invoice_number": p.get("invoice_number", "N/A"),
            "status": p.get("status", "N/A"),
            "account_name": p.get("account_name", "N/A"),
            "client_name": get_client_name(p.get("client", {}).get("id"))
        }
        for p in payments
    ]
    
    df = pd.DataFrame(data)
    print(df.to_string(index=False))
    
    # Save to CSV for easier analysis
    df.to_csv("data/invoice_payments.csv", index=False)
    print("Invoice payments saved to data/invoice_payments.csv")

if __name__ == '__main__':
    fetch_invoice_payments()

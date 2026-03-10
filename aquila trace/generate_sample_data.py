"""
Generate sample transaction data for testing AquilaTrace.
Run this before starting the application for the first time.
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# Configuration
NUM_TRANSACTIONS = 5000
NUM_ACCOUNTS = 500
ANOMALY_PERCENTAGE = 5

# Create data directory if it doesn't exist
os.makedirs("data", exist_ok=True)

print("[*] Generating sample transaction data...")

np.random.seed(42)

# Generate accounts
accounts = [f"ACC{str(i).zfill(6)}" for i in range(NUM_ACCOUNTS)]
countries = ["US", "GB", "CN", "JP", "IN", "DE", "FR", "CA", "AU", "SG"]

# Generate transaction data
transactions = []

for i in range(NUM_TRANSACTIONS):
    # Normal transactions
    if np.random.random() > ANOMALY_PERCENTAGE / 100:
        amount = np.random.lognormal(mean=7, sigma=2)  # Log-normal distribution
        sender = np.random.choice(accounts)
        receiver = np.random.choice(accounts)
    else:
        # Anomalous transactions (suspicious patterns)
        amount = np.random.lognormal(mean=12, sigma=3)  # Much larger amounts
        sender = np.random.choice(accounts[:50])  # Fewer accounts
        receiver = np.random.choice(accounts[-50:])  # Different set
    
    sender_country = np.random.choice(countries)
    receiver_country = np.random.choice(countries)
    
    timestamp = datetime.now() - timedelta(days=np.random.randint(0, 90))
    
    transactions.append({
        "id": f"TXN{str(i).zfill(8)}",
        "sender": sender,
        "receiver": receiver,
        "amount": round(amount, 2),
        "sender_country": sender_country,
        "receiver_country": receiver_country,
        "timestamp": timestamp.isoformat()
    })

# Create DataFrame
df = pd.DataFrame(transactions)

# Save to CSV
file_path = "data/transactions.csv"
df.to_csv(file_path, index=False)

print(f"[✓] Generated {len(df)} transactions")
print(f"[✓] Saved to {file_path}")
print(f"\nDataset Statistics:")
print(f"  - Total Transactions: {len(df)}")
print(f"  - Unique Senders: {df['sender'].nunique()}")
print(f"  - Unique Receivers: {df['receiver'].nunique()}")
print(f"  - Amount Range: ${df['amount'].min():.2f} - ${df['amount'].max():.2f}")
print(f"  - Average Amount: ${df['amount'].mean():.2f}")
print(f"\nSample Data:")
print(df.head(10).to_string())
print(f"\nReady to run: python main.py")

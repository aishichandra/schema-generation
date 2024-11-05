from pathlib import Path

import duckdb

emails_container = Path("./data/emails")
emails_container.mkdir(exist_ok=True)

con = duckdb.connect(database=":memory:")
emails = con.execute(
    "SELECT message FROM './data/enron_sample_small.parquet';"
).fetchall()
emails = [email[0] for email in emails]

for i, email in enumerate(emails):
    with open(emails_container / f"email_{i}.txt", "w") as f:
        f.write(email)

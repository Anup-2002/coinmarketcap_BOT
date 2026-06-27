import json
import pandas as pd

with open(
    "output/last_trending.json",
    "r",
    encoding="utf-8"
) as f:

    coins = json.load(f)

print(
    f"Total records: {len(coins)}"
)

df = pd.DataFrame(
    coins
)

# Duplicate URL
duplicate_urls = df[
    df.duplicated(
        subset=["url"],
        keep=False
    )
]

print(
    f"Duplicate URLs: {len(duplicate_urls)}"
)

# Duplicate names
duplicate_names = df[
    df.duplicated(
        subset=["name"],
        keep=False
    )
]

print(
    f"Duplicate names: {len(duplicate_names)}"
)

# Duplicate symbols
duplicate_symbols = df[
    df.duplicated(
        subset=["symbol"],
        keep=False
    )
]

print(
    f"Duplicate symbols: {len(duplicate_symbols)}"
)

# Save everything
df.to_csv(
    "output/trending_coins.csv",
    index=False
)

duplicate_urls.to_csv(
    "output/duplicate_urls.csv",
    index=False
)

duplicate_names.to_csv(
    "output/duplicate_names.csv",
    index=False
)

duplicate_symbols.to_csv(
    "output/duplicate_symbols.csv",
    index=False
)

print(
    "CSV files created."
)
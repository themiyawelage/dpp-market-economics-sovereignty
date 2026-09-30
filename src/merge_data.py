from collections import defaultdict

from src.clean_data import main as clean_all
from src.config import EU27, PROCESSED
from src.io_utils import write_csv


def main():
    circularity, trade, digital = clean_all()
    panel = defaultdict(dict)
    for row in circularity:
        if row["country"] in EU27:
            panel[(row["country"], row["year"])]["circularity_rate"] = row["value"]
    for row in trade:
        if row["country"] in EU27:
            panel[(row["country"], row["year"])]["recyclable_imports_tonnes"] = row["value"]
    for row in digital:
        if row["country"] not in EU27 or row["intensity"] != "basic_or_above":
            continue
        key = f"digital_basic_{row['size_class']}_{row['version']}"
        panel[(row["country"], row["year"])][key] = row["value"]
    digital_keys = sorted({key for values in panel.values() for key in values if key.startswith("digital_")})
    rows = []
    for (country, year), values in sorted(panel.items()):
        row = {"country": country, "year": year}
        row.update(values)
        rows.append(row)
    fields = ["country", "year", "circularity_rate", "recyclable_imports_tonnes"] + digital_keys
    write_csv(PROCESSED / "eu_panel_data.csv", rows, fields)
    return rows


if __name__ == "__main__":
    main()

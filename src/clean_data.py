from src.config import EU27, PROCESSED, RAW
from src.io_utils import write_csv
from src.xlsx_reader import read_sheet


def _extract_wide(rows, header_label="TIME"):
    header_idx = next(i for i, row in enumerate(rows) if row and row[0] == header_label)
    years = []
    year_cols = []
    for idx, value in enumerate(rows[header_idx]):
        if isinstance(value, int) and 2000 <= value <= 2100:
            years.append(value)
            year_cols.append(idx)
        elif isinstance(value, str) and value.isdigit() and 2000 <= int(value) <= 2100:
            years.append(int(value))
            year_cols.append(idx)
    out = []
    for row in rows[header_idx + 2:]:
        if not row or not row[0] or row[0] in {"Special value", "Observation flags:"}:
            continue
        country = row[0]
        if country not in EU27 and country != "European Union - 27 countries (from 2020)":
            continue
        for year, col in zip(years, year_cols):
            value = row[col] if col < len(row) else None
            if isinstance(value, (int, float)):
                out.append({"country": country, "year": year, "value": float(value)})
    return out


def clean_circularity():
    rows = read_sheet(RAW / "env_ac_cur.xlsx", "Sheet 1")
    data = _extract_wide(rows)
    write_csv(PROCESSED / "circularity_long.csv", data, ["country", "year", "value"])
    return data


def clean_trade():
    rows = read_sheet(RAW / "cei_srm020.xlsx", "Sheet 1")
    data = _extract_wide(rows)
    write_csv(PROCESSED / "trade_long.csv", data, ["country", "year", "value"])
    return data


def clean_digital():
    summary = read_sheet(RAW / "isoc_e_dii.xlsx", "Summary")
    specs = []
    for row in summary:
        if len(row) >= 7 and isinstance(row[1], str) and row[1].startswith("Sheet "):
            specs.append({
                "sheet": row[1],
                "size_class": row[3],
                "indicator": row[5],
                "unit": row[6],
            })
    out = []
    for spec in specs:
        rows = read_sheet(RAW / "isoc_e_dii.xlsx", spec["sheet"])
        values = _extract_wide(rows)
        version = "v4" if "Version 4" in spec["indicator"] else "v3"
        if "at least basic" in spec["indicator"].lower():
            intensity = "basic_or_above"
        elif "very low" in spec["indicator"].lower():
            intensity = "very_low"
        elif "very high" in spec["indicator"].lower():
            intensity = "very_high"
        elif "high" in spec["indicator"].lower():
            intensity = "high"
        elif "low" in spec["indicator"].lower():
            intensity = "low"
        else:
            intensity = "other"
        size = {
            "From 10 to 49 persons employed": "small_10_49",
            "From 50 to 249 persons employed": "medium_50_249",
            "250 persons employed or more": "large_250_plus",
            "From 10 to 249 persons employed": "sme_10_249",
            "10 persons employed or more": "all_10_plus",
        }.get(spec["size_class"], spec["size_class"])
        for item in values:
            out.append({
                "country": item["country"],
                "year": item["year"],
                "value": item["value"],
                "size_class": size,
                "intensity": intensity,
                "version": version,
                "sheet": spec["sheet"],
            })
    write_csv(
        PROCESSED / "digital_intensity_long.csv",
        out,
        ["country", "year", "value", "size_class", "intensity", "version", "sheet"],
    )
    return out


def main():
    PROCESSED.mkdir(parents=True, exist_ok=True)
    circularity = clean_circularity()
    trade = clean_trade()
    digital = clean_digital()
    return circularity, trade, digital


if __name__ == "__main__":
    main()

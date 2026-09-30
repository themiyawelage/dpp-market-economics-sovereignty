import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

NS_MAIN = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
NS_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS_PKG = "http://schemas.openxmlformats.org/package/2006/relationships"


def _col_index(ref):
    letters = re.match(r"([A-Z]+)", ref).group(1)
    out = 0
    for char in letters:
        out = out * 26 + ord(char) - 64
    return out - 1


def _shared_strings(zf):
    if "xl/sharedStrings.xml" not in zf.namelist():
        return []
    root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    values = []
    for item in root.findall(f"{{{NS_MAIN}}}si"):
        text = "".join(node.text or "" for node in item.iter(f"{{{NS_MAIN}}}t"))
        values.append(text)
    return values


def _sheet_map(zf):
    wb = ET.fromstring(zf.read("xl/workbook.xml"))
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    targets = {
        rel.attrib["Id"]: rel.attrib["Target"]
        for rel in rels.findall(f"{{{NS_PKG}}}Relationship")
    }
    sheets = {}
    for sheet in wb.find(f"{{{NS_MAIN}}}sheets"):
        rid = sheet.attrib[f"{{{NS_REL}}}id"]
        target = targets[rid].lstrip("/")
        if not target.startswith("xl/"):
            target = "xl/" + target
        sheets[sheet.attrib["name"]] = target
    return sheets


def read_sheet(path, sheet_name):
    path = Path(path)
    with zipfile.ZipFile(path) as zf:
        shared = _shared_strings(zf)
        sheets = _sheet_map(zf)
        root = ET.fromstring(zf.read(sheets[sheet_name]))
        rows = []
        for row in root.findall(f".//{{{NS_MAIN}}}sheetData/{{{NS_MAIN}}}row"):
            values = {}
            max_col = -1
            for cell in row.findall(f"{{{NS_MAIN}}}c"):
                ref = cell.attrib["r"]
                idx = _col_index(ref)
                max_col = max(max_col, idx)
                cell_type = cell.attrib.get("t")
                value_node = cell.find(f"{{{NS_MAIN}}}v")
                inline = cell.find(f"{{{NS_MAIN}}}is")
                value = None
                if inline is not None:
                    value = "".join(node.text or "" for node in inline.iter(f"{{{NS_MAIN}}}t"))
                elif value_node is not None:
                    raw = value_node.text
                    if cell_type == "s":
                        value = shared[int(raw)]
                    elif cell_type == "b":
                        value = raw == "1"
                    else:
                        try:
                            value = float(raw)
                            if value.is_integer():
                                value = int(value)
                        except (TypeError, ValueError):
                            value = raw
                values[idx] = value
            if max_col >= 0:
                rows.append([values.get(i) for i in range(max_col + 1)])
            else:
                rows.append([])
        width = max((len(row) for row in rows), default=0)
        return [row + [None] * (width - len(row)) for row in rows]


def sheet_names(path):
    with zipfile.ZipFile(path) as zf:
        return list(_sheet_map(zf))

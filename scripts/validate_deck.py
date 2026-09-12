#!/usr/bin/env python3
"""Read-only PPTX structural checks. Not a renderer or a full OOXML validator."""
import argparse
import json
import posixpath
import sys
import zipfile
from collections import Counter
from pathlib import Path
from urllib.parse import unquote
from xml.etree import ElementTree as ET

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}
EMU = 914400


def tag(prefix, name):
    return "{" + NS[prefix] + "}" + name


def rels_path(part):
    folder, name = posixpath.split(part)
    return posixpath.join(folder, "_rels", name + ".rels")


def target_path(part, target):
    value = unquote(target.split("#", 1)[0])
    if value.startswith("/"):
        return posixpath.normpath(value).lstrip("/")
    return posixpath.normpath(posixpath.join(posixpath.dirname(part), value))


def relations(part, roots):
    result = {}
    root = roots.get(rels_path(part))
    if root is not None:
        for rel in root:
            if rel.get("TargetMode") != "External":
                result[rel.get("Id")] = (rel.get("Type", ""), target_path(part, rel.get("Target", "")))
    return result


def linked(part, suffix, roots):
    return next((dest for kind, dest in relations(part, roots).values() if kind.endswith(suffix)), None)


def shapes(root):
    if root is None:
        return []
    tree = root.find("p:cSld/p:spTree", NS)
    if tree is None:
        return []
    return [e for e in tree if e.tag in {tag("p", n) for n in ("sp", "pic", "cxnSp", "graphicFrame", "grpSp")}]


def placeholder(shape):
    ph = shape.find(".//p:ph", NS)
    return int(ph.get("idx", "0")) if ph is not None else None


def geometry(shape):
    for path in ("p:spPr/a:xfrm", "p:xfrm"):
        xf = shape.find(path, NS)
        if xf is not None:
            off, ext = xf.find("a:off", NS), xf.find("a:ext", NS)
            if off is not None and ext is not None:
                return tuple(int(v) / EMU for v in (off.get("x"), off.get("y"), ext.get("cx"), ext.get("cy")))
    return None


def text(shape):
    return "".join(e.text or "" for e in shape.iter(tag("a", "t")))


def close_geometry(actual, expected):
    desired = tuple(expected[k] for k in ("x", "y", "w", "h"))
    return actual is not None and all(abs(a - b) <= 0.02 for a, b in zip(actual, desired))


def validate(path, structure_only=False):
    tokens = json.loads((Path(__file__).resolve().parents[1] / "assets" / "design-tokens.json").read_text(encoding="utf-8"))
    errors, warnings = [], []
    roots = {}
    with zipfile.ZipFile(path) as package:
        bad = package.testzip()
        if bad:
            errors.append("ZIP CRC failure: " + bad)
        names = set(package.namelist())
        for name in sorted(names):
            if name.endswith((".xml", ".rels")):
                try:
                    roots[name] = ET.fromstring(package.read(name))
                except ET.ParseError as exc:
                    errors.append("XML parse failure: " + name + ": " + str(exc))
    pres = roots.get("ppt/presentation.xml")
    if pres is None:
        raise ValueError("Missing or unreadable ppt/presentation.xml")
    for name, root in roots.items():
        if name.endswith(".rels"):
            if name == "_rels/.rels":
                base = ""
            else:
                folder, filename = posixpath.split(name)
                base = posixpath.join(posixpath.dirname(folder), filename[:-5])
            for rel in root:
                if rel.get("TargetMode") != "External":
                    dest = target_path(base, rel.get("Target", ""))
                    if dest not in names:
                        errors.append("Missing relationship target: " + name + " -> " + dest)
        for para in root.iter(tag("a", "p")):
            props = para.findall("a:pPr", NS)
            if len(props) > 1 or (props and list(para).index(props[0]) != 0):
                errors.append("Invalid paragraph property count/order: " + name)
        if name.startswith(("ppt/slides/", "ppt/slideLayouts/", "ppt/slideMasters/")) and name.endswith(".xml"):
            ids = [e.get("id") for e in root.iter(tag("p", "cNvPr"))]
            if len(ids) != len(set(ids)):
                errors.append("Duplicate shape IDs: " + name)
    dims = pres.find("p:sldSz", NS)
    width, height = int(dims.get("cx")) / EMU, int(dims.get("cy")) / EMU
    if not structure_only and (abs(width - tokens["slide"]["width"]) > 0.02 or abs(height - tokens["slide"]["height"]) > 0.02):
        errors.append("Slide size differs from the default 16:9 template")
    prs_rels = relations("ppt/presentation.xml", roots)
    order = []
    for item in pres.findall("p:sldIdLst/p:sldId", NS):
        pair = prs_rels.get(item.get(tag("r", "id")))
        if pair and pair[1] in roots:
            order.append(pair[1])
        else:
            errors.append("Unresolved slide relationship")
    fonts, types = Counter(), Counter()
    used_parts, footer_titles = set(order), set()
    notes_count = 0
    allowed_colors = set(tokens["colors"].values())
    for number, part in enumerate(order, 1):
        root = roots[part]
        layout_part = linked(part, "/slideLayout", roots)
        layout = roots.get(layout_part)
        if layout_part:
            used_parts.add(layout_part)
        master_part = linked(layout_part, "/slideMaster", roots) if layout_part else None
        master = roots.get(master_part)
        if master_part:
            used_parts.add(master_part)
        layout_ph = {placeholder(s): s for s in shapes(layout) if placeholder(s) is not None}
        slide_shapes = shapes(root)
        slide_ph = {placeholder(s): s for s in slide_shapes if placeholder(s) is not None}
        if not slide_shapes:
            warnings.append(f"Slide {number}: no local shapes")
        if linked(part, "/notesSlide", roots):
            notes_count += 1
        else:
            warnings.append(f"Slide {number}: no speaker notes; check source mapping")
        if not structure_only:
            expected = {12: tokens["footer"]["page_number"]}
            if 0 in slide_ph or 1 in slide_ph:
                expected.update({0: tokens["content_layout"]["title"], 1: tokens["content_layout"]["header"]})
            for idx, spec in expected.items():
                sh = slide_ph.get(idx)
                if sh is None:
                    errors.append(f"Slide {number}: missing default placeholder {idx}")
                    continue
                geo = geometry(sh)
                if geo is None and idx in layout_ph:
                    geo = geometry(layout_ph[idx])
                if not close_geometry(geo, spec):
                    errors.append(f"Slide {number}: placeholder {idx} geometry differs from shared default")
            page = slide_ph.get(12)
            if page is not None and text(page) != str(number):
                errors.append(f"Slide {number}: cached page number is {text(page)!r}")
            if page is not None and page.find(".//a:fld[@type='slidenum']", NS) is None:
                warnings.append(f"Slide {number}: page number is static text rather than a slidenum field")
            footers = [text(s) for s in shapes(master) if close_geometry(geometry(s), tokens["footer"]["document_title"])]
            if len(footers) != 1 or not footers[0].strip():
                warnings.append(f"Slide {number}: verify the one shared document-title Footer")
            else:
                footer_titles.add(footers[0])
        for sh in slide_shapes:
            kind = sh.tag.split("}")[-1]
            types[kind] += 1
            geo = geometry(sh)
            if geo is None and placeholder(sh) in layout_ph:
                geo = geometry(layout_ph[placeholder(sh)])
            if geo:
                x, y, w, h = geo
                if x < -0.02 or y < -0.02 or x + w > width + 0.02 or y + h > height + 0.02:
                    errors.append(f"Slide {number}: shape outside slide bounds")
                if kind == "pic" and w >= width * 0.9 and h >= height * 0.9:
                    warnings.append(f"Slide {number}: near-full-slide picture; verify editability")
            if kind == "grpSp":
                warnings.append(f"Slide {number}: grouped child coordinates need separate inspection")
        types["native_tables"] += len(root.findall(".//a:tbl", NS))
        visible = " ".join(text(s) for s in slide_shapes)
        if any(marker in visible for marker in ("예시 문구", "발표 전체 제목", "발표자 이름", "원고로 교체")):
            warnings.append(f"Slide {number}: generic template wording may remain")
    if len(footer_titles) > 1:
        errors.append("Document-title Footer differs across slide masters")
    for part in sorted(used_parts):
        root = roots.get(part)
        if root is None:
            continue
        for suffix in ("latin", "ea", "cs"):
            fonts.update(e.get("typeface", "") for e in root.iter(tag("a", suffix)))
        if not structure_only:
            unknown = {e.get("val", "").upper() for e in root.iter(tag("a", "srgbClr"))} - allowed_colors
            if unknown:
                warnings.append("Review colors outside default palette in " + part + ": " + ", ".join(sorted(unknown)))
    if not structure_only:
        for family in fonts:
            if family and not family.startswith(("+", "Pretendard")):
                warnings.append("Explicit font differs from Pretendard: " + family)
    return {
        "file": str(Path(path).resolve()), "mode": "structure-only" if structure_only else "default-design",
        "slides": len(order), "size_inches": [width, height], "shape_counts": dict(types),
        "notes_slides": notes_count, "explicit_fonts": dict(fonts),
        "errors": sorted(set(errors)), "warnings": sorted(set(warnings)),
        "visual_check": "NOT_PERFORMED",
        "limitations": ["No rendering, text-overflow, overlap or factual-source verification", "Not full OOXML schema validation", "Grouped child transforms and complete style inheritance are not fully checked"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--json", type=Path, dest="json_path")
    parser.add_argument("--structure-only", action="store_true")
    args = parser.parse_args()
    try:
        report = validate(args.pptx, args.structure_only)
    except (OSError, ValueError, zipfile.BadZipFile, KeyError, TypeError) as exc:
        report = {"errors": [str(exc)], "visual_check": "NOT_PERFORMED"}
    output = json.dumps(report, ensure_ascii=False, indent=2)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    print(output)
    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(output + "\n", encoding="utf-8")
    return 1 if report.get("errors") else 0


if __name__ == "__main__":
    raise SystemExit(main())

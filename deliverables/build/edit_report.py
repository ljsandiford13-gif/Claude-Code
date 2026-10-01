"""Edit HSFB_Report_Food_First.docx in place: refresh every number for the 36-item record,
anonymise store names, fix the exclusion paragraph, draft Section 8 and swap the chart images."""
import copy, json, re, sys
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

SRC, OUT, STATS, CHARTS = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
S = json.load(open(STATS)); O = S["overall"]; C = S["cats"]; A, B = S["storeA"], S["storeB"]
items = S["items"]
MINUS = "−"
def pct(x, d=1):
    return ("+" if x > 0 else MINUS if x < 0 else "") + f"{abs(x)*100:.{d}f}%"
def pp(x, d=1): return f"{x*100:.{d}f}%"     # plain, no sign
def money(x): return f"{x:.2f}"
by = {d["item"]: d for d in items}
mango, red_on, jal = by["Mangoes"], by["Red Onions"], by["Jalapeno Peppers"]
ffc = O["cheapest"]["Food First"]; n = O["n"]

doc = Document(SRC)
P = doc.paragraphs

# ---------------------------------------------------------------- helpers
def replace_in_par(p, old, new):
    full = "".join(r.text for r in p.runs)
    s = full.find(old)
    assert s >= 0, f"not found: {old[:60]!r}\n in: {full[:200]!r}"
    e = s + len(old); pos = 0; i0 = i1 = None
    starts = []
    for i, r in enumerate(p.runs):
        starts.append(pos); pos += len(r.text)
    for i, r in enumerate(p.runs):
        rs, re_ = starts[i], starts[i] + len(r.text)
        if i0 is None and re_ > s: i0 = i
        if rs < e: i1 = i
    r0, r1 = p.runs[i0], p.runs[i1]
    head = r0.text[: s - starts[i0]]
    tail = r1.text[e - starts[i1]:]
    r0.text = head + new + (tail if i0 == i1 else "")
    for i in range(i0 + 1, i1 + 1):
        p.runs[i].text = tail if i == i1 else ""
    if i0 != i1:
        p.runs[i1].text = tail

def set_par(p, text):
    """Replace a paragraph's whole text, keeping the first run's formatting."""
    p.runs[0].text = text
    for r in p.runs[1:]: r.text = ""

def set_cell(cell, text, fill=None):
    par = cell.paragraphs[0]
    if par.runs:
        par.runs[0].text = text
        for r in par.runs[1:]: r._r.getparent().remove(r._r)
    else:
        par.add_run(text)
    tcPr = cell._tc.get_or_add_tcPr()
    for shd in tcPr.findall(qn("w:shd")): tcPr.remove(shd)
    if fill:
        shd = OxmlElement("w:shd"); shd.set(qn("w:val"), "clear"); shd.set(qn("w:color"), "auto"); shd.set(qn("w:fill"), fill)
        after = [qn(f"w:{t}") for t in ("noWrap", "tcMar", "textDirection", "tcFitText", "vAlign", "hideMark", "headers", "cellIns", "cellDel", "cellMerge", "tcPrChange")]
        anchor = next((el for el in tcPr if el.tag in after), None)
        if anchor is not None: anchor.addprevious(shd)
        else: tcPr.append(shd)

PALE_BLUE, PALE_RED = "E3EEFB", "FBE3E3"
def fill_for(txt): return PALE_BLUE if txt.startswith(MINUS) else PALE_RED if txt.startswith("+") else None

R = []  # (paragraph index, old, new)
# ---------------------------------------------------------------- executive summary
R += [
 (9, "Of 42 items recorded, 38 could be compared on an identical price basis; four were excluded because the retailers price them on different bases.",
     f"Of the 95 products on Food First's price list, {n} could be compared on an identical price basis at all three stores; the rest were excluded because they were not available at the supermarkets or are priced on different bases (Section 3.3)."),
 (10, "28 of 38 items (74%). Supermarket A was cheapest for 6 items and Supermarket B for 4.",
      f"{ffc} of {n} items ({pp(ffc/n,0)}). {A} was cheapest for {O['cheapest'][A]} items and {B} for {O['cheapest'][B]}."),
 (11, "The median item was 20.3% cheaper at Food First than at Supermarket A and 22.7% cheaper than at Supermarket B. Means were −16.2% and −18.6%,",
      f"The median item was {pp(-O['medA'])} cheaper at Food First than at {A} and {pp(-O['medB'])} cheaper than at {B}. Means were {pct(O['meanA'])} and {pct(O['meanB'])},"),
 (12, "11 of 12 vegetables (median −40.3% vs Supermarket A, −36.1% vs Supermarket B) and on 5 of 7 grocery items (median −41.1% and −43.1%).",
      f"{C['Vegetables']['both']} of {C['Vegetables']['n']} vegetables (median {pct(C['Vegetables']['medA'])} vs {A}, {pct(C['Vegetables']['medB'])} vs {B}) and on {C['Grocery']['both']} of {C['Grocery']['n']} grocery items (median {pct(C['Grocery']['medA'])} and {pct(C['Grocery']['medB'])})."),
 (13, "Food First was cheaper on 12 of 19 fruit items but markedly dearer on Mangoes (+124% vs Supermarket A), Red Apples and Blueberries. Outside fruit, Cucumbers and Pepper Mash were also dearer at Food First.",
      f"Food First was cheaper on {C['Fruits']['both']} of {C['Fruits']['n']} fruit items but markedly dearer on Mangoes ({pct(mango['ff_a'],0)} vs {A}) and Red Apples, and modestly dearer on grapefruit, kiwis and sweet peppers against {A}. Outside fruit, Cucumbers were also dearer at Food First."),
 (14, "Summing the 38 standardised prices gives BBD 342.41 at Food First, BBD 411.68 at Supermarket A and BBD 432.03 at Supermarket B: −16.8% and −20.7% respectively.",
      f"Summing the {n} standardised prices gives BBD {money(O['sumFF'])} at Food First, BBD {money(O['sumA'])} at {A} and BBD {money(O['sumB'])} at {B}: {pct(O['basketA'])} and {pct(O['basketB'])} respectively."),
 (15, "Across the 38 items the mean difference between Supermarket A and Supermarket B was +0.1%; Supermarket A was cheaper on 25 items and Supermarket B on 12.",
      f"Across the {n} items the mean difference between {A} and {B} was {pct(O['meanAB'])}; {A} was cheaper on {O['ltAB']} items and {B} on {O['gtAB']}."),
 # background typo
 (18, "[1].This trend begins in childhood and can be said to be somewhat responsible for the high burden of Non- Communicable Diseases",
      "[1]. This trend begins in childhood and can be said to be somewhat responsible for the high burden of non-communicable diseases"),
 # materials / methods: anonymity and typos
 (27, "Popular's and Massy's", f"{A}'s and {B}'s"),
 (27, "Food First’s provided list of product.", "Food First’s provided list of products."),
 (31, "The price list for Food first was provided to the researched directly", "The price list for Food First was provided to the researcher directly"),
 (31, "Shelf prices at the Stores 1 and 2 were recorded", f"Shelf prices at {A} and {B} were recorded"),
 (31, "Prices provided by food First", "Prices provided by Food First"),
 (31, "prices obtained in stores 1 and 2 were also recorded using identical biases or where this was not availibe, prices were standardized",
      f"prices obtained in {A} and {B} were also recorded using identical bases or, where this was not available, prices were standardised"),
 (33, "for those specifies quantity", "for those specified quantities"),
 (36, "items with ambiguous pricing biases", "items with ambiguous pricing bases"),
 (36, "50 were excluded.", f"{95 - n} were excluded."),
 (36, "Brazilian  melons", "Brazilian melons"),
 (36, "pineapples, kiwi, pomegranate, pears, plums,", "pineapples, pomegranate, plums,"),
 (36, "fine frisse, green cabbage, chines cabbage", "fine frisée, green cabbage, Chinese cabbage"),
 (36, "whole chcken. The remaining 38 items", f"whole chicken. The remaining {n} items"),
 # results
 (45, "Supermarket A was cheaper on 25 items and Supermarket B on 12 (mean +0.1%, median −10.3%, negative = Supermarket A cheaper).",
      f"{A} was cheaper on {O['ltAB']} items and {B} on {O['gtAB']} (mean {pct(O['meanAB'])}, median {pct(O['medAB'])}, negative = {A} cheaper)."),
 (48, "(38 like-for-like items)", f"({n} like-for-like items)"),
 (60, "Summing the standardised prices of the 38 included items", f"Summing the standardised prices of the {n} included items"),
 (62, "Figure 3. Sum of standardised prices, 38 included items. Food First −16.8% vs Supermarket A and −20.7% vs Supermarket B.",
      f"Figure 3. Sum of standardised prices, {n} included items. Food First {pct(O['basketA'])} vs {A} and {pct(O['basketB'])} vs {B}."),
 (66, "Figure 4 ranks the 38 included items", f"Figure 4 ranks the {n} included items"),
 (66, "a short tail where Food First is clearly dearer: Pepper Mash, Cucumbers, Red Apples and Mangoes against both supermarkets, and Blueberries against Supermarket B.",
      "a short tail where Food First is clearly dearer: Cucumbers, Red Apples and Mangoes against both supermarkets."),
 (68, "for the 38 like-for-like items", f"for the {n} like-for-like items"),
 (77, " Excluded items are listed for completeness with no percentages.", ""),
 (78, "Blackberries, Red Currants, Pineapple and Baby Spinach are excluded because Food First and the supermarkets price them on different bases (see Section 3.3); their supermarket prices are shown on the supermarkets' own basis.",
      "Sweet peppers are listed by colour because Food First prices each colour separately; both supermarkets sell them at a single price regardless of colour."),
 # worked examples
 (89, "5.4 Basket total.", "5.3 Basket total."),
 (90, "Food First BBD 342.41, Supermarket A BBD 411.68: (342.41 − 411.68) ÷ 411.68 × 100 = −16.8%.",
      f"Food First BBD {money(O['sumFF'])}, {A} BBD {money(O['sumA'])}: ({money(O['sumFF'])} − {money(O['sumA'])}) ÷ {money(O['sumA'])} × 100 = {pct(O['basketA'])}."),
 (92, "5.5 Mean versus median.", "5.4 Mean versus median."),
 (92, "the mean difference is −16.2% but the median is −20.3%.", f"the mean difference is {pct(O['meanA'])} but the median is {pct(O['medA'])}."),
 # discussion
 (95, "for 74% of like-for-like items, was cheaper than Supermarket A on 29 of 38 items and cheaper than Supermarket B on 30, and its typical price sat a fifth to a quarter below both benchmarks (median −20.3% and −22.7%).",
      f"for {pp(ffc/n,0)} of like-for-like items, was cheaper than {A} on {O['ltA']} of {n} items and cheaper than {B} on {O['ltB']}, and its typical price sat about a quarter below both benchmarks (median {pct(O['medA'])} and {pct(O['medB'])})."),
 (96, "pepper mash was the only grocery item where Food First was clearly dearer.", "no grocery item was clearly dearer at Food First."),
 (97, "markedly dearer on mangoes, red apples and blueberries against both supermarkets", "markedly dearer on mangoes and red apples against both supermarkets"),
 # limitations
 (101, "The record contains 42 items, of which 38 were comparable; seasonings and herbs are absent because no supermarket prices were recorded for them.",
       f"Of the 95 products on Food First's list, {n} were comparable; seasonings, herbs, sauces and desserts are absent because no like-for-like supermarket prices were recorded for them."),
]
for idx, old, new in R:
    replace_in_par(P[idx], old, new)

# sanity: nothing left that refers to the old record
for i, p in enumerate(P):
    for bad in ("38 ", "Blueberr", "Pepper Mash", "Popular", "Massy", "Stores 1", "stores 1"):
        if bad in p.text and i not in (105,):
            print("WARNING leftover", repr(bad), "in paragraph", i, p.text[:80])

# ---------------------------------------------------------------- tables
T1, T2, T3 = doc.tables
t1 = [
    (str(n), str(n)), (str(O["ltA"]), str(O["ltB"])), (str(O["eqA"]), str(O["eqB"])), (str(O["gtA"]), str(O["gtB"])),
    (pp(O["ltA"]/n, 0), pp(O["ltB"]/n, 0)), (pct(O["meanA"]), pct(O["meanB"])), (pct(O["medA"]), pct(O["medB"])),
    (pct(O["minA"]), pct(O["minB"])), (pct(O["maxA"]), pct(O["maxB"])),
    (money(O["sumFF"]), money(O["sumFF"])), (money(O["sumA"]), money(O["sumB"])), (pct(O["basketA"]), pct(O["basketB"])),
]
for ri, (va, vb) in enumerate(t1, 1):
    row = T1.rows[ri]
    set_cell(row.cells[1], va, fill_for(va)); set_cell(row.cells[2], vb, fill_for(vb))

cats = ["Vegetables", "Fruits", "Grocery"]
for ri, cat in enumerate(cats + ["All"], 1):
    c = O if cat == "All" else C[cat]
    vals = [str(c["n"]), str(c["n"]), pct(c["meanA"]), pct(c["medA"]), pct(c["meanB"]), pct(c["medB"]), f"{c['both']} of {c['n']}"]
    for ci, v in enumerate(vals, 1):
        set_cell(T2.rows[ri].cells[ci], v, fill_for(v) if 3 <= ci <= 6 else None)

# item table: rebuild data rows from a template row
tmpl = copy.deepcopy(T3.rows[1]._tr)
for row in list(T3.rows[1:]):
    row._tr.getparent().remove(row._tr)
ordered = [d for cat in cats for d in sorted((x for x in items if x["cat"] == cat), key=lambda x: x["item"])]
from docx.table import _Row
for d in ordered:
    tr = copy.deepcopy(tmpl); T3._tbl.append(tr)
    row = _Row(tr, T3)
    vals = [d["cat"], d["item"], d["basis_label"], money(d["ff"]), money(d["a"]), money(d["b"]), pct(d["ff_a"]), pct(d["ff_b"]), d["cheapest"]]
    for ci, v in enumerate(vals):
        set_cell(row.cells[ci], v, fill_for(v) if ci in (6, 7) else None)
assert len(T3.rows) == n + 1

# ---------------------------------------------------------------- section 8
h = P[105]  # "To be completed" (Heading 1) -> becomes first body paragraph
body_tmpl = P[95]._p; bullet_tmpl = P[100]._p
def new_par_after(anchor, tmpl, text):
    el = copy.deepcopy(tmpl); anchor.addnext(el)
    from docx.text.paragraph import Paragraph
    p = Paragraph(el, anchor.getparent())
    set_par(p, text)
    return el
concl = (f"Across {n} verified, like-for-like items, Food First was the cheapest of the three retailers for {ffc} items ({pp(ffc/n,0)}) and was, on both a mean and a median basis, "
         f"meaningfully cheaper than either supermarket, with a typical saving of about a quarter (median {pct(O['medA'])} against {A} and {pct(O['medB'])} against {B}). "
         f"The research hypothesis (H₁) is supported. The advantage is broad-based across vegetables and grocery staples and weaker, or reversed, for a small group of fruit, "
         f"most of them tropical varieties that the supermarkets can source regionally.")
recs = [
    "Repeat the price survey at two or three further dates across the year, using the same workbook, to test whether the advantage holds across seasons and promotions.",
    "Record pack weights for the items Food First sells per unit or per punnet (for example lettuce, berries and pineapple) so that more of the 95 products can be brought into a like-for-like comparison.",
    "Build a household-weighted \"healthy basket\" of the vegetables and staples HSFB promotes, so the saving can be expressed as dollars per week for a typical family.",
    "Share the findings with parents, schools and policymakers as a concrete example that whole foods can be sourced affordably, while noting that price is only one barrier to healthier eating.",
]
# turn heading paragraph into a body paragraph by replacing it
new_body = copy.deepcopy(body_tmpl); h._p.addnext(new_body); h._p.getparent().remove(h._p)
from docx.text.paragraph import Paragraph
set_par(Paragraph(new_body, None), concl)
anchor = new_par_after(new_body, body_tmpl, "Recommended next steps:")
for t in recs:
    anchor = new_par_after(anchor, bullet_tmpl, t)

# ---------------------------------------------------------------- images
img_map = {"rId7": "chart_cheapest.png", "rId8": "chart_category.png", "rId9": "chart_basket.png", "rId10": "chart_items.png"}
for rid, fn in img_map.items():
    part = doc.part.related_parts[rid]
    part._blob = open(f"{CHARTS}/{fn}", "rb").read()

if "--strip-highlight" in sys.argv:
    body = doc.element.body
    n_h = 0
    for hl in body.iter(qn("w:highlight")):
        n_h += 1
    for hl in list(body.iter(qn("w:highlight"))):
        hl.getparent().remove(hl)
    print("removed highlight runs:", n_h)
doc.save(OUT)
print("saved", OUT)

import sys
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, NamedStyle
from openpyxl.utils import get_column_letter
from openpyxl.formatting.rule import CellIsRule, FormulaRule
from openpyxl.worksheet.formula import ArrayFormula
from openpyxl.chart import BarChart, Reference
from openpyxl.chart.label import DataLabelList
from openpyxl.chart.shapes import GraphicalProperties
from openpyxl.comments import Comment
from openpyxl.worksheet.datavalidation import DataValidation

from data import ROWS, STORE_A, STORE_B, CATEGORIES

OUT = sys.argv[1]

# ---------- palette ----------
NAVY = "184F95"      # header fill
BLUE = "2A78D6"      # Food First / cheaper
ORANGE = "EB6834"    # Supermarket A
AQUA = "1BAF7A"      # Supermarket B
RED = "E34948"       # dearer
INPUT_BLUE = "0000FF"
LIGHT_GREY = "F2F2F2"
MID_GREY = "D9D9D9"
PALE_BLUE = "E3EEFB"
PALE_RED = "FBE3E3"
PALE_YELLOW = "FFF7CC"

FONT = "Arial"
f_base = Font(name=FONT, size=10)
f_bold = Font(name=FONT, size=10, bold=True)
f_input = Font(name=FONT, size=10, color=INPUT_BLUE)
f_hdr = Font(name=FONT, size=10, bold=True, color="FFFFFF")
f_title = Font(name=FONT, size=16, bold=True, color=NAVY)
f_sub = Font(name=FONT, size=11, bold=True, color=NAVY)
f_note = Font(name=FONT, size=9, italic=True, color="595959")
f_kpi = Font(name=FONT, size=20, bold=True, color=NAVY)
fill_hdr = PatternFill("solid", fgColor=NAVY)
fill_grey = PatternFill("solid", fgColor=LIGHT_GREY)
fill_yellow = PatternFill("solid", fgColor=PALE_YELLOW)
fill_excl = PatternFill("solid", fgColor="EDEDED")
thin = Side(style="thin", color=MID_GREY)
border = Border(left=thin, right=thin, top=thin, bottom=thin)
center = Alignment(horizontal="center", vertical="center", wrap_text=True)
left = Alignment(horizontal="left", vertical="center", wrap_text=True)
right = Alignment(horizontal="right", vertical="center")

PCT = '0.0%;-0.0%;0.0%'
MONEY = '#,##0.00'

wb = Workbook()

# =====================================================================
# Sheet 1: Read Me
# =====================================================================
ws = wb.active
ws.title = "Read Me"
ws.sheet_view.showGridLines = False
ws.column_dimensions["A"].width = 26
ws.column_dimensions["B"].width = 110

ws["A1"] = "FOOD FIRST vs SUPERMARKET PRICE COMPARISON"
ws["A1"].font = f_title
ws["A2"] = "Standardised, like-for-like unit-price comparison of Food First against two Barbados supermarkets"
ws["A2"].font = f_note
ws.merge_cells("A1:B1"); ws.merge_cells("A2:B2")

readme = [
    ("Purpose", "Establish whether Food First's fresh-produce and grocery prices are, on balance, higher or lower than two established Barbados supermarkets, overall and by category, using like-for-like standardised unit prices."),
    ("Prepared for", "Heart & Stroke Foundation of Barbados (HSFB), in support of its work on healthier lifestyles, good nutrition and childhood-obesity prevention."),
    ("Store anonymity", f"Per HSFB's undertaking to the retailers, the supermarkets visited are not named. They appear throughout as '{STORE_A}' and '{STORE_B}'. Food First is named because it is the subject of the comparison."),
    ("Price basis", "Every comparison uses a standardised price on the same basis (BBD per kg, per litre, per unit, per head, per pack or per dozen). Standardised price = shelf price / pack quantity, and the pack quantity is shown beside every shelf price so each conversion can be checked."),
    ("Price difference", "% difference = Food First price / comparator price - 1.  Negative = Food First is cheaper.  Positive = Food First is more expensive.  The same formula is used for Supermarket A vs Supermarket B."),
    ("Included / excluded", "Column L on the Price Data tab marks each item Y (included) or N (excluded). Four items are excluded because Food First and the supermarkets price them on different bases (per punnet vs per kg, per kg vs per whole fruit, or unknown pack size). Excluded rows stay visible but drop out of every average, median, count, basket total and chart. Change the flag to Y once the source data is corrected and everything updates."),
    ("Excluded items", "Baby Spinach (pack sizes unknown / differ), Blackberries (Food First price not credible as per kg), Red Currants (per punnet vs per kg), Pineapple (per kg vs per whole fruit). Reasons are in column T of Price Data."),
    ("Assumptions", "Lemons and limes at Supermarket A are priced per kg; they are converted to per unit at an assumed 10 fruit per kg (blue input cells in column H). Strawberries: Food First 'unit' taken to be the same 1 lb pack the supermarkets sell. Pepper Mash: 26 oz = 0.7371 kg; 750 ml treated as 0.75 kg. Carrots: 1 lb = 0.4536 kg. Every assumption is also recorded in the note beside the item."),
    ("Mean vs median", "Both are reported. A few large gaps (for example Mangoes at +124%) pull the mean, so the median is the better guide to the typical item."),
    ("Cell colours", "Blue text = a recorded price, pack quantity or Y/N flag that may be edited.  Black text = formula, do not overwrite.  Grey rows = excluded from statistics.  Blue-shaded % = Food First cheaper; red-shaded % = Food First dearer."),
    ("Tabs", "Price Data (source record and item-level results)  |  Summary (headline results)  |  Category Analysis (results by food group)  |  Charts."),
    ("Data collection", "Prices were recorded by the HSFB intern during in-store visits over the holiday period as a single point-in-time snapshot. Promotions were not separated from list prices. Collection date should be recorded here: ____________"),
    ("Source record", "Rebuilt from 'Food_First_Comparison_Workbook_Completed_3.xlsx' (42 items). Every standardised price and % difference was independently recomputed in Python and matches this workbook's formulas."),
]
ws.page_setup.orientation = "portrait"; ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0
ws.sheet_properties.pageSetUpPr.fitToPage = True
r = 4
for k, v in readme:
    ws.cell(r, 1, k).font = f_bold
    ws.cell(r, 1).alignment = Alignment(vertical="top")
    ws.cell(r, 1).fill = fill_grey
    c = ws.cell(r, 2, v); c.font = f_base; c.alignment = left
    ws.row_dimensions[r].height = max(30, 15 * (len(v) // 105 + 1))
    r += 1

# =====================================================================
# Sheet 2: Price Data
# =====================================================================
pd = wb.create_sheet("Price Data")
pd.sheet_view.showGridLines = False
HDR_ROW = 4
FIRST = HDR_ROW + 1
LAST = FIRST + len(ROWS) - 1

pd["A1"] = "PRICE DATA AND ITEM-LEVEL RESULTS"; pd["A1"].font = f_title
pd["A2"] = ("All prices in BBD. Standardised price = shelf price / pack quantity. % difference = Food First / comparator - 1 "
            "(negative = Food First cheaper). Rows flagged N are excluded from all statistics.")
pd["A2"].font = f_note
pd.merge_cells("A1:T1"); pd.merge_cells("A2:T2")

# group header row 3
groups = [("A3:D3", "Item"), ("E3:E3", "Food First"), ("F3:H3", STORE_A), ("I3:K3", STORE_B),
          ("L3:L3", "Flag"), ("M3:O3", "% difference (standardised price)"), ("P3:P3", "Result"), ("Q3:S3", "Standardised price (BBD)"), ("T3:T3", "Notes")]
gfill = {"Food First": BLUE, STORE_A: ORANGE, STORE_B: AQUA}
for rng, label in groups:
    a = rng.split(":")[0]
    pd[a] = label
    pd[a].font = f_hdr; pd[a].alignment = center
    pd[a].fill = PatternFill("solid", fgColor=gfill.get(label, "3A3A3A"))
    if rng.split(":")[0] != rng.split(":")[1]:
        pd.merge_cells(rng)

headers = ["#", "Category", "Item", "Basis",
           "Price (BBD)",
           "Shelf price (BBD)", "Pack / unit sold", "Pack qty (basis units)",
           "Shelf price (BBD)", "Pack / unit sold", "Pack qty (basis units)",
           "Include? (Y/N)",
           f"Food First vs {STORE_A}", f"Food First vs {STORE_B}", f"{STORE_A} vs {STORE_B}",
           "Cheapest store",
           "Food First", STORE_A, STORE_B,
           "Note / assumption"]
for i, h in enumerate(headers, 1):
    c = pd.cell(HDR_ROW, i, h); c.font = f_hdr; c.fill = fill_hdr; c.alignment = center; c.border = border
pd.row_dimensions[HDR_ROW].height = 42
pd.row_dimensions[3].height = 20

widths = [5, 12, 26, 13, 11, 11, 24, 11, 11, 24, 11, 9, 13, 13, 13, 15, 11, 11, 11, 70]
for i, w in enumerate(widths, 1):
    pd.column_dimensions[get_column_letter(i)].width = w

for i, row in enumerate(ROWS):
    rr = FIRST + i
    cat, item, basis, ff, a_shelf, a_lbl, a_q, b_shelf, b_lbl, b_q, inc, note = row
    vals = [i + 1, cat, item, basis, ff, a_shelf, a_lbl, a_q, b_shelf, b_lbl, b_q, inc]
    for ci, v in enumerate(vals, 1):
        c = pd.cell(rr, ci, v); c.border = border; c.font = f_base
    for ci in (5, 6, 8, 9, 11, 12):
        pd.cell(rr, ci).font = f_input
    pd.cell(rr, 12).alignment = center
    for ci in (5, 6, 9): pd.cell(rr, ci).number_format = MONEY
    for ci in (8, 11): pd.cell(rr, ci).number_format = '0.####'
    pd.cell(rr, 1).alignment = center
    # standardised prices Q:S
    pd.cell(rr, 17, f"=E{rr}")
    pd.cell(rr, 18, f"=F{rr}/H{rr}")
    pd.cell(rr, 19, f"=I{rr}/K{rr}")
    # % differences M:O
    pd.cell(rr, 13, f'=IF($L{rr}="Y",Q{rr}/R{rr}-1,"")')
    pd.cell(rr, 14, f'=IF($L{rr}="Y",Q{rr}/S{rr}-1,"")')
    pd.cell(rr, 15, f'=IF($L{rr}="Y",R{rr}/S{rr}-1,"")')
    # cheapest store P
    pd.cell(rr, 16, f'=IF($L{rr}="Y",IF(Q{rr}<=MIN(R{rr},S{rr}),"Food First",IF(R{rr}<=S{rr},"{STORE_A}","{STORE_B}")),"Excluded")')
    for ci in range(13, 20):
        c = pd.cell(rr, ci); c.border = border; c.font = f_base
    for ci in (13, 14, 15): pd.cell(rr, ci).number_format = PCT; pd.cell(rr, ci).alignment = right
    for ci in (17, 18, 19): pd.cell(rr, ci).number_format = MONEY
    pd.cell(rr, 16).alignment = center
    c = pd.cell(rr, 20, note); c.font = f_note; c.alignment = left; c.border = border
    if inc == "N":
        for ci in range(1, 21):
            pd.cell(rr, ci).fill = fill_excl

# totals row
TOT = LAST + 2
pd.cell(TOT, 3, "Matched-basket total (included items only)").font = f_bold
pd.cell(TOT, 16, "Items included").font = f_bold
pd.cell(TOT, 12, f'=COUNTIF(L{FIRST}:L{LAST},"Y")').font = f_bold
pd.cell(TOT, 12).alignment = center
for ci, col in ((17, "Q"), (18, "R"), (19, "S")):
    c = pd.cell(TOT, ci, f'=SUMIFS({col}{FIRST}:{col}{LAST},$L${FIRST}:$L${LAST},"Y")')
    c.font = f_bold; c.number_format = MONEY; c.border = border; c.fill = fill_yellow
pd.cell(TOT, 20, "Sum of standardised prices for the included items: an indicative basket, not a real shopping list.").font = f_note

# conditional formatting on % columns
pd.conditional_formatting.add(f"M{FIRST}:O{LAST}", CellIsRule(operator="lessThan", formula=["0"], fill=PatternFill("solid", fgColor=PALE_BLUE)))
pd.conditional_formatting.add(f"M{FIRST}:O{LAST}", CellIsRule(operator="greaterThan", formula=["0"], fill=PatternFill("solid", fgColor=PALE_RED)))

dv = DataValidation(type="list", formula1='"Y,N"', allow_blank=False)
pd.add_data_validation(dv); dv.add(f"L{FIRST}:L{LAST}")
pd.freeze_panes = "E5"
pd.auto_filter.ref = f"A{HDR_ROW}:T{LAST}"
pd.print_title_rows = f"{HDR_ROW}:{HDR_ROW}"
pd.page_setup.orientation = "landscape"; pd.page_setup.fitToWidth = 1; pd.page_setup.fitToHeight = 0
pd.sheet_properties.pageSetUpPr.fitToPage = True

# legend under table
LEG = TOT + 2
pd.cell(LEG, 3, "Legend").font = f_bold
pd.cell(LEG + 1, 3, "Blue text = recorded input (editable).  Black = formula.  Grey row = excluded (flag N).  Blue-shaded % = Food First cheaper; red-shaded % = Food First dearer.").font = f_note
pd.cell(LEG + 2, 3, f"Cheapest store: lowest standardised price of the three; ties go to Food First, then {STORE_A}.").font = f_note

# named ranges (as strings) used by other sheets
R = lambda col: f"'Price Data'!${col}${FIRST}:${col}${LAST}"
CAT, INC, FFA, FFB, AB, CHEAP, Q, RR, S = R("B"), R("L"), R("M"), R("N"), R("O"), R("P"), R("Q"), R("R"), R("S")

# =====================================================================
# Sheet 3: Summary
# =====================================================================
sm = wb.create_sheet("Summary")
sm.sheet_view.showGridLines = False
for col, w in zip("ABCDEFG", (44, 16, 16, 16, 3, 30, 16)):
    sm.column_dimensions[col].width = w
sm["A1"] = "OVERALL COMPARISON SUMMARY"; sm["A1"].font = f_title
sm["A2"] = "All figures calculated from the Price Data tab, included items only (flag = Y). Negative % = Food First cheaper."
sm["A2"].font = f_note
sm.merge_cells("A1:G1"); sm.merge_cells("A2:G2")

# KPI tiles row 4-6
kpis = [
    ("Items compared", f'=COUNTIF({INC},"Y")', '0'),
    ("Food First cheapest of the three", f'=COUNTIFS({CHEAP},"Food First")&" of "&COUNTIF({INC},"Y")', '@'),
    (f"Median saving vs {STORE_A}", f"=MEDIAN({FFA})", PCT),
    (f"Median saving vs {STORE_B}", f"=MEDIAN({FFB})", PCT),
]
col = 1
for label, formula, fmt in kpis:
    c = sm.cell(4, col, label); c.font = f_note; c.alignment = center
    c = sm.cell(5, col, formula); c.font = f_kpi; c.alignment = center; c.number_format = fmt
    sm.cell(4, col).fill = fill_grey; sm.cell(5, col).fill = fill_grey
    col += 1 if col != 1 else 1
    if col == 5: col = 6
sm.row_dimensions[5].height = 34

# main table
T0 = 8
hdr = ["Metric", f"vs {STORE_A}", f"vs {STORE_B}", f"{STORE_A} vs {STORE_B}"]
for i, h in enumerate(hdr, 1):
    c = sm.cell(T0, i, h); c.font = f_hdr; c.fill = fill_hdr; c.alignment = center; c.border = border
rows_sm = [
    ("Items compared (like-for-like)", f'=COUNT({FFA})', f'=COUNT({FFB})', f'=COUNT({AB})', '0'),
    ("Food First cheaper (items)", f'=COUNTIF({FFA},"<0")', f'=COUNTIF({FFB},"<0")', f'=COUNTIF({AB},"<0")', '0'),
    ("Same price (items)", f'=COUNTIF({FFA},0)', f'=COUNTIF({FFB},0)', f'=COUNTIF({AB},0)', '0'),
    ("Food First more expensive (items)", f'=COUNTIF({FFA},">0")', f'=COUNTIF({FFB},">0")', f'=COUNTIF({AB},">0")', '0'),
    ("Share of items where Food First is cheaper", f'=B10/B9', f'=C10/C9', f'=D10/D9', PCT),
    ("Mean % difference", f'=AVERAGE({FFA})', f'=AVERAGE({FFB})', f'=AVERAGE({AB})', PCT),
    ("Median % difference", f'=MEDIAN({FFA})', f'=MEDIAN({FFB})', f'=MEDIAN({AB})', PCT),
    ("Largest saving for Food First (min %)", f'=MIN({FFA})', f'=MIN({FFB})', f'=MIN({AB})', PCT),
    ("Largest premium for Food First (max %)", f'=MAX({FFA})', f'=MAX({FFB})', f'=MAX({AB})', PCT),
]
for i, (label, b, c_, d, fmt) in enumerate(rows_sm):
    rr = T0 + 1 + i
    sm.cell(rr, 1, label).font = f_base
    for ci, f in ((2, b), (3, c_), (4, d)):
        cell = sm.cell(rr, ci, f); cell.number_format = fmt; cell.font = f_base; cell.alignment = right
    for ci in range(1, 5): sm.cell(rr, ci).border = border
sm.cell(T0 + 4, 1).font = f_note
note_r = T0 + 1 + len(rows_sm)
sm.cell(note_r, 1, f"In the third column, negative = {STORE_A} cheaper than {STORE_B}.").font = f_note

# cheapest store table
C0 = note_r + 2
for i, h in enumerate(["Cheapest of the three stores", "Items", "Share of items"], 1):
    c = sm.cell(C0, i, h); c.font = f_hdr; c.fill = fill_hdr; c.alignment = center; c.border = border
for i, store in enumerate(["Food First", STORE_A, STORE_B]):
    rr = C0 + 1 + i
    sm.cell(rr, 1, store).font = f_base
    sm.cell(rr, 2, f'=COUNTIF({CHEAP},A{rr})').number_format = '0'
    sm.cell(rr, 3, f'=B{rr}/COUNTIF({INC},"Y")').number_format = PCT
    for ci in range(1, 4): sm.cell(rr, ci).border = border; sm.cell(rr, ci).font = f_base
    sm.cell(rr, 2).alignment = right; sm.cell(rr, 3).alignment = right

# basket table
B0 = C0 + 6
for i, h in enumerate(["Matched basket (sum of standardised prices, included items)", "BBD", "vs Food First"], 1):
    c = sm.cell(B0, i, h); c.font = f_hdr; c.fill = fill_hdr; c.alignment = center; c.border = border
for i, (store, col) in enumerate([("Food First", "Q"), (STORE_A, "R"), (STORE_B, "S")]):
    rr = B0 + 1 + i
    sm.cell(rr, 1, store).font = f_base
    sm.cell(rr, 2, f"='Price Data'!{col}{TOT}").number_format = MONEY
    sm.cell(rr, 3, "" if i == 0 else f"=$B${B0+1}/B{rr}-1").number_format = PCT
    for ci in range(1, 4): sm.cell(rr, ci).border = border; sm.cell(rr, ci).font = f_base
    sm.cell(rr, 2).alignment = right; sm.cell(rr, 3).alignment = right
sm.cell(B0 + 4, 1, "Basket difference = Food First total / supermarket total - 1. Indicative only: an equal-weighted sum of unit prices, not a real weekly shop.").font = f_note

# reading guide
G0 = B0 + 6
sm.cell(G0, 1, "How to read this sheet").font = f_sub
guide = [
    "Mean and median are simple statistics of the item-level % differences; each item counts equally regardless of how much of it a household buys.",
    "The median is the better guide to a typical item because a few large gaps (e.g. Mangoes +124%) pull the mean.",
    "Excluded items (flag N on Price Data) are not in any figure here. Change a flag to Y and every number on this sheet updates.",
]
for i, g in enumerate(guide):
    c = sm.cell(G0 + 1 + i, 1, g); c.font = f_base; c.alignment = left
    sm.merge_cells(start_row=G0 + 1 + i, start_column=1, end_row=G0 + 1 + i, end_column=4)
    sm.row_dimensions[G0 + 1 + i].height = 28

# conditional format on % cells
for rng in (f"B{T0+6}:D{T0+9}", f"C{B0+2}:C{B0+3}"):
    sm.conditional_formatting.add(rng, CellIsRule(operator="lessThan", formula=["0"], fill=PatternFill("solid", fgColor=PALE_BLUE)))
    sm.conditional_formatting.add(rng, CellIsRule(operator="greaterThan", formula=["0"], fill=PatternFill("solid", fgColor=PALE_RED)))
sm.page_setup.orientation = "portrait"; sm.page_setup.fitToWidth = 1; sm.page_setup.fitToHeight = 0
sm.sheet_properties.pageSetUpPr.fitToPage = True

# =====================================================================
# Sheet 4: Category Analysis
# =====================================================================
ca = wb.create_sheet("Category Analysis")
ca.sheet_view.showGridLines = False
ca["A1"] = "RESULTS BY FOOD CATEGORY"; ca["A1"].font = f_title
ca["A2"] = "Included items only. Negative % = Food First cheaper. Category labels follow the source record (tomatoes, peppers and jalapenos are listed under Fruits; local onions under Grocery)."
ca["A2"].font = f_note
ca.merge_cells("A1:L1"); ca.merge_cells("A2:L2")
H0 = 4
hdrs = ["Category", "Items listed", "Items compared",
        f"Mean: FF vs {STORE_A}", f"Median: FF vs {STORE_A}",
        f"Mean: FF vs {STORE_B}", f"Median: FF vs {STORE_B}",
        f"Mean: {STORE_A} vs {STORE_B}",
        f"FF cheaper vs {STORE_A} (items)", f"FF cheaper vs {STORE_B} (items)", "FF cheaper than both (items)", "FF cheapest of three (items)"]
for i, h in enumerate(hdrs, 1):
    c = ca.cell(H0, i, h); c.font = f_hdr; c.fill = fill_hdr; c.alignment = center; c.border = border
ca.row_dimensions[H0].height = 44
for col, w in zip("ABCDEFGHIJKL", (16, 24, 11, 13, 13, 13, 13, 13, 14, 14, 14, 14)):
    ca.column_dimensions[col].width = w

def med_if(col_rng, crit_cell):
    # array formula: median of a column restricted to one category
    return f"=MEDIAN(IF({CAT}={crit_cell},{col_rng}))"

for i, cat in enumerate(CATEGORIES + ["All categories"]):
    rr = H0 + 1 + i
    is_all = cat == "All categories"
    ca.cell(rr, 1, cat).font = f_bold if is_all else f_base
    if is_all:
        f = [f'=COUNTA({CAT})', f'=COUNT({FFA})',
             f'=AVERAGE({FFA})', f'=MEDIAN({FFA})', f'=AVERAGE({FFB})', f'=MEDIAN({FFB})', f'=AVERAGE({AB})',
             f'=COUNTIF({FFA},"<0")', f'=COUNTIF({FFB},"<0")',
             f'=SUMPRODUCT(({FFA}<>"")*({FFA}<0)*({FFB}<0))',
             f'=COUNTIF({CHEAP},"Food First")']
    else:
        f = [f'=COUNTIF({CAT},$A{rr})', f'=COUNTIFS({CAT},$A{rr},{INC},"Y")',
             f'=IFERROR(AVERAGEIFS({FFA},{CAT},$A{rr}),"")', None,
             f'=IFERROR(AVERAGEIFS({FFB},{CAT},$A{rr}),"")', None,
             f'=IFERROR(AVERAGEIFS({AB},{CAT},$A{rr}),"")',
             f'=COUNTIFS({CAT},$A{rr},{FFA},"<0")', f'=COUNTIFS({CAT},$A{rr},{FFB},"<0")',
             f'=SUMPRODUCT(({CAT}=$A{rr})*({FFA}<>"")*({FFA}<0)*({FFB}<0))',
             f'=COUNTIFS({CAT},$A{rr},{CHEAP},"Food First")']
    for ci, formula in enumerate(f, 2):
        cell = ca.cell(rr, ci)
        if formula is None:
            src = FFA if ci == 5 else FFB
            ref = f"{get_column_letter(ci)}{rr}"
            ca[ref] = ArrayFormula(ref, med_if(src, f"$A{rr}"))
        else:
            cell.value = formula
        cell.font = f_bold if is_all else f_base
        cell.alignment = right
        cell.number_format = PCT if ci in (4, 5, 6, 7, 8) else '0'
    for ci in range(1, 13):
        ca.cell(rr, ci).border = border
        if is_all: ca.cell(rr, ci).fill = fill_grey
CA_LAST = H0 + 4
ca.conditional_formatting.add(f"D{H0+1}:H{CA_LAST}", CellIsRule(operator="lessThan", formula=["0"], fill=PatternFill("solid", fgColor=PALE_BLUE)))
ca.conditional_formatting.add(f"D{H0+1}:H{CA_LAST}", CellIsRule(operator="greaterThan", formula=["0"], fill=PatternFill("solid", fgColor=PALE_RED)))
ca.cell(CA_LAST + 2, 1, "Seasonings / herbs: no items could be compared because no supermarket prices were recorded for that category. It is therefore not shown.").font = f_note
ca.cell(CA_LAST + 3, 1, f"Medians by category use an array formula (MEDIAN(IF(...))). 'Mean: {STORE_A} vs {STORE_B}' negative = {STORE_A} cheaper.").font = f_note

# helper block for item-level charts (one block per category, sorted by FF vs A)
ca.cell(CA_LAST + 5, 1, "Chart data (item level, included items only; feeds the Charts tab)").font = f_sub
CH0 = CA_LAST + 6
for i, h in enumerate(["Category", "Item", f"FF vs {STORE_A}", f"FF vs {STORE_B}"], 1):
    c = ca.cell(CH0, i, h); c.font = f_hdr; c.fill = fill_hdr; c.alignment = center; c.border = border
chart_blocks = {}
rr = CH0 + 1
for cat in CATEGORIES:
    start = rr
    for idx, row in enumerate(ROWS):
        if row[0] != cat or row[10] != "Y":
            continue
        src = FIRST + idx
        ca.cell(rr, 1, f"='Price Data'!B{src}")
        ca.cell(rr, 2, f"='Price Data'!C{src}")
        ca.cell(rr, 3, f"='Price Data'!M{src}").number_format = PCT
        ca.cell(rr, 4, f"='Price Data'!N{src}").number_format = PCT
        for ci in range(1, 5): ca.cell(rr, ci).border = border; ca.cell(rr, ci).font = f_base
        rr += 1
    chart_blocks[cat] = (start, rr - 1)
ca.page_setup.orientation = "landscape"; ca.page_setup.fitToWidth = 1; ca.page_setup.fitToHeight = 0
ca.sheet_properties.pageSetUpPr.fitToPage = True

# =====================================================================
# Sheet 5: Charts
# =====================================================================
ch = wb.create_sheet("Charts")
ch.sheet_view.showGridLines = False
ch["A1"] = "CHARTS"; ch["A1"].font = f_title
ch["A2"] = "Bars below zero = Food First cheaper; above zero = Food First more expensive. Charts read live from the Price Data and Category Analysis tabs."
ch["A2"].font = f_note

def vals_only(fmt):
    dl = DataLabelList()
    dl.showVal = True; dl.showSerName = False; dl.showCatName = False
    dl.showLegendKey = False; dl.showPercent = False; dl.showLeaderLines = False
    dl.numFmt = fmt
    return dl

def style_series(s, hex_color):
    s.graphicalProperties = GraphicalProperties(solidFill=hex_color)
    s.graphicalProperties.line.solidFill = hex_color

def base_chart(title, ytitle, horizontal=False):
    c = BarChart()
    c.type = "bar" if horizontal else "col"
    c.grouping = "clustered"
    c.title = title
    c.y_axis.title = ytitle
    c.y_axis.number_format = '0%'
    c.y_axis.majorGridlines.spPr = GraphicalProperties(ln=None)
    c.legend.position = "b"
    c.gapWidth = 60
    c.overlap = -10
    c.style = 10
    c.x_axis.delete = False; c.y_axis.delete = False
    return c

# Chart 1: mean by category
c1 = base_chart("Mean price difference by category (Food First vs each supermarket)", "% difference")
data = Reference(ca, min_col=4, max_col=6, min_row=H0, max_row=CA_LAST)  # D (mean A), E (median A), F (mean B) -> pick D and F
# openpyxl adds each column as a series; build explicitly
from openpyxl.chart import Series
cats = Reference(ca, min_col=1, min_row=H0 + 1, max_row=CA_LAST)
sA = Series(Reference(ca, min_col=4, min_row=H0, max_row=CA_LAST), title_from_data=True)
sB = Series(Reference(ca, min_col=6, min_row=H0, max_row=CA_LAST), title_from_data=True)
c1.series.append(sA); c1.series.append(sB)
c1.set_categories(cats)
style_series(sA, ORANGE); style_series(sB, AQUA)
c1.dataLabels = vals_only('0%')
c1.height = 9; c1.width = 20
ch.add_chart(c1, "A4")

# Chart 2: median by category
c2 = base_chart("Median price difference by category (Food First vs each supermarket)", "% difference")
sA2 = Series(Reference(ca, min_col=5, min_row=H0, max_row=CA_LAST), title_from_data=True)
sB2 = Series(Reference(ca, min_col=7, min_row=H0, max_row=CA_LAST), title_from_data=True)
c2.series.append(sA2); c2.series.append(sB2); c2.set_categories(cats)
style_series(sA2, ORANGE); style_series(sB2, AQUA)
c2.dataLabels = vals_only('0%')
c2.height = 9; c2.width = 20
ch.add_chart(c2, "A23")

# Chart 3: cheapest store count (single series)
c3 = BarChart(); c3.type = "col"; c3.title = "Number of items where each store is cheapest"
c3.y_axis.title = "Items"; c3.legend = None; c3.style = 10; c3.gapWidth = 80
c3.y_axis.majorGridlines.spPr = GraphicalProperties(ln=None)
c3.x_axis.delete = False; c3.y_axis.delete = False
s3 = Series(Reference(sm, min_col=2, min_row=C0 + 1, max_row=C0 + 3), title="Items")
c3.series.append(s3); c3.set_categories(Reference(sm, min_col=1, min_row=C0 + 1, max_row=C0 + 3))
style_series(s3, BLUE)
c3.dataLabels = vals_only('0')
c3.height = 8; c3.width = 14
ch.add_chart(c3, "A42")

# Charts 4-6: item level per category (horizontal)
anchor_row = 60
for cat in CATEGORIES:
    a, b = chart_blocks[cat]
    c = base_chart(f"{cat}: Food First price relative to each supermarket (item level)", "% difference", horizontal=True)
    sA_ = Series(Reference(ca, min_col=3, min_row=CH0, max_row=b) if False else Reference(ca, min_col=3, min_row=a, max_row=b), title=f"FF vs {STORE_A}")
    sB_ = Series(Reference(ca, min_col=4, min_row=a, max_row=b), title=f"FF vs {STORE_B}")
    c.series.append(sA_); c.series.append(sB_)
    c.set_categories(Reference(ca, min_col=2, min_row=a, max_row=b))
    style_series(sA_, ORANGE); style_series(sB_, AQUA)
    c.x_axis.scaling.orientation = "maxMin"  # first item at top
    c.x_axis.tickLblPos = "low"
    c.y_axis.crosses = "max"
    n = b - a + 1
    c.height = max(7, 0.6 * n + 3); c.width = 24
    ch.add_chart(c, f"A{anchor_row}")
    anchor_row += int(c.height * 2) + 2

ch.page_setup.orientation = "portrait"; ch.page_setup.fitToWidth = 1; ch.page_setup.fitToHeight = 0
ch.sheet_properties.pageSetUpPr.fitToPage = True

# sheet order & tab colours
wb["Read Me"].sheet_properties.tabColor = "3A3A3A"
pd.sheet_properties.tabColor = BLUE
sm.sheet_properties.tabColor = NAVY
ca.sheet_properties.tabColor = ORANGE
ch.sheet_properties.tabColor = AQUA

wb.save(OUT)
print("saved", OUT, "rows", FIRST, LAST, "TOT", TOT, "C0", C0, "B0", B0, "chart_blocks", chart_blocks)

"""Clean source record for the Food First price comparison.

Every price is the value recorded in Workbook 3 (the source record). Pack
quantities are expressed in the item's basis unit so that
standardised price = shelf price / pack quantity.
"""

# (category, item, basis, ff_price,
#  A_shelf, A_pack_label, A_qty,
#  B_shelf, B_pack_label, B_qty,
#  include, note)
ROWS = [
    # ---------------- Vegetables ----------------
    ("Vegetables", "Broccoli", "per kg", 14.00, 14.99, "per kg", 1, 15.99, "per kg", 1, "Y", ""),
    ("Vegetables", "Cauliflower", "per kg", 11.40, 14.99, "per kg", 1, 17.99, "per kg", 1, "Y", ""),
    ("Vegetables", "Romaine Lettuce", "per head", 5.00, 7.99, "1 head (approx. 0.3 kg)", 1, 5.79, "1 head (approx. 0.2 kg)", 1, "Y",
     "Compared per head. Supermarket heads differ in recorded weight (0.3 kg vs 0.2 kg); Food First head weight not recorded."),
    ("Vegetables", "Iceberg Lettuce", "per head", 4.50, 5.99, "1 head", 1, 6.99, "1 head", 1, "Y", ""),
    ("Vegetables", "Local Cabbage", "per kg", 3.50, 6.59, "per kg", 1, 7.89, "per kg", 1, "Y", ""),
    ("Vegetables", "Pumpkin", "per kg", 2.00, 3.52, "per kg", 1, 5.29, "per kg", 1, "Y", ""),
    ("Vegetables", "Red Cabbage", "per kg", 5.00, 9.99, "per kg", 1, 9.99, "per kg", 1, "Y", ""),
    ("Vegetables", "Red Onions", "per kg", 6.70, 11.88, "per kg", 1, 17.85, "per kg", 1, "Y", ""),
    ("Vegetables", "English Potatoes (Medium)", "per kg", 2.00, 2.25, "per kg", 1, 2.59, "per kg", 1, "Y", ""),
    ("Vegetables", "Cucumbers", "per kg", 8.44, 5.49, "per kg", 1, 5.29, "per kg", 1, "Y", ""),
    ("Vegetables", "Zucchini", "per kg", 5.00, 10.99, "per kg", 1, 14.69, "per kg", 1, "Y", ""),
    ("Vegetables", "Carrots", "per kg", 6.50, 13.82, "per kg", 1, 3.89, "1 lb pack (0.4536 kg)", 0.4536, "Y",
     "Supermarket B sold by the pound; converted at 1 lb = 0.4536 kg."),
    ("Vegetables", "Baby Spinach", "per pack", 16.85, 13.75, "142 g pack", 1, 10.99, "283 g pack", 1, "N",
     "EXCLUDED: Food First pack size not recorded and supermarket packs differ (142 g vs 283 g), so no like-for-like basis exists."),
    # ---------------- Fruits ----------------
    ("Fruits", "Tomatoes", "per kg", 14.30, 15.99, "per kg", 1, 14.99, "per kg", 1, "Y", ""),
    ("Fruits", "Red Apples", "per unit", 1.00, 0.599, "each", 1, 0.69, "each", 1, "Y", ""),
    ("Fruits", "Green Apples", "per unit", 1.20, 1.99, "each", 1, 1.49, "each", 1, "Y", ""),
    ("Fruits", "Oranges", "per unit", 1.00, 1.49, "each", 1, 1.59, "each", 1, "Y", ""),
    ("Fruits", "Red Seedless Grapes", "per kg", 16.70, 16.99, "per kg", 1, 18.99, "per kg", 1, "Y", ""),
    ("Fruits", "Green Seedless Grapes", "per kg", 16.70, 16.88, "per kg", 1, 20.59, "per kg", 1, "Y", ""),
    ("Fruits", "Strawberries", "per 1 lb pack", 12.88, 12.99, "1 lb pack", 1, 18.49, "1 lb pack", 1, "Y",
     "Food First 'unit' assumed to be the same 1 lb pack sold by both supermarkets."),
    ("Fruits", "Blackberries", "per kg", 16.65, 10.99, "170 g pack", 0.17, 11.99, "170 g pack", 0.17, "N",
     "EXCLUDED: Food First 16.65/kg is not credible against 64.65 and 70.53/kg at the supermarkets; most likely a per-punnet price recorded as per kg. Re-check at source before use."),
    ("Fruits", "Blueberries", "per kg", 63.80, 9.99, "170 g pack", 0.17, 10.99, "12 oz pack (0.3402 kg)", 0.3402, "Y",
     "Both supermarket packs converted to per kg."),
    ("Fruits", "Red Currants", "per punnet", 8.88, 26.99, "per kg", 1, 29.05, "per kg", 1, "N",
     "EXCLUDED: Food First priced per punnet (weight not recorded); supermarkets priced per kg."),
    ("Fruits", "Dragonfruit", "per unit", 10.00, 10.99, "each", 1, 15.99, "each", 1, "Y", ""),
    ("Fruits", "Pears", "per unit", 0.90, 2.99, "each", 1, 1.49, "each", 1, "Y", ""),
    ("Fruits", "Kiwis", "per unit", 1.99, 1.69, "each", 1, 1.99, "each", 1, "Y", ""),
    ("Fruits", "Lemons", "per unit", 1.00, 11.99, "per kg (approx. 10 lemons)", 10, 1.29, "each", 1, "Y",
     "Supermarket A priced per kg; converted to per lemon at an assumed 10 lemons per kg."),
    ("Fruits", "Limes", "per unit", 0.90, 9.68, "per kg (approx. 10 limes)", 10, 0.79, "each", 1, "Y",
     "Supermarket A priced per kg; converted at an assumed 10 limes per kg. Supermarket B recorded shelf price of 0.79 per lime used; the earlier 0.74 figure had no documented basis."),
    ("Fruits", "Jalapeno Peppers", "per kg", 15.50, 28.20, "per kg", 1, 12.69, "340 g pack", 0.34, "Y",
     "Supermarket B 340 g pack converted to per kg."),
    ("Fruits", "Sweet Pepper", "per kg", 18.50, 17.99, "per kg", 1, 19.99, "per kg", 1, "Y", ""),
    ("Fruits", "Grapefruit", "per unit", 3.30, 2.99, "each", 1, 3.29, "each", 1, "Y", ""),
    ("Fruits", "Pineapple", "per kg", 8.70, 5.99, "per whole fruit", 1, 7.99, "per whole fruit", 1, "N",
     "EXCLUDED: Food First priced per kg; supermarkets priced per whole pineapple with no weight recorded."),
    ("Fruits", "Gala Apple", "per unit", 0.50, 1.99, "each", 1, 1.45, "each", 1, "Y", ""),
    ("Fruits", "Mangoes", "per kg", 13.80, 6.16, "per kg", 1, 7.36, "per kg", 1, "Y", ""),
    ("Fruits", "Watermelon", "per kg", 4.50, 6.99, "per kg", 1, 5.29, "per kg", 1, "Y", ""),
    # ---------------- Grocery ----------------
    ("Grocery", "Cooking Cream", "per litre", 15.00, 25.99, "1 L", 1, 30.65, "1 L", 1, "Y", ""),
    ("Grocery", "Whipping Cream", "per litre", 15.00, 25.99, "1 L", 1, 31.45, "1 L", 1, "Y", ""),
    ("Grocery", "Oat Milk", "per litre", 8.50, 8.45, "1 L", 1, 10.99, "1 L", 1, "Y", ""),
    ("Grocery", "Whole Milk", "per litre", 5.00, 8.49, "1 L", 1, 8.79, "1 L", 1, "Y", ""),
    ("Grocery", "Eggs", "per dozen", 9.00, 9.35, "dozen", 1, 9.25, "dozen", 1, "Y", ""),
    ("Grocery", "Pepper Mash", "per kg", 15.40, 9.99, "26 oz jar (0.7371 kg)", 0.7371, 9.45, "750 ml bottle (0.75 kg)", 0.75, "Y",
     "Supermarket A 26 oz jar converted at 0.7371 kg. Supermarket B 750 ml treated as 0.75 kg (sauce density taken as 1); its 2 L size gives the same 12.60/kg."),
    ("Grocery", "Local Onions", "per kg", 2.00, 3.52, "per kg", 1, 3.99, "per kg", 1, "Y", ""),
]

STORE_A = "Supermarket A"
STORE_B = "Supermarket B"
CATEGORIES = ["Vegetables", "Fruits", "Grocery"]


def computed():
    """Return list of dicts with standardised prices and % differences (Python check values)."""
    out = []
    for i, r in enumerate(ROWS, 1):
        cat, item, basis, ff, a_shelf, a_lbl, a_q, b_shelf, b_lbl, b_q, inc, note = r
        a = a_shelf / a_q
        b = b_shelf / b_q
        d = dict(n=i, cat=cat, item=item, basis=basis, ff=ff, a_shelf=a_shelf, a_lbl=a_lbl, a_q=a_q,
                 b_shelf=b_shelf, b_lbl=b_lbl, b_q=b_q, a=a, b=b, include=inc, note=note)
        if inc == "Y":
            d["ff_a"] = ff / a - 1
            d["ff_b"] = ff / b - 1
            d["a_b"] = a / b - 1
            m = min(ff, a, b)
            d["cheapest"] = "Food First" if ff == m else (STORE_A if a == m else STORE_B)
        out.append(d)
    return out

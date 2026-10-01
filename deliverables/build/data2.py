"""Final 36-item record, taken from Final_Draft_HSFB_Workbook.xlsx (Comparison Data).

Pineapple removed (Food First per kg vs supermarkets per whole fruit).
Sweet Pepper Red / Yellow percentages in the source were copies of the Green row and are
recomputed here. Standardised prices are the values recorded in the source workbook.
"""
STORE_A = "Supermarket A"   # Popular in the source
STORE_B = "Supermarket B"   # Massy in the source
CATEGORIES = ["Vegetables", "Fruits", "Grocery"]

# (category, item, ff_basis, ff_std, A_qty_label, A_unit, A_shelf, A_std, B_qty_label, B_unit, B_shelf, B_std, note)
ROWS = [
    ("Vegetables", "Broccoli", "kg", 14.00, "Kg", "BBD/kg", 14.99, 14.99, "Kg", "BBD/kg", 15.99, 15.99, ""),
    ("Vegetables", "Cauliflower", "kg", 11.40, "Kg", "BBD/kg", 14.99, 14.99, "Kg", "BBD/kg", 17.99, 17.99, ""),
    ("Vegetables", "Romaine Lettuce", "unit", 5.00, "1 head (0.3 kg)", "BBD/unit", 7.99, 7.99, "1 head (0.2 kg)", "BBD/unit", 5.79, 5.79, "Compared per head; recorded head weights differ."),
    ("Vegetables", "Iceberg Lettuce", "unit", 4.50, "1 head", "BBD/unit", 5.99, 5.99, "1 head", "BBD/unit", 6.99, 6.99, ""),
    ("Vegetables", "Local Cabbage", "kg", 3.50, "Kg", "BBD/kg", 6.59, 6.59, "Kg", "BBD/kg", 7.89, 7.89, ""),
    ("Vegetables", "Pumpkin", "kg", 2.00, "Kg", "BBD/kg", 3.52, 3.52, "Kg", "BBD/kg", 5.29, 5.29, ""),
    ("Vegetables", "Red Cabbage", "kg", 5.00, "Kg", "BBD/kg", 9.99, 9.99, "Kg", "BBD/kg", 9.99, 9.99, ""),
    ("Vegetables", "Red Onions", "kg", 6.70, "Kg", "BBD/kg", 11.88, 11.88, "Kg", "BBD/kg", 17.85, 17.85, ""),
    ("Vegetables", "English Potatoes (Medium)", "kg", 2.00, "Kg", "BBD/kg", 2.25, 2.25, "Kg", "BBD/kg", 2.59, 2.59, ""),
    ("Vegetables", "Cucumbers", "kg", 8.44, "Kg", "BBD/kg", 5.49, 5.49, "Kg", "BBD/kg", 5.29, 5.29, ""),
    ("Vegetables", "Zucchini", "kg", 5.00, "Kg", "BBD/kg", 10.99, 10.99, "Kg", "BBD/kg", 14.69, 14.69, ""),
    ("Vegetables", "Carrots", "kg", 6.50, "Kg", "BBD/kg", 13.82, 13.82, "1 lb", "BBD/kg", 3.89, 8.576, "1 lb = 0.4536 kg: 3.89 / 0.4536 = 8.576 per kg."),
    ("Fruits", "Tomatoes", "kg", 14.30, "Kg", "BBD/kg", 15.99, 15.99, "Kg", "BBD/kg", 14.99, 14.99, ""),
    ("Fruits", "Red Apples", "unit", 1.00, "unit", "BBD/unit", 0.599, 0.599, "unit", "BBD/unit", 0.69, 0.69, ""),
    ("Fruits", "Green Apples", "unit", 1.20, "unit", "BBD/unit", 1.99, 1.99, "unit", "BBD/unit", 1.49, 1.49, ""),
    ("Fruits", "Oranges", "unit", 1.00, "unit", "BBD/unit", 1.49, 1.49, "unit", "BBD/unit", 1.59, 1.59, ""),
    ("Fruits", "Red Seedless Grapes", "kg", 16.70, "Kg", "BBD/kg", 16.99, 16.99, "Kg", "BBD/kg", 18.99, 18.99, ""),
    ("Fruits", "Green Seedless Grapes", "kg", 16.70, "Kg", "BBD/kg", 16.88, 16.88, "Kg", "BBD/kg", 20.59, 20.59, ""),
    ("Fruits", "Strawberries", "unit", 12.88, "1 lb", "BBD/unit", 12.99, 12.99, "1 lb", "BBD/unit", 18.49, 18.49, "Food First unit taken as the same 1 lb pack."),
    ("Fruits", "Dragonfruit", "unit", 10.00, "unit", "BBD/unit", 10.99, 10.99, "unit", "BBD/unit", 15.99, 15.99, ""),
    ("Fruits", "Pears", "unit", 0.90, "unit", "BBD/unit", 2.99, 2.99, "unit", "BBD/unit", 1.49, 1.49, ""),
    ("Fruits", "Kiwis", "unit", 1.99, "unit", "BBD/unit", 1.69, 1.69, "unit", "BBD/unit", 1.99, 1.99, ""),
    ("Fruits", "Jalapeno Peppers", "kg", 15.50, "Kg", "BBD/kg", 28.20, 28.20, "340g", "BBD/kg", 12.69, 37.3235, "340 g = 0.34 kg: 12.69 / 0.34 = 37.32 per kg."),
    ("Fruits", "Sweet Pepper Green", "kg", 18.50, "Kg", "BBD/kg", 17.99, 17.99, "Kg", "BBD/kg", 19.99, 19.99, "Supermarkets sell sweet peppers at one price regardless of colour."),
    ("Fruits", "Sweet Pepper Red", "kg", 19.50, "Kg", "BBD/kg", 17.99, 17.99, "Kg", "BBD/kg", 19.99, 19.99, "Supermarkets sell sweet peppers at one price regardless of colour."),
    ("Fruits", "Sweet Pepper Yellow", "kg", 20.50, "Kg", "BBD/kg", 17.99, 17.99, "Kg", "BBD/kg", 19.99, 19.99, "Supermarkets sell sweet peppers at one price regardless of colour."),
    ("Fruits", "Grapefruit", "unit", 3.30, "unit", "BBD/unit", 2.99, 2.99, "unit", "BBD/unit", 3.29, 3.29, ""),
    ("Fruits", "Gala Apple", "unit", 0.50, "unit", "BBD/unit", 1.99, 1.99, "unit", "BBD/unit", 1.45, 1.45, ""),
    ("Fruits", "Mangoes", "kg", 13.80, "Kg", "BBD/kg", 6.16, 6.16, "Kg", "BBD/kg", 7.36, 7.36, ""),
    ("Fruits", "Watermelon", "kg", 4.50, "Kg", "BBD/kg", 6.99, 6.99, "Kg", "BBD/kg", 5.29, 5.29, ""),
    ("Grocery", "Cooking Cream", "litre", 15.00, "litre", "BBD/litre", 25.99, 25.99, "litre", "BBD/litre", 30.65, 30.65, ""),
    ("Grocery", "Whipping Cream", "litre", 15.00, "litre", "BBD/litre", 25.99, 25.99, "litre", "BBD/litre", 31.45, 31.45, ""),
    ("Grocery", "Oat Milk", "litre", 8.50, "litre", "BBD/litre", 8.45, 8.45, "litre", "BBD/litre", 10.99, 10.99, ""),
    ("Grocery", "Whole Milk", "litre", 5.00, "litre", "BBD/litre", 8.49, 8.49, "litre", "BBD/litre", 8.79, 8.79, ""),
    ("Grocery", "Eggs", "dozen", 9.00, "dozen", "BBD/dozen", 9.35, 9.35, "dozen", "BBD/dozen", 9.25, 9.25, ""),
    ("Grocery", "Local Onions", "kg", 2.00, "Kg", "BBD/kg", 3.52, 3.52, "Kg", "BBD/kg", 3.99, 3.99, ""),
]

BASIS_LABEL = {"kg": "per kg", "unit": "per unit", "litre": "per litre", "dozen": "per dozen"}


def computed():
    out = []
    for i, r in enumerate(ROWS, 1):
        cat, item, basis, ff, aq, au, ash, a, bq, bu, bsh, b, note = r
        d = dict(n=i, cat=cat, item=item, basis=basis, basis_label=BASIS_LABEL[basis], ff=ff, a=a, b=b,
                 a_shelf=ash, b_shelf=bsh, a_q=aq, b_q=bq, note=note)
        if item == "Romaine Lettuce" or item == "Iceberg Lettuce":
            d["basis_label"] = "per head"
        if item == "Strawberries":
            d["basis_label"] = "per 1 lb pack"
        d["ff_a"] = ff / a - 1
        d["ff_b"] = ff / b - 1
        d["a_b"] = a / b - 1
        m = min(ff, a, b)
        d["cheapest"] = "Food First" if ff == m else (STORE_A if a == m else STORE_B)
        out.append(d)
    return out

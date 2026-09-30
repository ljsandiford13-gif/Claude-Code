# Build scripts

Reproduces the two deliverables from the clean source record in `data.py`.

```bash
pip install openpyxl matplotlib            # docx (npm) and LibreOffice also required
python build_workbook.py ../Food_First_Price_Comparison_Workbook.xlsx
python <xlsx-skill>/scripts/recalc.py ../Food_First_Price_Comparison_Workbook.xlsx   # LibreOffice recalculation
python make_charts.py                      # writes charts/*.png next to the scripts
python -c "from data import *"             # stats.json is produced by the snippet in the session; see build_report.js
node build_report.js ../Food_First_Price_Comparison_Report.docx
```

`data.py` is the single source of truth: one tuple per item with shelf price, pack quantity,
include flag and note. Both the workbook and the report are generated from it.

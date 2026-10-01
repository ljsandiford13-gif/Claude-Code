# Build scripts

Reproduce both deliverables from the 36-item record in `data2.py`
(taken from `Final_Draft_HSFB_Workbook.xlsx`, Pineapple removed, sweet-pepper
percentages recomputed).

```bash
pip install openpyxl matplotlib python-docx     # LibreOffice is needed for recalculation
python build_workbook2.py ../Food_First_Price_Comparison_Workbook.xlsx
python <xlsx-skill>/scripts/recalc.py ../Food_First_Price_Comparison_Workbook.xlsx
python make_charts2.py                          # writes charts2/*.png
python edit_report.py HSFB_Report_Food_First.docx ../Food_First_Price_Comparison_Report.docx stats2.json charts2 --strip-highlight
```

`edit_report.py` edits the intern's Word report in place: it refreshes every
number, table and chart for the 36-item record, anonymises the store names,
corrects the exclusion paragraph, drafts Section 8 and (with
`--strip-highlight`) removes the yellow review highlighting. `stats2.json`
holds the statistics it reads.

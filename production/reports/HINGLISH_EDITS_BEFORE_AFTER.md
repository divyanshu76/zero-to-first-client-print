# Hinglish print-edition adaptations — before and after

All 10 passages flagged `author_review: true` in `source/print_edits.yaml` were reviewed against the original manuscript.
**Review result:** each one changes only what a physical book cannot do (click, download, spreadsheet cells, dropdowns) and keeps the author's sentence structure, Hinglish register and meaning. No passage was materially rewritten, and no prompt instruction text was touched (`validation/prompts_final_*.json`: all 141 prompt bodies identical to the original).

| ID | Where | Before (original manuscript) | After (paperback) | Why |
|---|---|---|---|---|
| FM-03 | How to use this book, item 5 (print only) | 5. References. Text में [1] जैसे numbers Sources section के references से link हैं। PDF में इन पर click कर सकते हैं। | 5. References. Text में [1] जैसे numbers book के अंत में दिए Appendix: Sources and Further Reading के references हैं। | Printed references cannot be clicked. Digital edition keeps the original sentence. |
| FM-04 | How to use this book, item 6 | 6. Bonus files. Editable templates (DOCX, XLSX), calculators (XLSX), prompts और directory के download links Download Your Resources page पर हैं। | 6. Bonus sections. 104 prompts (Bonus A), 20 templates (Bonus B), 7 calculator sheets (Bonus C) और resource directory (Bonus D) इसी book में हैं। Templates और calculators सीधे book में भरिए, या उसी format को अपनी notebook या spreadsheet में copy कर लीजिए। | Brief §4 — 'How to Use This Book' item 6 pointed to downloadable DOCX/XLSX files on the removed portal. Rewritten to describe what is actually printed in the book. |
| CH03-02 | Ch 3 workflow card, TOOL USE | Workbook की Project Pricing sheet में hours और rate डालिए; हर tier की minimum price वहाँ से देखिए। | Bonus C की Project Pricing sheet में hours और rate डालिए; हर tier की minimum price वहाँ से निकालिए। | Same workflow card, TOOL USE row: 'Workbook' (removed XLSX) → printed Bonus C sheet. 'देखिए' → 'निकालिए' because on paper the reader calculates the value. |
| CH10-03 | Ch 10 Lead tracking | Workbook में Client Acquisition Tracker तैयार है। | Bonus C की Client Tracker sheet इसी के लिए है। | Lead tracking paragraph pointed to the workbook's tracker; the printed equivalent is the Client Tracker sheet in Bonus C. |
| BB-01 | Bonus B introduction | हर template का editable version नीचे दिए गए link से download होता है। यहाँ printable version है। Example column या grey row सिर्फ़ fictional examples के लिए है। ये general formats हैं, legal या tax advice नहीं। सभी files एक साथ: Download Your Resources। | हर template यहाँ printable form में है: सीधे book में भरिए, या उसी format को अपनी notebook या spreadsheet में copy कर लीजिए। Example column या grey row सिर्फ़ fictional examples के लिए है। ये general formats हैं, legal या tax advice नहीं। | Bonus B introduction described downloadable editable versions and the removed resource page. |
| BB-03 | Template 07 instructions | Yellow cells भरिए; बाकी formula हैं। | Input rows भरिए; दोनों Result rows नीचे दिए formula से निकालिए। | Template 07 told the reader to fill 'yellow cells' of a spreadsheet. Rewritten for paper; the two result formulas printed with the template are the ones already used in Chapter 6 (25 h × 1.3 = 32.5 h × ₹412 + ₹1,500 = ₹14,890). |
| BB-04 | Template 17 instructions | Status dropdown से चुनिए। | Status इन्हीं values में से लिखिए: New, Contacted, Replied, Call booked, Proposal sent, Won, Lost, Do not contact। | Template 17 'Status dropdown' does not exist on paper. The allowed values are the ones Chapter 10 lists for lead tracking. |
| BB-05 | Templates 17, 18, 19 | पूरी tracker table Excel file में है, जिसमें कई rows, dropdowns और dates पहले से तैयार हैं। यहाँ एक record का format है। | पहले एक record का format (fictional example) है, फिर भरने के लिए blank tracker sheet। | Templates 17, 18, 19 said the full tracker is in an Excel file. The paperback prints a blank tracker sheet after the example record. |
| BB-06 | Template 20 | Spreadsheet में वही 30 rows पहले से भरी हैं, साथ में Done, Actual hours और Note columns हैं। | नीचे की planner sheet में वही 30 days हैं, साथ में Done, Actual hours और Note columns हैं। | Template 20 referred to spreadsheet rows. The paperback prints the 30-day planner sheet. |
| BC-01 | Bonus C introduction | Download: BUSINESS_CALCULATORS.xlsx. Yellow cells में अपने numbers डालिए। Purple cells formulas हैं। File में दी गई values सिर्फ़ examples हैं, कोई benchmark या income promise नहीं। | सातों calculator sheets नीचे printable form में हैं। Input lines में अपने numbers लिखिए और formula lines से result निकालिए। Sheets में दी गई values सिर्फ़ examples हैं, कोई benchmark या income promise नहीं। | Bonus C introduction described the removed XLSX workbook (yellow input cells, purple formula cells). The paperback prints all seven calculator sheets. |

## All other documented edits (not wording-sensitive)

| ID | Edition | Category | Change |
|---|---|---|---|
| FM-01 | both | resource-removal | Brief §4 — remove the two-page 'Download Your Resources' section (original pp. xi–xii, PDF pp. 11–12). |
| FM-02 | both | navigation | Brief §13 — the original Table of Contents carries A4 page numbers and the removed resource page; it is rebuilt from final pagination by the typesetter. |
| CH03-01 | both | resource-removal | Workflow card 'Three-package builder' TOOL row linked the removed BUSINESS_CALCULATORS.xlsx; now points to the printed calculator in Bonus C. |
| CH03-03 | both | resource-removal | Recommended tools list named the removed XLSX. |
| CH04-01 | both | resource-removal | Demand Scoring Calculator referred to the removed workbook; the same calculation is printed in Bonus C. |
| CH06-01 | both | resource-removal | Project example said the workbook calculates automatically; the printed Bonus C sheet shows the same calculation step by step. |
| CH06-02 | both | resource-removal | Prompt #C-G VERIFY note (not the prompt instruction) pointed to the removed workbook. |
| CH06-03 | both | resource-removal | Next-step assignment named the removed XLSX. |
| CH10-01 | both | resource-removal | 30-day plan, Day 8 Tools column: 'Workbook' → printed Bonus C. |
| CH10-02 | both | resource-removal | 30-day plan, Day 30 Tools column: 'Workbook' → printed Bonus C. |
| CH10-04 | both | resource-removal | Tools and official links named the removed XLSX and the removed Download Your Resources page. |
| CH10-05 | both | resource-removal | Practical exercise 2 referred to the workbook tracker. |
| BA-01 | both | resource-removal | Prompt #080 (Project profitability review) VERIFY note, not the prompt instruction: 'Workbook' → printed Profit sheet in Bonus C. |
| BB-02 | both | resource-removal | Remove the 'Download: NN_*.docx/.xlsx' link from all 20 template instruction lines (files are not part of the book). |
| BC-02 | both | resource-removal | Pointed to the removed 07_pricing_calculator.xlsx; its printed equivalent is Template 07 in Bonus B. |

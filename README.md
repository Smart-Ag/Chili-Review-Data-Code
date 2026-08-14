# Chili Harvesting and Cleaning Evolution — Code & Data

This repository contains the code and data for the paper:  
**"Engineering evolution of chili harvesting and cleaning: From mechanisation to perception–actuation integration"** (Biosystems Engineering).

---

## How to Run the Code

1. Ensure the raw patent data file `1.Raw_787_Patents.xlsx` is placed in the `Patent_Data/` folder.

2. Install dependencies (run this command in the **project root directory**):
   ```bash
   pip install -r requirements.txt
   ```

3. Run the scripts in numerical order from the `Code/` folder:
   ```bash
   python Code/1.TF-IDF_Extraction.py
   python Code/2.Assign_Dimension_Labels.py
   python Code/3.Patent_Dimension_Donut_Plot.py
   python Code/4.Patent_Dimension_Annual_Plot.py
   python Code/5.Jaccard_Similarity_Plot.py
   python Code/6.Data_Conversion_CiteSpace.py
   python Code/7.IPC_Frequency_Stat.py
   ```

4. All outputs (figures, reports, CNKI txt) will be generated in the `Patent_Data/` folder.

5. Use **CiteSpace** to analyze the exported files:
   - The script `6.Data_Conversion_CiteSpace.py` produces files suitable for CiteSpace.
   - Run CiteSpace separately on the WoS, CNKI, and patent data files (converted formats) to generate co‑occurrence, clustering, and burst‑detection visualizations.

---

## Note on `jieba` Version

Keyword extraction uses the `jieba` library. Different versions may produce minor differences in individual keyword frequencies due to dictionary updates.

The version used is recorded in `requirements.txt` (`jieba==0.42.1`). These small variations do not affect the overall trends or the paper's main conclusions.
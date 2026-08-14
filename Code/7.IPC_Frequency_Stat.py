#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script 7: IPC Classification Code Frequency Report
====================================================
Input : ../Patent_Data/1.Raw_787_Patents.xlsx  (raw IncoPat export; IPC column only exists here)
Output: ../Patent_Data/IPC_Frequency_Report.txt
Logic :
  1. Split semicolon-separated IPC codes into individual rows.
  2. Remove all spaces to merge duplicate codes (e.g. "B07B 1/42" -> "B07B1/42").
  3. Output top-10 high-frequency to console; save full list to text file.
"""

from pathlib import Path
import pandas as pd

# ===================== Path Configuration =====================
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "Patent_Data"
INPUT_FILE = DATA_DIR / "1.Raw_787_Patents.xlsx"
OUTPUT_TXT = DATA_DIR / "IPC_Frequency_Report.txt"


def generate_ipc_full_report(file_path, save_to_txt=True):
    """
    Generate IPC frequency report.
    - Prints only top-10 high-frequency codes to console.
    - Saves full frequency list (including top-10, bottom-20, and all others) to a text file.
    """
    try:
        # ---- 1. Detect IPC column ----
        df_raw = pd.read_excel(file_path, nrows=0)
        ipc_col = None
        for candidate in ["IPC", "IPC分类号", "ipc", "IPC分类"]:
            if candidate in df_raw.columns:
                ipc_col = candidate
                break
        if ipc_col is None:
            raise KeyError(f"IPC column not found. Available columns: {list(df_raw.columns)}")

        df = pd.read_excel(file_path, usecols=[ipc_col])
        print(f"Using IPC column: '{ipc_col}'")

        # ---- 2. Split and clean IPC codes ----
        df[ipc_col] = df[ipc_col].astype(str).str.split(";")
        ipc_series = df.explode(ipc_col)[ipc_col]
        ipc_series = ipc_series.str.replace(" ", "", regex=False).str.strip()
        ipc_series = ipc_series[ipc_series != ""].dropna()

        total_records = len(ipc_series)
        ipc_full_counts = ipc_series.value_counts()  # descending
        unique_ipc_count = len(ipc_full_counts)

        # ---- 3. Console output: only top 10 ----
        print("=" * 60)
        print("  IPC Classification Frequency Report (duplicates merged)")
        print(f"  Total records: {total_records} | Unique IPC codes: {unique_ipc_count}")
        print("=" * 60)

        print("\n[Top 10 most frequent IPC codes]")
        print(f"{'Rank':<5} {'IPC':<14} {'Count':<7} {'Share'}")
        print("-" * 42)
        for rank, (ipc, count) in enumerate(ipc_full_counts.head(10).items(), 1):
            share = count / total_records * 100
            print(f"{rank:<5} {ipc:<14} {count:<7} {share:.1f}%")

        # ---- 4. Save full report to file (including all codes) ----
        if save_to_txt:
            # Build full report lines
            full_lines = []
            for rank, (ipc, count) in enumerate(ipc_full_counts.items(), 1):
                share = count / total_records * 100
                full_lines.append(f"{rank:<5} {ipc:<14} {count:<7} {share:.1f}%")

            OUTPUT_TXT.parent.mkdir(parents=True, exist_ok=True)
            with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
                f.write("IPC Classification Frequency Report (duplicates merged)\n")
                f.write(f"Data source: {INPUT_FILE.name}\n")
                f.write(f"Total records: {total_records} | Unique IPC codes: {unique_ipc_count}\n")
                f.write("=" * 60 + "\n\n")
                f.write("Complete frequency list (descending):\n")
                f.write(f"{'Rank':<5} {'IPC':<14} {'Count':<7} {'Share'}\n")
                f.write("-" * 42 + "\n")
                f.write("\n".join(full_lines))
            print(f"\nFull report saved to: {OUTPUT_TXT.resolve()}")

    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}")
    except KeyError as e:
        print(f"ERROR: {e}")
    except Exception as e:
        print(f"ERROR: {str(e)}")


if __name__ == "__main__":
    generate_ipc_full_report(INPUT_FILE, save_to_txt=True)
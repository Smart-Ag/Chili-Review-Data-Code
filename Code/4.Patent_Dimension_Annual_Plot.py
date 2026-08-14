#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script 4: Yearly stacked percentage bar chart for chili patent dimensions
Input: ../Patent_Data/3.Patent_Keywords_with_Dimensions.xlsx
Output: ../Patent_Data/patent_yearly_stacked_bar.png
"""

import pandas as pd
import matplotlib.pyplot as plt
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

# ===================== Path Configuration =====================
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "Patent_Data"
INPUT_FILE = DATA_DIR / "3.Patent_Keywords_with_Dimensions.xlsx"
SAVE_PIC = DATA_DIR / "patent_yearly_stacked_bar.png"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ===================== Plot Style =====================
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

TARGET_DIMS = [
    'A',      # Harvest only (mechanical)
    'A∩C',    # Harvest + intelligent
    'A∩B',    # Harvest + cleaning (mechanical)
    'A∩B∩C',  # Harvest + cleaning + intelligent
    'B∩C',    # Cleaning + intelligent
    'B'       # Cleaning only (mechanical)
]

DIM_COLOR_MAP = {
    'A': '#C70039',
    'A∩C': '#FF5733',
    'A∩B': '#900C3F',
    'A∩B∩C': '#581845',
    'B∩C': '#0000FF',
    'B': '#117A65'
}

# ===================== Load & Clean Data =====================
df = pd.read_excel(INPUT_FILE)

# Auto generate unique ID if missing
if "专利唯一标识" not in df.columns:
    df["专利唯一标识"] = "专利_" + (df.index + 1).astype(str)

# Auto detect year column
if "申请年份" not in df.columns:
    year_cols = [col for col in df.columns if "年" in col]
    if year_cols:
        df["申请年份"] = df[year_cols[0]]
    else:
        df["申请年份"] = "未知年份"

# Filter valid integer years and deduplicate
df_valid = df[
    (df["申请年份"].apply(lambda x: isinstance(x, int) and x > 1900)) &
    (~df["专利唯一标识"].duplicated())
].copy()

if len(df_valid) == 0:
    raise ValueError("No valid patents with proper year found.")

year_min = df_valid["申请年份"].min()
year_max = df_valid["申请年份"].max()

# ===================== Yearly Count Function =====================
def count_dim_per_year(year_df):
    dim_count = {d: 0 for d in TARGET_DIMS}
    dim_count["A"] = len(year_df[year_df["技术维度"] == "采收"])
    dim_count["A∩C"] = len(year_df[year_df["技术维度"] == "采收;智能"])
    dim_count["A∩B"] = len(year_df[year_df["技术维度"] == "采收;清杂"])          # 修正：原误写为"清杂"列
    dim_count["A∩B∩C"] = len(year_df[year_df["技术维度"] == "采收;清杂;智能"])
    dim_count["B∩C"] = len(year_df[year_df["技术维度"] == "清杂;智能"])
    dim_count["B"] = len(year_df[year_df["技术维度"] == "清杂"])
    return dim_count

# Aggregate yearly counts
year_dim_count = {}
for year in sorted(df_valid["申请年份"].unique()):
    sub = df_valid[df_valid["申请年份"] == year]
    year_dim_count[year] = count_dim_per_year(sub)

year_dim_df = pd.DataFrame(year_dim_count).T.fillna(0).astype(int)

# Calculate annual percentages
year_dim_ratio = year_dim_df.div(year_dim_df.sum(axis=1), axis=0) * 100
year_dim_ratio = year_dim_ratio.fillna(0)

# ===================== Plot Stacked Bar =====================
fig, ax = plt.subplots(figsize=(16, 9))
bottom = pd.Series([0] * len(year_dim_ratio.index), index=year_dim_ratio.index)

for dim in TARGET_DIMS:
    lw = 3 if "C" in dim else 2
    ax.bar(
        year_dim_ratio.index,
        year_dim_ratio[dim],
        bottom=bottom,
        label=dim,
        color=DIM_COLOR_MAP[dim],
        width=0.8,
        edgecolor="white",
        linewidth=lw,
        alpha=1
    )
    bottom += year_dim_ratio[dim]

# Chart styling
ax.set_title(f'Annual proportion of chili patent dimensions ({year_min}–{year_max})',
             fontsize=18, fontweight="bold", pad=25, alpha=0.8)
ax.set_xlabel("Application Year", fontsize=14, labelpad=12, alpha=0.8)
ax.set_ylabel("Proportion (%)", fontsize=14, labelpad=12, alpha=0.8)
ax.set_ylim(0, 100)
ax.tick_params(axis="x", labelsize=11, rotation=45)
ax.tick_params(axis="y", labelsize=11)

# Legend
leg = ax.legend(
    loc="upper right", fontsize=8, frameon=True, fancybox=True, shadow=True,
    title="Dimension key: A=harvest, B=cleaning, C=intelligent"
)
leg.get_title().set_alpha(0.8)
leg.get_frame().set_alpha(0.5)

# Note box
note_text = (
"Symbol explanation:\n"
"A = mechanical harvest only\n"
"A∩C = harvest + intelligent\n"
"A∩B = mechanical harvest + cleaning\n"
"A∩B∩C = harvest + cleaning + intelligent\n"
"B∩C = cleaning + intelligent\n"
"B = mechanical cleaning only"
)
ax.text(0.02, 0.98, note_text, transform=ax.transAxes, fontsize=10, va="top", alpha=0.5,
        bbox=dict(boxstyle="round,pad=0.5", facecolor="#F0F0F0", alpha=0.5))

ax.grid(axis="y", linestyle="--", alpha=0.4, c="#333333")
ax.set_facecolor("#FFFFFF")
plt.tight_layout()

# Save
plt.savefig(SAVE_PIC, dpi=300, bbox_inches="tight")
plt.close()

# ===================== Minimal Output =====================
print(f"Chart saved to: {SAVE_PIC}")

# ===================== Journal Figure Caption =====================
print("\n===== Figure caption for Biosystems Engineering =====")
print(f"Stacked percentage bar chart showing annual proportion of six chili patent technical dimensions from {year_min} to {year_max}. Symbol definitions: A = mechanical harvesting only, A∩C = harvesting with intelligent modules, A∩B = mechanical harvesting-cleaning integrated devices, A∩B∩C = harvesting-cleaning with intelligent functions, B∩C = intelligent sorting/cleaning equipment, B = mechanical cleaning only. Each vertical bar sums to 100% representing all patents filed in that corresponding year.")
print("======================================================")
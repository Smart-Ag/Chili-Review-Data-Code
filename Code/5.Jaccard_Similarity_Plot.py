#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script 5: Calculate & Visualize Jaccard Similarity Coefficients of Patent Keyword Sets
Input: ../Patent_Data/3.Patent_Keywords_with_Dimensions.xlsx
Output: ../Patent_Data/jaccard_similarity_bar.png
"""

import pandas as pd
import matplotlib.pyplot as plt
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

# ===================== Path Configuration =====================
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "Patent_Data"
CORE_FILE = DATA_DIR / "3.Patent_Keywords_with_Dimensions.xlsx"
SAVE_FIG = DATA_DIR / "jaccard_similarity_bar.png"
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ===================== Plot Style =====================
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

COLOR_MAP = {
    '纯采收（机械）': '#C70039',
    '采收智能': '#FF5733',
    '采收清杂（机械）': '#900C3F',
    '采收清杂智能（交叉）': '#581845',
    '清杂智能': '#0000FF',
    '纯清杂（机械）': '#117A65'
}

# ===================== Core Functions =====================
def calculate_jaccard(set1, set2):
    intersection = len(set1 & set2)
    union = len(set1 | set2)
    return intersection / union if union != 0 else 0

def clean_dim_value(dim_str):
    if pd.isna(dim_str):
        return ""
    return dim_str.replace(" ", "").replace("；", ";").replace("-", ";").lower()

def get_keyword_set_by_dim(df, dim_keywords, keyword_col):
    df["技术维度_清洗后"] = df["技术维度"].apply(clean_dim_value)
    filter_mask = pd.Series([True] * len(df))
    for kw in dim_keywords:
        filter_mask = filter_mask & df["技术维度_清洗后"].str.contains(kw.lower(), na=False)
    if "采收" in dim_keywords and "智能" not in dim_keywords and "清杂" not in dim_keywords:
        filter_mask = filter_mask & ~df["技术维度_清洗后"].str.contains("清杂|智能", na=False)
    if "清杂" in dim_keywords and "智能" not in dim_keywords and "采收" not in dim_keywords:
        filter_mask = filter_mask & ~df["技术维度_清洗后"].str.contains("采收|智能", na=False)
    df_filtered = df[filter_mask].copy()
    keyword_set = set()
    for kw_str in df_filtered[keyword_col]:
        if pd.isna(kw_str) or kw_str in ["无", "无关键词", "", " "]:
            continue
        for kw in kw_str.split(";"):
            if kw.strip():
                keyword_set.add(kw.strip().lower())
    return keyword_set

# ===================== Load & Deduplicate =====================
df_core = pd.read_excel(CORE_FILE)

# 自动检测关键词列（匹配“关键词”或“keyword”）
keyword_col = None
for col in df_core.columns:
    if '关键词' in col or 'keyword' in col.lower():
        keyword_col = col
        break
if keyword_col is None:
    raise ValueError(f"未找到关键词列，可用列名: {df_core.columns.tolist()}")

# 去重（如果有专利唯一标识列）
if "专利唯一标识" in df_core.columns:
    df_core = df_core.drop_duplicates(subset="专利唯一标识", keep="first")

# ===================== Extract Keyword Sets =====================
harvest_mech_set = get_keyword_set_by_dim(df_core, ["采收"], keyword_col)           # A
harvest_intel_set = get_keyword_set_by_dim(df_core, ["采收", "智能"], keyword_col)   # A∩C
harvest_clean_mech_set = get_keyword_set_by_dim(df_core, ["采收", "清杂"], keyword_col)  # A∩B
harvest_clean_intel_set = get_keyword_set_by_dim(df_core, ["采收", "清杂", "智能"], keyword_col)  # A∩B∩C
clean_intel_set = get_keyword_set_by_dim(df_core, ["清杂", "智能"], keyword_col)     # B∩C
clean_mech_set = get_keyword_set_by_dim(df_core, ["清杂"], keyword_col)             # B

# ===================== Compute Jaccard =====================
pairs = [
    "A vs A∩C",
    "B vs B∩C",
    "B vs A∩B∩C",
    "A∩C vs A∩B∩C",
    "A vs B",
    "A∩C vs B∩C"
]
sets_mapping = {
    "A vs A∩C": (harvest_mech_set, harvest_intel_set),
    "B vs B∩C": (clean_mech_set, clean_intel_set),
    "B vs A∩B∩C": (clean_mech_set, harvest_clean_intel_set),
    "A∩C vs A∩B∩C": (harvest_intel_set, harvest_clean_intel_set),
    "A vs B": (harvest_mech_set, clean_mech_set),
    "A∩C vs B∩C": (harvest_intel_set, clean_intel_set)
}
jaccard_results = {pair: calculate_jaccard(s1, s2) for pair, (s1, s2) in sets_mapping.items()}

# ===================== Plot =====================
fig, ax = plt.subplots(figsize=(14, 8))
bars = ax.bar(jaccard_results.keys(), jaccard_results.values(),
              color=[COLOR_MAP['采收智能'], COLOR_MAP['清杂智能'], COLOR_MAP['采收清杂智能（交叉）'],
                     COLOR_MAP['采收清杂智能（交叉）'], COLOR_MAP['纯清杂（机械）'], COLOR_MAP['清杂智能']],
              width=0.7, edgecolor="white", linewidth=2, alpha=0.9)

for bar, val in zip(bars, jaccard_results.values()):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height()+0.01,
            f"{val:.3f}", ha="center", va="bottom", fontsize=12, weight="bold", alpha=0.8)

ax.axhline(y=0.3, c="#FECA57", ls="--", lw=2, label="Low similarity threshold = 0.3")
ax.axhline(y=0.4, c="#96CEB4", ls="--", lw=2, label="Medium fusion threshold = 0.4")
ax.axhline(y=0.6, c="#FF9FF3", ls="--", lw=2, label="High similarity threshold = 0.6")

ax.set_title("Pairwise Jaccard similarity of keyword sets for chili patent technical groups",
             fontsize=18, weight="bold", pad=25, alpha=0.8)
ax.set_ylabel("Jaccard Similarity Coefficient (0–1)", fontsize=14, labelpad=12, alpha=0.8)
ax.set_ylim(0, 1.0)
ax.tick_params(axis="x", labelsize=12, rotation=0)
ax.grid(axis="y", ls="--", alpha=0.3, c="#333333")
ax.legend(loc="upper right", fontsize=11, frameon=True, shadow=True)

note_text = "Symbol rule: A=mechanical harvest, B=mechanical cleaning, C=intelligent modules\nA∩C=harvest+intelligent, B∩C=cleaning+intelligent, A∩B∩C=integrated three-in-one"
ax.text(0.02, 0.98, note_text, transform=ax.transAxes, fontsize=10, va="top", alpha=0.8,
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5))

plt.tight_layout()
plt.savefig(SAVE_FIG, dpi=300, bbox_inches="tight")
plt.close()

print(f"Chart saved to: {SAVE_FIG}")

# ===================== Figure Caption =====================
print("\n===== Figure Caption for Biosystems Engineering =====")
print("Bar chart of pairwise Jaccard similarity coefficients calculated on extracted keyword sets of six chili patent technical categories. Symbol definitions: A = purely mechanical harvesting patents, B = purely mechanical cleaning patents, A∩C = harvesting equipment with intelligent modules, B∩C = intelligent sorting/cleaning devices, A∩B∩C = integrated harvesting-cleaning machinery equipped with intelligent functions. Jaccard index is defined as the size of the intersection of two keyword sets divided by the size of their union. Three horizontal dashed reference lines denote low (0.3), medium fusion (0.4), and high similarity (0.6) thresholds respectively.")
print("======================================================")
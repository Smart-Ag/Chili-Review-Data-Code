#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script 3: Double-layer donut chart for patent technical dimension statistics
Input : ../Patent_Data/3.Patent_Keywords_with_Dimensions.xlsx
Output: ../Patent_Data/chili_patent_dimension_donut.png
"""

import pandas as pd
import matplotlib.pyplot as plt
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

# ===================== 1. 路径配置 =====================
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "Patent_Data"
FILE_PATH = DATA_DIR / "3.Patent_Keywords_with_Dimensions.xlsx"
OUT_PIC = DATA_DIR / "chili_patent_dimension_donut.png"

# ===================== 2. 绘图样式 =====================
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False

COLORS = {
    "A": "#1f77b4",
    "B": "#2ca02c",
    "A∩B": "#9467bd",
    "A∩C": "#ff7f0e",
    "A\\C": "#aec7e8",
    "B∩C": "#d62728",
    "B\\C": "#98df8a",
    "A∩B∩C": "#8c564b",
    "(A∩B)\\C": "#e377c2",
}

# ===================== 3. 核心函数（与原始完全一致） =====================
def get_top2_keywords(df_target, keyword_col):
    """统计Top2关键词，过滤作物词汇"""
    FILTER_CROP_WORDS = ["辣椒", "辣椒粉", "朝天椒"]
    if len(df_target) == 0:
        return ["无", "无"]
    kw_count = {}
    for kw_str in df_target[keyword_col]:
        if pd.isna(kw_str) or kw_str == "无关键词":
            continue
        for kw in kw_str.split(";"):
            if kw not in FILTER_CROP_WORDS:
                kw_count[kw] = kw_count.get(kw, 0) + 1
    sorted_kw = sorted(kw_count.items(), key=lambda x: x[1], reverse=True)
    top2 = [kw[0] for kw in sorted_kw[:2]] if sorted_kw else ["无", "无"]
    return top2 if len(top2) == 2 else top2 + ["无"]

# ===================== 4. 数据读取与统计 =====================
df = pd.read_excel(FILE_PATH)

# 自动检测关键词列（适配“关键词(K1)”等变体）
keyword_col = None
for col in df.columns:
    if '关键词' in col or 'keyword' in col.lower():
        keyword_col = col
        break
if keyword_col is None:
    raise ValueError(f"未找到关键词列，可用列名: {df.columns.tolist()}")

# 确保专利唯一标识列存在（若没有则生成）
if "专利唯一标识" not in df.columns:
    df["专利唯一标识"] = "专利_" + (df.index + 1).astype(str)

# 【重要】原始代码未去重，此处保持一致，直接使用全部数据
# 若您希望去重，可取消下面一行的注释并注释掉上一行
# df = df.drop_duplicates(subset=["专利唯一标识"])
total_all = len(df)

print(f"========== 字母体系说明：A=采收、B=清杂、C=智能 ==========\n")

# ------------ 内层3大类 ------------
df_pure_harvest = df[
    (df["技术维度"].str.contains("采收", na=False)) &
    (~df["技术维度"].str.contains("清杂", na=False))
]
pure_harvest_total = len(df_pure_harvest)
pure_harvest_ratio = pure_harvest_total / total_all * 100

df_pure_clean = df[
    (df["技术维度"].str.contains("清杂", na=False)) &
    (~df["技术维度"].str.contains("采收", na=False))
]
pure_clean_total = len(df_pure_clean)
pure_clean_ratio = pure_clean_total / total_all * 100

df_mix_harvest_clean = df[
    (df["技术维度"].str.contains("采收", na=False)) &
    (df["技术维度"].str.contains("清杂", na=False))
]
mix_harvest_clean_total = len(df_mix_harvest_clean)
mix_harvest_clean_ratio = mix_harvest_clean_total / total_all * 100

# ------------ 外层细分 ------------
# 纯采收内部分类
df_pure_harvest_intel = df_pure_harvest[df_pure_harvest["技术维度"] == "采收;智能"]
df_pure_harvest_mech = df_pure_harvest[df_pure_harvest["技术维度"] == "采收"]
pure_harvest_intel = len(df_pure_harvest_intel)
pure_harvest_mech = len(df_pure_harvest_mech)
pure_harvest_intel_ratio = pure_harvest_intel / pure_harvest_total * 100 if pure_harvest_total > 0 else 0
pure_harvest_mech_ratio = 100 - pure_harvest_intel_ratio

# 纯清杂内部分类
df_pure_clean_intel = df_pure_clean[df_pure_clean["技术维度"] == "清杂;智能"]
df_pure_clean_mech = df_pure_clean[df_pure_clean["技术维度"] == "清杂"]
pure_clean_intel = len(df_pure_clean_intel)
pure_clean_mech = len(df_pure_clean_mech)
pure_clean_intel_ratio = pure_clean_intel / pure_clean_total * 100 if pure_clean_total > 0 else 0
pure_clean_mech_ratio = 100 - pure_clean_intel_ratio

# 混采清内部分类
df_mix_harvest_clean_intel = df_mix_harvest_clean[df_mix_harvest_clean["技术维度"] == "采收;清杂;智能"]
df_mix_harvest_clean_mech = df_mix_harvest_clean[df_mix_harvest_clean["技术维度"] == "采收;清杂"]
mix_harvest_clean_intel = len(df_mix_harvest_clean_intel)
mix_harvest_clean_mech = len(df_mix_harvest_clean_mech)
mix_harvest_clean_intel_ratio = mix_harvest_clean_intel / mix_harvest_clean_total * 100 if mix_harvest_clean_total > 0 else 0
mix_harvest_clean_mech_ratio = 100 - mix_harvest_clean_intel_ratio

# ------------ 关键词统计 ------------
pure_harvest_top2 = get_top2_keywords(df_pure_harvest, keyword_col)
pure_clean_top2 = get_top2_keywords(df_pure_clean, keyword_col)
mix_harvest_clean_top2 = get_top2_keywords(df_mix_harvest_clean, keyword_col)
pure_harvest_intel_top2 = get_top2_keywords(df_pure_harvest_intel, keyword_col)
pure_clean_intel_top2 = get_top2_keywords(df_pure_clean_intel, keyword_col)
mix_harvest_clean_intel_top2 = get_top2_keywords(df_mix_harvest_clean_intel, keyword_col)
pure_harvest_mech_top2 = get_top2_keywords(df_pure_harvest_mech, keyword_col)
pure_clean_mech_top2 = get_top2_keywords(df_pure_clean_mech, keyword_col)
mix_harvest_clean_mech_top2 = get_top2_keywords(df_mix_harvest_clean_mech, keyword_col)

# ------------ 全局纯机械占比 ------------
global_mech_total = pure_harvest_mech + pure_clean_mech + mix_harvest_clean_mech
global_mech_ratio = global_mech_total / total_all * 100

# ===================== 5. 打印统计结果（与原始输出完全一致） =====================
print("========== 自动精准统计（ABC字母体系+全维度关键词，已过滤辣椒相关作物词汇）==========")
print(f"总专利数：{total_all}条（100%）")
print(f"1. 纯采收类（A）：{pure_harvest_total}条（占总数{pure_harvest_ratio:.1f}%）｜核心词：{pure_harvest_top2[0]}、{pure_harvest_top2[1]}")
print(f"   ├─ 智能采收（A∩C）：{pure_harvest_intel}条（占A类{pure_harvest_intel_ratio:.1f}%）｜核心词：{pure_harvest_intel_top2[0]}、{pure_harvest_intel_top2[1]}")
print(f"   └─ 机械采收（A\\C）：{pure_harvest_mech}条（占A类{pure_harvest_mech_ratio:.1f}%）｜核心词：{pure_harvest_mech_top2[0]}、{pure_harvest_mech_top2[1]}")
print(f"2. 纯清杂类（B）：{pure_clean_total}条（占总数{pure_clean_ratio:.1f}%）｜核心词：{pure_clean_top2[0]}、{pure_clean_top2[1]}")
print(f"   ├─ 智能清杂（B∩C）：{pure_clean_intel}条（占B类{pure_clean_intel_ratio:.1f}%）｜核心词：{pure_clean_intel_top2[0]}、{pure_clean_intel_top2[1]}")
print(f"   └─ 机械清杂（B\\C）：{pure_clean_mech}条（占B类{pure_clean_mech_ratio:.1f}%）｜核心词：{pure_clean_mech_top2[0]}、{pure_clean_mech_top2[1]}")
print(f"3. 采收+清杂类（A∩B）：{mix_harvest_clean_total}条（占总数{mix_harvest_clean_ratio:.1f}%）｜核心词：{mix_harvest_clean_top2[0]}、{mix_harvest_clean_top2[1]}")
print(f"   ├─ 智能混采清（A∩B∩C）：{mix_harvest_clean_intel}条（占A∩B类{mix_harvest_clean_intel_ratio:.1f}%）｜核心词：{mix_harvest_clean_intel_top2[0]}、{mix_harvest_clean_intel_top2[1]}")
print(f"   └─ 机械混采清（(A∩B)\\C）：{mix_harvest_clean_mech}条（占A∩B类{mix_harvest_clean_mech_ratio:.1f}%）｜核心词：{mix_harvest_clean_mech_top2[0]}、{mix_harvest_clean_mech_top2[1]}")
print(f"\n【全局纯机械专利占比】{global_mech_total}条，占总数的 {global_mech_ratio:.1f}%")

# ===================== 6. 绘制双层环形图 =====================
fig, ax = plt.subplots(figsize=(22, 14))
start_angle = 90
inner_radius = 0.5
inner_w = 0.3
outer_r = inner_radius + inner_w
outer_w = 0.3

# 内层
inner_labels = [
    f'A（纯采收）\n{pure_harvest_total}条（总数{pure_harvest_ratio:.1f}%）\n关键词：{pure_harvest_top2[0]}、{pure_harvest_top2[1]}',
    f'B（纯清杂）\n{pure_clean_total}条（总数{pure_clean_ratio:.1f}%）\n关键词：{pure_clean_top2[0]}、{pure_clean_top2[1]}',
    f'A∩B（采收+清杂）\n{mix_harvest_clean_total}条（总数{mix_harvest_clean_ratio:.1f}%）\n关键词：{mix_harvest_clean_top2[0]}、{mix_harvest_clean_top2[1]}'
]
ax.pie(
    [pure_harvest_total, pure_clean_total, mix_harvest_clean_total],
    radius=inner_radius, startangle=start_angle,
    colors=[COLORS["A"], COLORS["B"], COLORS["A∩B"]],
    labels=inner_labels, labeldistance=0.7, textprops={"fontsize":12, "weight":"bold"},
    wedgeprops={"edgecolor":"white", "linewidth":3, "alpha":0.9, "width":inner_w}
)

# 外层
outer_vals = [pure_harvest_intel, pure_harvest_mech, pure_clean_intel, pure_clean_mech, mix_harvest_clean_intel, mix_harvest_clean_mech]
outer_labels = [
    f'A∩C（智能采收）\n{pure_harvest_intel}条（A类{pure_harvest_intel_ratio:.1f}%）\n关键词：{pure_harvest_intel_top2[0]}、{pure_harvest_intel_top2[1]}',
    f'A\\C（机械采收）\n{pure_harvest_mech}条（A类{pure_harvest_mech_ratio:.1f}%）\n关键词：{pure_harvest_mech_top2[0]}、{pure_harvest_mech_top2[1]}',
    f'B∩C（智能清杂）\n{pure_clean_intel}条（B类{pure_clean_intel_ratio:.1f}%）\n关键词：{pure_clean_intel_top2[0]}、{pure_clean_intel_top2[1]}',
    f'B\\C（机械清杂）\n{pure_clean_mech}条（B类{pure_clean_mech_ratio:.1f}%）\n关键词：{pure_clean_mech_top2[0]}、{pure_clean_mech_top2[1]}',
    f'A∩B∩C（智能混采清）\n{mix_harvest_clean_intel}条（A∩B类{mix_harvest_clean_intel_ratio:.1f}%）\n关键词：{mix_harvest_clean_intel_top2[0]}、{mix_harvest_clean_intel_top2[1]}',
    f'(A∩B)\\C（机械混采清）\n{mix_harvest_clean_mech}条（A∩B类{mix_harvest_clean_mech_ratio:.1f}%）\n关键词：{mix_harvest_clean_mech_top2[0]}、{mix_harvest_clean_mech_top2[1]}'
]
outer_cols = [COLORS["A∩C"], COLORS["A\\C"], COLORS["B∩C"], COLORS["B\\C"], COLORS["A∩B∩C"], COLORS["(A∩B)\\C"]]
ax.pie(
    outer_vals, radius=outer_r, startangle=start_angle, colors=outer_cols,
    labels=outer_labels, labeldistance=1.08, textprops={"fontsize":10},
    wedgeprops={"edgecolor":"white", "linewidth":2, "alpha":0.85, "width":outer_w}
)

ax.set_title("辣椒专利技术维度双层占比图（A=采收、B=清杂、C=智能）", fontsize=20, weight="bold", pad=50)

# 图例
legend_items = [
    plt.Rectangle((0,0),1,1, fc=COLORS["A"], ec="white", label=f"A（纯采收）｜{pure_harvest_top2[0]}、{pure_harvest_top2[1]}"),
    plt.Rectangle((0,0),1,1, fc=COLORS["B"], ec="white", label=f"B（纯清杂）｜{pure_clean_top2[0]}、{pure_clean_top2[1]}"),
    plt.Rectangle((0,0),1,1, fc=COLORS["A∩B"], ec="white", label=f"A∩B（采收+清杂）｜{mix_harvest_clean_top2[0]}、{mix_harvest_clean_top2[1]}"),
    plt.Rectangle((0,0),1,1, fc=COLORS["A∩C"], ec="white", label=f"A∩C（智能采收）｜{pure_harvest_intel_top2[0]}、{pure_harvest_intel_top2[1]}"),
    plt.Rectangle((0,0),1,1, fc=COLORS["B∩C"], ec="white", label=f"B∩C（智能清杂）｜{pure_clean_intel_top2[0]}、{pure_clean_intel_top2[1]}"),
    plt.Rectangle((0,0),1,1, fc=COLORS["A∩B∩C"], ec="white", label=f"A∩B∩C（智能混采清）｜{mix_harvest_clean_intel_top2[0]}、{mix_harvest_clean_intel_top2[1]}"),
    plt.Rectangle((0,0),1,1, fc=COLORS["A\\C"], ec="white", label=f"A\\C（机械采收）｜{pure_harvest_mech_top2[0]}、{pure_harvest_mech_top2[1]}"),
    plt.Rectangle((0,0),1,1, fc=COLORS["B\\C"], ec="white", label=f"B\\C（机械清杂）｜{pure_clean_mech_top2[0]}、{pure_clean_mech_top2[1]}"),
    plt.Rectangle((0,0),1,1, fc=COLORS["(A∩B)\\C"], ec="white", label=f"(A∩B)\\C（机械混采清）｜{mix_harvest_clean_mech_top2[0]}、{mix_harvest_clean_mech_top2[1]}")
]
ax.legend(handles=legend_items, loc="center left", bbox_to_anchor=(1.1, 0.5), fontsize=10,
          title="字母体系：A=采收、B=清杂、C=智能", title_fontsize=13)

plt.subplots_adjust(left=0.05, right=0.75)
plt.tight_layout()
plt.savefig(OUT_PIC, dpi=300, bbox_inches="tight")
plt.close()

print(f"\n图表已保存至: {OUT_PIC}")

# ===================== 7. 输出论文图注（与原始一致） =====================
print("\n" + "="*70)
print("【✅ 论文图注直接复制区 - 请直接复制以下说明到您的论文 Figure Caption 中】")
print("="*70)
print(f"辣椒专利技术维度双层占比分布图（基于 IncoPat 数据）。内环代表三大基础维度在全体专利中的实际占比（A：纯采收，B：纯清杂，A∩B：采收+清杂）；")
print(f"外环将各基础维度进一步细分为是否包含智能技术（C）。")
print(f"需特别说明：外环所示百分比（如 A\\C 占 A 类的 {pure_harvest_mech_ratio:.1f}%）表示该细分占其所属内环维度的相对比例，而非占总专利的比例。")
print(f"经计算，全局纯机械技术（即 A\\C、B\\C 及 (A∩B)\\C 三者互斥之和）在总专利中的真实占比为 {global_mech_ratio:.1f}%。")
print("="*70)
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script 6: Convert patent Excel to CNKI-format TXT for CiteSpace import
Input : ../Patent_Data/3.Patent_Keywords_with_Dimensions.xlsx
Output: ../Patent_Data/cnki_patent_standard.txt
"""

import pandas as pd
from pathlib import Path

# ===================== 路径配置 =====================
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "Patent_Data"
EXCEL_PATH = DATA_DIR / "3.Patent_Keywords_with_Dimensions.xlsx"
OUTPUT_TXT = DATA_DIR / "download_787_converted.txt"
DATA_DIR.mkdir(parents=True, exist_ok=True)


def detect_column(df, keywords):
    """根据关键词列表检测列名，返回第一个匹配的列名"""
    for col in df.columns:
        for kw in keywords:
            if kw in col or kw.lower() in col.lower():
                return col
    return None


def clean_text(text):
    """清理文本：去除换行、多余空格，空值转为空字符串"""
    if pd.isna(text):
        return ""
    return str(text).replace("\n", " ").replace("\t", " ").strip()


def main():
    print(f"读取文件: {EXCEL_PATH}")
    df = pd.read_excel(EXCEL_PATH)

    # 自动检测各列
    title_col = detect_column(df, ["标题", "T1"])
    inventor_col = detect_column(df, ["发明人", "A1"])
    applicant_col = detect_column(df, ["申请人", "AD"])
    year_col = detect_column(df, ["年份", "YR", "申请年份"])
    patent_col = detect_column(df, ["专利号", "PN", "专利唯一标识"])
    keyword_col = detect_column(df, ["关键词", "K1"])
    abstract_col = detect_column(df, ["摘要", "AB"])

    if keyword_col is None:
        raise ValueError(f"未找到关键词列，可用列名: {df.columns.tolist()}")
    print(f"使用关键词列: '{keyword_col}'")

    # 若某些列为空，用空字符串替代
    if title_col is None:
        title_col = "T1"
        df["T1"] = ""
    if inventor_col is None:
        inventor_col = "A1"
        df["A1"] = ""
    if applicant_col is None:
        applicant_col = "AD"
        df["AD"] = ""
    if year_col is None:
        year_col = "YR"
        df["YR"] = ""
    if patent_col is None:
        patent_col = "PN"
        df["PN"] = ""
    if abstract_col is None:
        abstract_col = "AB"
        df["AB"] = ""

    # 构建CNKI字段映射
    records = []
    for idx, row in df.iterrows():
        record = [
            "RT Patent",
            f"SR {idx + 1}",
            f"A1 {clean_text(row[inventor_col])}",
            "FI",
            f"AD {clean_text(row[applicant_col])}",
            f"T1 {clean_text(row[title_col])}",
            f"YR {clean_text(row[year_col])}",
            f"PN {clean_text(row[patent_col])}",
            "IP",
            "MP",
            f"K1 {clean_text(row[keyword_col])}",
            f"AB {clean_text(row[abstract_col])}",
            "LA 中文;",
            "DS CNKI",
            "LK",
            "DO"
        ]
        records.append("\n".join(record))

    # 写入文件（无空行间隔）
    with open(OUTPUT_TXT, "w", encoding="utf-8") as f:
        f.write("\n".join(records))

    print(f"CNKI格式文本已生成: {OUTPUT_TXT}")
    print(f"共处理 {len(records)} 条专利")


if __name__ == "__main__":
    main()
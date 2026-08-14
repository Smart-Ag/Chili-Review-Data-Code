"""
Script 1: TF-IDF Keyword Extraction for Patent Records
=======================================================
Input : ../Patent_Data/1.Raw_787_Patents.xlsx  (raw IncoPat export, 787 patents)
Output: ../Patent_Data/2.Extracted_Keywords_787.xlsx
Output columns (exact match with provided template):
   序号, 标题(T1), 发明人(A1), 申请人(AD), 年份(YR), 专利号(PN), 关键词(K1), 摘要(AB)
Logic :
  1. Train a TF-IDF model on all patent titles.
  2. For each patent, select top-N keywords from the title first;
     if fewer than N, supplement from the abstract using the same model.
  3. Core technical words receive a 2x score boost.
Dependencies: pandas, numpy, jieba, scikit-learn, openpyxl
"""

import os
import re
import sys
import warnings
from collections import Counter
from pathlib import Path

import jieba
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

# Suppress sklearn warnings about token_pattern (we use custom tokenizer)
warnings.filterwarnings('ignore', category=UserWarning, module='sklearn')

# ===================== 1. Configuration =====================
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "Patent_Data"

INPUT_FILE = DATA_DIR / "1.Raw_787_Patents.xlsx"
OUTPUT_FILE = DATA_DIR / "2.Extracted_Keywords_787.xlsx"

TARGET_KW_NUM = 5

TECH_CORE_WORDS = {
    '采收', '收获', '采摘', '清选', '筛选', '分选', '色选', '风选', '去杂', '去石机',
    '采收机', '收获机', '采摘机', '清选机', '色选机', '风选机', '切把', '除柄',
    '智能', '自动', '机器人', '视觉', '机器视觉', '辣椒', '果实',
    '清杂', '除杂', '去杂质', '采摘器', '斜眼筛', '去把', '机械臂', '识别', '预测模型'
}

STOPWORDS = set([
    "设置", "设有", "机构", "装置", "安装", "连接", "输送", "机架", "箱体", "基于", "快速", "具备", "不易",
    "驱动", "设备", "本发明", "进行", "用于", "提供", "所述", "包括", "可以", "部件", "任务", "及其", "适宜",
    "新型", "方法", "具有", "结构", "生产", "加工", "作业", "电机", "壳体", "不同", "可拆卸", "优异", "构成",
    "能够", "实用新型", "固定架", "支撑架", "支架", "人工", "人员", "采用", "方便", "综合", "加工性", "农作物",
    "主轴", "本体", "框架", "使用", "单元", "转动", "支撑", "传动", "车体", "给料", "便于", "露地",
    "系统", "带有", "放置", "固定", "实现", "操作", "涉及", "属于", "领域", "适用", "简易", "规格", "大量",
    "解决", "技术", "方案", "效果", "组件", "原料", "物料", "模块", "工具", "辅助", "平台"
])

# ===================== 2. Custom dictionary =====================
for word in TECH_CORE_WORDS:
    jieba.add_word(word, freq=2000)

# ===================== 3. Preprocessing functions =====================
def preprocess_text(text):
    if pd.isna(text) or not isinstance(text, str):
        return ""
    # Remove common patent boilerplate prefixes
    patterns = [
        r'一种', r'本发明涉及', r'本实用新型涉及',
        r'本发明提供', r'本实用新型提供', r'本发明公开了',
        r'本实用新型公开了', r'该发明', r'该实用新型'
    ]
    for pattern in patterns:
        text = re.sub(pattern, '', text)
    text = re.sub(r'[^\u4e00-\u9fa5]', ' ', text)
    return ' '.join(text.split())

def extract_public_year(public_date):
    if pd.isna(public_date):
        return "未知年份"
    date_str = str(public_date).strip()
    match = re.search(r"^(\d{4})-\d{2}-\d{2}$", date_str)
    if match:
        return int(match.group(1))
    try:
        parsed = pd.to_datetime(date_str, errors='coerce')
        if not pd.isna(parsed):
            return parsed.year
    except Exception:
        pass
    match = re.search(r"\b(19\d{2}|20\d{2})\b", date_str)
    if match:
        return int(match.group(1))
    return "未知年份"

# ===================== 4. Main processing =====================
def batch_process_simple():
    # Minimal output
    print("Patent Keyword Extraction (TF-IDF) ...", end=' ', flush=True)

    try:
        # ---- 0. Input check ----
        if not INPUT_FILE.exists():
            print("\nERROR: Input file not found. Expected:")
            print(f"  {INPUT_FILE}")
            print("Please ensure the directory structure:\n  Chili_Review_Data_Code/\n  ├── Code/\n  │   └── 1.TF-IDF_Extraction.py\n  └── Patent_Data/\n      └── 1.Raw_787_Patents.xlsx")
            sys.exit(1)

        # ---- 1. Read data ----
        df = pd.read_excel(INPUT_FILE)

        # Standardise column names (IncoPat export conventions)
        column_mapping = {
            '标题': ['标题', '标题 (中文)', 'title', '专利名称', '发明名称'],
            '摘要': ['摘要', '摘要 (中文)', 'abstract', '专利摘要', '发明摘要'],
            '申请日': ['申请日', '申请日期', '公开日', '公开日期'],
            '发明人': ['发明人', 'inventor', 'inventors'],
            '申请人': ['申请人', 'applicant', '申请单位', '专利权人'],
            '专利号': ['专利号', '申请号', '公开（公告）号', '公开号', '公告号'],
        }

        for standard_name, possible_names in column_mapping.items():
            if standard_name not in df.columns:
                for name in possible_names:
                    if name in df.columns:
                        df.rename(columns={name: standard_name}, inplace=True)
                        break

        total_patents = len(df)

        # ---- 2. Metadata ----
        if "申请日" in df.columns:
            df["申请年份"] = df["申请日"].apply(extract_public_year)
        else:
            df["申请年份"] = "未知年份"

        df["作者"] = df["发明人"].astype(str).str.strip() if "发明人" in df.columns else "未知作者"
        df["机构"] = df["申请人"].astype(str).str.strip() if "申请人" in df.columns else "未知机构"

        # ---- 3. Preprocess ----
        df["标题处理文本"] = df["标题"].apply(preprocess_text)
        df["摘要处理文本"] = df["摘要"].apply(preprocess_text) if "摘要" in df.columns else ""

        # ---- 4. Train TF-IDF ----
        title_corpus = df["标题处理文本"].fillna('').tolist()
        tfidf_vectorizer = TfidfVectorizer(
            tokenizer=lambda x: list(jieba.cut(x)),
            stop_words=list(STOPWORDS),
            max_features=2000,
            min_df=1,
            max_df=0.9
        )
        tfidf_vectorizer.fit(title_corpus)
        feature_names = tfidf_vectorizer.get_feature_names_out()

        # ---- 5. Extract keywords ----
        all_keywords = []

        for i, (title_text, abstract_text) in enumerate(
            zip(df["标题处理文本"], df["摘要处理文本"])
        ):
            keywords = []
            title_candidates = []

            # Title first
            if title_text and len(title_text.strip()) > 1:
                title_tfidf = tfidf_vectorizer.transform([title_text])
                title_scores = dict(zip(feature_names, title_tfidf.toarray().flatten()))
                for word, score in title_scores.items():
                    if score > 0 and word not in STOPWORDS and len(word) > 1:
                        if word in TECH_CORE_WORDS:
                            score *= 2.0
                        title_candidates.append((word, score))
                title_candidates.sort(key=lambda x: x[1], reverse=True)
                for word, _ in title_candidates:
                    if word not in keywords:
                        keywords.append(word)
                        if len(keywords) >= TARGET_KW_NUM:
                            break

            # Supplement from abstract if needed
            if len(keywords) < TARGET_KW_NUM and abstract_text and len(abstract_text.strip()) > 10:
                abstract_tfidf = tfidf_vectorizer.transform([abstract_text])
                abstract_scores = dict(zip(feature_names, abstract_tfidf.toarray().flatten()))
                abstract_candidates = []
                for word, score in abstract_scores.items():
                    if score > 0 and word not in STOPWORDS and len(word) > 1 and word not in keywords:
                        if word in TECH_CORE_WORDS:
                            score *= 2.0
                        abstract_candidates.append((word, score))
                abstract_candidates.sort(key=lambda x: x[1], reverse=True)
                for word, _ in abstract_candidates:
                    if word not in keywords:
                        keywords.append(word)
                        if len(keywords) >= TARGET_KW_NUM:
                            break

            all_keywords.append(keywords[:TARGET_KW_NUM])

        # ---- 6. Build output DataFrame ----
        # Generate sequential number starting from 1
        df_out = pd.DataFrame({
            "序号": range(1, total_patents + 1),
            "标题(T1)": df["标题"],
            "发明人(A1)": df["作者"],
            "申请人(AD)": df["机构"],
            "年份(YR)": df["申请年份"],
            "专利号(PN)": df["专利号"] if "专利号" in df.columns else [f"专利_{i+1:04d}" for i in range(total_patents)],
            "关键词(K1)": [";".join(kws) if kws else "无关键词" for kws in all_keywords],
            "摘要(AB)": df["摘要"] if "摘要" in df.columns else ""
        })

        # ---- 7. Save ----
        OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
        df_out.to_excel(OUTPUT_FILE, index=False)
        print("Done.")
        return df_out

    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = batch_process_simple()
    if result is not None:
        print("\nSample output (first 3 rows):")
        print(result[["序号", "标题(T1)", "发明人(A1)", "申请人(AD)", "年份(YR)", "专利号(PN)", "关键词(K1)"]].head(3).to_string(index=False))
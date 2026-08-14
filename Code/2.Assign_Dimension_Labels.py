#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script 2: Patent Dimension Labelling
=====================================
Input : ../Patent_Data/2.Extracted_Keywords_787.xlsx
Output: ../Patent_Data/3.Patent_Keywords_with_Dimensions.xlsx
"""

from pathlib import Path
import pandas as pd

# ===================== 路径配置 =====================
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "Patent_Data"
INPUT_FILE = DATA_DIR / "2.Extracted_Keywords_787.xlsx"
OUTPUT_FILE = DATA_DIR / "3.Patent_Keywords_with_Dimensions.xlsx"

# ===================== 技术维度词库 =====================
HARVEST_KEYWORDS = [
    '采收', '收获', '采摘', '收割', '摘果', '采果', '采集', '剪枝', '脱果', '收料',
    '采椒', '摘椒', '收果', '采收机', '收获机', '采摘装置', '收集', '抓取'
]

CLEAN_KEYWORDS = [
    '除杂', '筛选', '清选', '分选', '清杂', '筛分', '风选', '色选', '分拣', '风筛',
    '筛网', '清理', '去石机', '清洗机', '清洗', '过滤', '分拣机', '脱帽', '摘柄',
    '初筛', '精筛', '除柄', '去把', '清灰', '去杂质', '去杂', '精选', '分级',
    '分离', '清选机', '分选机', '脱粒', '斜眼筛', '除杂装置', '筛筒', '筛板',
    '清除', '干洗机', '旋振筛', '去除', '切把', '除尘', '去石', '挑选', '振动筛', '去蒂机'
]

SMART_KEYWORDS = [
    '自动', '控制', '智能', '机器人', '视觉', '传感器', '算法', '自适应', '识别',
    '物联网', '监控', '调控', '电磁', '自走式', '摘除', '电子设备', '图像',
    '图像处理', '色度', '机器视觉', '自动化', '程控', '数控', '精准', '检测',
    '定位', '导航', '协同', '电磁式', '可调', '深度学习', '神经网络', '测量',
    '色选', '信号', '机械臂', '遥控', '预测模型'
]

def label_patent_dimension(keyword):
    """返回维度标签列表"""
    if pd.isna(keyword):
        return ['其他']
    labels = []
    if any(word in keyword for word in HARVEST_KEYWORDS):
        labels.append('采收')
    if any(word in keyword for word in CLEAN_KEYWORDS):
        labels.append('清杂')
    if any(word in keyword for word in SMART_KEYWORDS):
        labels.append('智能')
    if not labels:
        labels.append('其他')
    return labels

def main():
    print(f"读取文件: {INPUT_FILE}")
    df = pd.read_excel(INPUT_FILE)

    # 自动识别关键词列
    keyword_col = None
    for col in df.columns:
        if '关键词' in col or 'keyword' in col.lower():
            keyword_col = col
            break
    if keyword_col is None:
        raise ValueError(f"未找到关键词列，可用列名: {df.columns.tolist()}")
    print(f"使用关键词列: '{keyword_col}'")

    # 标注技术维度
    df['技术维度标签'] = df[keyword_col].apply(label_patent_dimension)
    df['技术维度'] = df['技术维度标签'].apply(lambda x: ';'.join(x))
    df = df.drop(columns=['技术维度标签'])

    # 保存结果
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(OUTPUT_FILE, index=False)

    print(f"已保存至: {OUTPUT_FILE}")
    print(f"共处理专利数: {len(df)}")

if __name__ == "__main__":
    main()
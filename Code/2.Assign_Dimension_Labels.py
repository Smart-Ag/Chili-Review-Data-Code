#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script 2: Patent Dimension Labelling
=====================================
Input : ../Patent_Data/2.Extracted_Keywords_883.xlsx
Output: ../Patent_Data/3.Patent_Keywords_with_Dimensions.xlsx
规则更新：
1. 不设置"其他"分类（数据均为辣椒采收/清杂相关筛选数据）
2. 先从关键词列打标签（采收/清杂/智能）
3. 若标签中无"采收/清杂"任意业务维度（仅智能或完全未匹配）：
   第一步优先匹配【标题】，命中对应词库即补充标签
   第二步若标题仍无匹配，再匹配【摘要】补充对应标签
"""
from pathlib import Path
import pandas as pd

# ===================== 路径配置 =====================
SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "Patent_Data"
INPUT_FILE = DATA_DIR / "2.Extracted_Keywords_883.xlsx"
OUTPUT_FILE = DATA_DIR / "3.Patent_Keywords_with_Dimensions.xlsx"

# ===================== 技术维度词库（和你原有词库完全一致，不改动） =====================
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


def match_text_to_keywords(text, keyword_list):
    """通用匹配函数：返回文本是否命中词库"""
    if pd.isna(text):
        return False
    text = str(text)
    return any(word in text for word in keyword_list)


def get_dimension_labels_from_keyword(keyword):
    """第一步：仅用关键词列生成初始标签"""
    labels = []
    if pd.isna(keyword):
        return labels
    # 按固定顺序：采收 → 清杂 → 智能，保证输出标签顺序统一
    if match_text_to_keywords(keyword, HARVEST_KEYWORDS):
        labels.append('采收')
    if match_text_to_keywords(keyword, CLEAN_KEYWORDS):
        labels.append('清杂')
    if match_text_to_keywords(keyword, SMART_KEYWORDS):
        labels.append('智能')
    return labels


def supplement_labels_by_title_abstract(row, title_col, abstract_col):
    """
    补充标签逻辑：
    若初始标签无采收/清杂，先查标题，标题无匹配再查摘要
    """
    current_labels = row['_temp_labels']
    # 如果已经有采收或清杂维度，不需要补充，直接返回
    if ('采收' in current_labels) or ('清杂' in current_labels):
        return current_labels

    new_labels = current_labels.copy()

    # 第一步：查标题
    title_text = row[title_col] if title_col is not None else ""
    if match_text_to_keywords(title_text, HARVEST_KEYWORDS):
        new_labels.append('采收')
    if match_text_to_keywords(title_text, CLEAN_KEYWORDS):
        new_labels.append('清杂')

    # 如果查完标题还是没有采收/清杂，再查摘要
    if not (('采收' in new_labels) or ('清杂' in new_labels)):
        abstract_text = row[abstract_col] if abstract_col is not None else ""
        if match_text_to_keywords(abstract_text, HARVEST_KEYWORDS):
            new_labels.append('采收')
        if match_text_to_keywords(abstract_text, CLEAN_KEYWORDS):
            new_labels.append('清杂')

    # 标签去重，保持固定顺序
    ordered_labels = []
    for dim in ['采收', '清杂', '智能']:
        if dim in new_labels and dim not in ordered_labels:
            ordered_labels.append(dim)
    return ordered_labels


def main():
    print(f"读取文件: {INPUT_FILE}")
    df = pd.read_excel(INPUT_FILE)

    # 自动识别三列：关键词列、标题列、摘要列
    keyword_col = None
    title_col = None
    abstract_col = None
    for col in df.columns:
        col_clean = str(col).strip()
        if '关键词' in col_clean or 'keyword' in col_clean.lower():
            keyword_col = col
        if '标题' in col_clean or 'title' in col_clean.lower():
            title_col = col
        if '摘要' in col_clean or 'abstract' in col_clean.lower():
            abstract_col = col

    # 打印识别结果，方便你核对有没有读错列
    print(f"识别到关键词列: {keyword_col}")
    print(f"识别到标题列: {title_col}")
    print(f"识别到摘要列: {abstract_col}")

    if keyword_col is None:
        raise ValueError(f"未找到关键词列，表格实际列名：{df.columns.tolist()}")
    if title_col is None and abstract_col is None:
        raise ValueError("未找到标题/摘要列，无法补充标签！")

    # 第一步：用关键词生成初始标签
    df['_temp_labels'] = df[keyword_col].apply(get_dimension_labels_from_keyword)

    # 第二步：逐行处理，对缺少采收/清杂维度的行，按标题→摘要顺序补标签
    df['_temp_labels'] = df.apply(
        lambda r: supplement_labels_by_title_abstract(r, title_col, abstract_col),
        axis=1
    )

    # 拼接为最终标签字符串
    df['技术维度'] = df['_temp_labels'].apply(lambda x: ';'.join(x))
    df = df.drop(columns=['_temp_labels'])

    # 保存结果
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_excel(OUTPUT_FILE, index=False)

    # 输出统计信息，方便你核对
    print(f"\n已保存至: {OUTPUT_FILE}")
    print(f"共处理专利总数: {len(df)}")
    print("\n==== 技术维度标签分布 ====")
    print(df['技术维度'].value_counts().to_string())

    # 打印无法匹配采收/清杂的异常行（方便你人工核对，正常应该没有）
    abnormal_rows = df[~df['技术维度'].str.contains('采收|清杂')]
    if len(abnormal_rows) > 0:
        print(f"\n==== 警告：共{len(abnormal_rows)}条数据未匹配到采收/清杂维度，请人工核对 ====")
        for idx, row in abnormal_rows.iterrows():
            print(f"专利号: {row.get('专利号(PN)', '无')}, 标题: {row.get(title_col, '无')[:50]}...")


if __name__ == "__main__":
    main()

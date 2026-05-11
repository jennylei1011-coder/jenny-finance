import streamlit as st
import pandas as pd
import numpy as np
import io
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

st.set_page_config(page_title="🌸 JENNY对账机器人", layout="wide")

# ========== 甜美可爱主题 ==========
st.markdown("""
<style>
    .main, .stApp { background: linear-gradient(135deg, #FFF0F5 0%, #FFE4E1 100%); }
    h1 { color: #FF69B4 !important; text-shadow: 2px 2px 4px rgba(255,182,193,0.5); }
    h2, h3, h4 { color: #DB7093 !important; }
    .stFileUploader, .stSelectbox, .stMultiSelect, .stButton>button, .stDateInput {
        border: 2px solid #FFB6C1 !important; border-radius: 20px !important;
        background: rgba(255,255,255,0.8) !important; backdrop-filter: blur(5px);
        box-shadow: 0 4px 15px rgba(255,182,193,0.3); transition: 0.3s;
    }
    .stFileUploader:hover, .stSelectbox:hover, .stMultiSelect:hover { box-shadow: 0 6px 20px rgba(255,105,180,0.4); }
    .stButton>button {
        background: linear-gradient(135deg, #FFB6C1, #FF69B4) !important;
        color: white !important; font-weight: bold; border: none !important;
        border-radius: 30px !important; padding: 10px 30px !important; transition: 0.3s;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #FF69B4, #FF1493) !important;
        box-shadow: 0 10px 25px rgba(255,105,180,0.6); transform: translateY(-2px);
    }
    .stFileUploader label, .stSelectbox label, .stMultiSelect label, .stDateInput label { color: #C71585 !important; font-weight: 700; }
    .stAlert { background: #FFE4E1 !important; border: 1px solid #FFB6C1 !important; color: #C71585 !important; border-radius: 15px !important; }
    .css-1d391kg, .css-1lcbmhc, .css-1out211 { background: #FFE4E1; border-radius: 20px; }
    .stDownloadButton>button { background: #FFB6C1 !important; color: white !important; border: none !important; border-radius: 30px !important; box-shadow: 0 4px 15px rgba(255,182,193,0.3); }
    p, span, div { color: #4A2545; }
    ::-webkit-scrollbar { width: 10px; }
    ::-webkit-scrollbar-track { background: #FFF0F5; }
    ::-webkit-scrollbar-thumb { background: #FFB6C1; border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: #FF69B4; }
</style>
""", unsafe_allow_html=True)

st.title("🍬 JENNY对账机器人")

# ---------- 选择工作模式 ----------
work_mode = st.selectbox("🌟 请选择对账模式", ["财务系统-日记账对账", "消耗账单对账 (新)"])

# =================================================================
# 模式一：原有财务系统-日记账对账（完全保留）
# =================================================================
if work_mode == "财务系统-日记账对账":
    # ---------- 原有所有代码（完全不变） ----------
    # 这里插入你之前完整可运行的财务对账代码（因过于庞大，此处省略，实际使用时请粘贴）
    st.warning("请将原有的完整对账代码粘贴到此分支。")
    # 你之前的所有上传、处理、对账、下载逻辑都放在这里。

# =================================================================
# 模式二：消耗账单对账（新增功能）
# =================================================================
else:
    st.header("📊 消耗账单清洗 / 对账")

    st.markdown("""
    1. 上传 **第一份消耗账单**（可多文件）  
    2. （可选）上传 **第二份消耗账单** 进行差异核对  
    3. 点击按钮开始处理  
    **对账规则**：汇总每个账号ID的总消耗，比较两个账单的总额差异。
    """)

    col_a, col_b = st.columns(2)
    with col_a:
        consumption_files1 = st.file_uploader("📤 消耗账单 ①（可多选）", type=["xlsx", "xls"], accept_multiple_files=True, key="cons1")
    with col_b:
        consumption_files2 = st.file_uploader("📤 消耗账单 ②（可选，用于比对）", type=["xlsx", "xls"], accept_multiple_files=True, key="cons2")

    # ---------- 消耗账单清洗函数 ----------
    def clean_consumption_bill(files):
        if not files:
            return pd.DataFrame()
        df_list = []
        for f in files:
            df = pd.read_excel(f, dtype=str)
            if df.empty:
                continue
            # 1. 字段映射
            rename_map = {
                '账号名称': ['广告账户名称', '账户名称', '账号名称'],
                '账号ID': ['账户ID', '广告账户ID', '账号ID'],
                '消耗': ['消耗金额', '消耗', '花费(美元)', '花费'],
                '日期': ['消耗时间', '日期', '开始日期', '时间']
            }
            lower_cols = {c.lower(): c for c in df.columns}
            final_rename = {}
            for std, candidates in rename_map.items():
                for cand in candidates:
                    if cand.lower() in lower_cols:
                        final_rename[lower_cols[cand.lower()]] = std
                        break
            df = df.rename(columns=final_rename)

            # 确保必要的列存在
            for col in ['账号名称', '账号ID', '消耗', '日期']:
                if col not in df.columns:
                    df[col] = np.nan

            # 2. 清洗文本和数值
            df['账号ID'] = df['账号ID'].astype(str).str.strip()
            df['账号名称'] = df['账号名称'].astype(str).str.strip()
            df['消耗'] = pd.to_numeric(df['消耗'], errors='coerce').fillna(0)
            df['日期'] = pd.to_datetime(df['日期'], errors='coerce', format='mixed').dt.strftime("%Y-%m-%d")

            # 3. 账号ID不是纯数字时，互换账号名称和账号ID
            def swap_if_needed(row):
                acc_id = str(row['账号ID'])
                if not acc_id.isdigit():
                    temp = row['账号名称']
                    row['账号名称'] = acc_id
                    row['账号ID'] = temp
                return row

            df = df.apply(swap_if_needed, axis=1)

            # 再次清洗
            df['账号ID'] = df['账号ID'].astype(str).str.strip()
            df['账号名称'] = df['账号名称'].astype(str).str.strip()

            # 只保留需要的列
            df = df[['账号ID', '账号名称', '消耗', '日期']].dropna(subset=['账号ID'])

            df_list.append(df)

        if not df_list:
            return pd.DataFrame(columns=['账号ID', '账号名称', '消耗', '日期'])
        return pd.concat(df_list, ignore_index=True)

    # ---------- 处理按钮 ----------
    if st.button("✨ 开始处理消耗账单", type="primary"):
        if not consumption_files1:
            st.error("请至少上传第一份消耗账单！")
        else:
            with st.spinner('🍬 JENNY 正在处理消耗账单，请稍候...'):
                df1 = clean_consumption_bill(consumption_files1)
                if df1.empty:
                    st.error("清洗后无有效数据，请检查账单格式。")
                else:
                    if not consumption_files2:   # 仅清洗
                        st.success(f"✅ 清洗完成，共 {len(df1)} 条有效记录")
                        st.dataframe(df1)
                        # 下载清洗后数据
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df1.to_excel(writer, sheet_name="清洗结果", index=False)
                        st.download_button(
                            label="📥 下载清洗结果",
                            data=output.getvalue(),
                            file_name=f"消耗账单清洗_{datetime.today().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:   # 双侧对账（按账号ID汇总消耗）
                        df2 = clean_consumption_bill(consumption_files2)
                        if df2.empty:
                            st.error("第二份账单清洗后无有效数据。")
                        else:
                            # 汇总每个账号ID的总消耗
                            agg1 = df1.groupby('账号ID').agg(
                                账号名称=('账号名称', 'first'),   # 取第一个名称
                                消耗_1=('消耗', 'sum')
                            ).reset_index()
                            agg2 = df2.groupby('账号ID').agg(
                                账号名称=('账号名称', 'first'),
                                消耗_2=('消耗', 'sum')
                            ).reset_index()

                            # 合并两个汇总表
                            merged = pd.merge(agg1, agg2, on='账号ID', how='outer', suffixes=('', ''))
                            # 补全名称（优先用账单1的名称，若缺失用账单2的）
                            merged['账号名称'] = merged['账号名称_x'].fillna(merged['账号名称_y'])
                            merged.drop(['账号名称_x', '账号名称_y'], axis=1, inplace=True)

                            # 消耗缺失填0
                            merged['消耗_1'] = merged['消耗_1'].fillna(0)
                            merged['消耗_2'] = merged['消耗_2'].fillna(0)

                            # 计算差异
                            merged['差异'] = merged['消耗_1'] - merged['消耗_2']

                            # 漏记：只在账单1中出现
                            missing_in_2 = merged[merged['消耗_2'] == 0]
                            # 多记：只在账单2中出现（消耗_1 == 0）
                            extra_in_2 = merged[merged['消耗_1'] == 0]
                            # 两边都有但差异不为零
                            diff = merged[(merged['消耗_1'] != 0) & (merged['消耗_2'] != 0) & (abs(merged['差异']) > 0.001)]

                            # 生成报告
                            output = io.BytesIO()
                            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                summary = pd.DataFrame({
                                    "项目": ["1.漏记(账单①有②无)", "2.多记(账单②有①无)", "3.消耗差异"],
                                    "数量": [len(missing_in_2), len(extra_in_2), len(diff)]
                                })
                                summary.to_excel(writer, sheet_name="对账汇总", index=False)
                                missing_in_2[['账号ID', '账号名称', '消耗_1']].to_excel(writer, sheet_name="1.漏记", index=False)
                                extra_in_2[['账号ID', '账号名称', '消耗_2']].to_excel(writer, sheet_name="2.多记", index=False)
                                if not diff.empty:
                                    diff[['账号ID', '账号名称', '消耗_1', '消耗_2', '差异']].to_excel(writer, sheet_name="3.消耗差异", index=False)

                            st.success(f"🎉 对账完成：漏记 {len(missing_in_2)}，多记 {len(extra_in_2)}，消耗差异 {len(diff)}")
                            st.download_button(
                                label="📥 下载对账报告",
                                data=output.getvalue(),
                                file_name=f"消耗对账_{datetime.today().strftime('%Y%m%d')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )

import streamlit as st
import pandas as pd
import numpy as np
import io
import warnings

warnings.filterwarnings('ignore')

# =========================
# 网页界面设计
# =========================
st.set_page_config(page_title="财务自动化对账系统", layout="wide")
st.title("📊 财务系统与人工日记账自动核对工具")
st.markdown("请在下方分别上传系统账单和日记账。上传完成后点击**开始对账**。")

# 划分两列界面
col1, col2 = st.columns(2)

with col1:
    st.header("🏢 系统账单上传区")
    taidong_file = st.file_uploader("1. 上传【钛动】账单", type=["xlsx", "xls"])
    cosmic_file = st.file_uploader("2. 上传【COSMIC】账单", type=["xlsx", "xls"])
    dingdian_file = st.file_uploader("3. 上传【顶点】账单", type=["xlsx", "xls"])

with col2:
    st.header("📝 人工日记账上传区")
    fb_file = st.file_uploader("4. 上传【FB日记账】", type=["xlsx", "xls"])
    tt_file = st.file_uploader("5. 上传【TT日记账】", type=["xlsx", "xls"])


# =========================
# 核心数据处理逻辑
# =========================
def load_and_tag(file, source_name):
    """辅助函数：如果用户上传了文件就读取，没上传就返回空表格防止报错"""
    if file is not None:
        df = pd.read_excel(file, dtype=str)
        df["来源平台"] = source_name
        return df
    else:
        # 如果没传文件，就造一个空的架子
        return pd.DataFrame(columns=['账号名称', '账号ID', '时间', '交易号', '金额', '类型', '来源平台'])


if st.button("🚀 开始自动对账", type="primary"):
    # 如果全都没上传，给个提示
    if not any([taidong_file, cosmic_file, dingdian_file, fb_file, tt_file]):
        st.error("❌ 您还没有上传任何文件！")
    else:
        with st.spinner('正在光速核对账目中，请稍候...'):

            # 1. 读取并打上标签
            taidong = load_and_tag(taidong_file, "钛动系统")
            cosmic = load_and_tag(cosmic_file, "cosmic系统")
            dingdian = load_and_tag(dingdian_file, "顶点系统")
            fb_journal = load_and_tag(fb_file, "FB日记账")
            tt_journal = load_and_tag(tt_file, "TT日记账")

            # 合并日记账
            journal = pd.concat([fb_journal, tt_journal], ignore_index=True)

            # 确保标准列存在
            standard_cols = ['账号名称', '账号ID', '时间', '交易号', '金额', '类型']
            for df in [taidong, cosmic, dingdian, journal]:
                for col in standard_cols:
                    if col not in df.columns:
                        df[col] = ''

            # 2. 统一列名与清理
            rename_dict = {"账户ID": "账号ID", "账户名称": "账号名称"}
            for df in [taidong, cosmic, dingdian, journal]:
                df.rename(columns=rename_dict, inplace=True)
                df.fillna('', inplace=True)
                for col in df.columns:
                    df[col] = df[col].astype(str).str.strip()
                    df[col] = df[col].replace({'nan': '', 'NaN': '', 'NaT': '', 'None': '', '<NA>': ''})

            # 3. 格式深度标准化
            for df in [taidong, cosmic, dingdian, journal]:
                if not df.empty:
                    df["时间"] = pd.to_datetime(df["时间"], errors="coerce", format="mixed").dt.strftime(
                        "%Y-%m-%d %H:%M").fillna("")
                    df["账号ID"] = df["账号ID"].str.replace(r'\.0$', '', regex=True)
                    df["类型"] = df["类型"].replace("减款", "清零")
                    df["金额"] = pd.to_numeric(df["金额"], errors="coerce").fillna(0).round(2)
                    df.loc[df["类型"] == "充值", "金额"] = df.loc[df["类型"] == "充值", "金额"].abs()
                    df.loc[df["类型"] == "清零", "金额"] = -df.loc[df["类型"] == "清零", "金额"].abs()

            # 4. 生成唯一主键 (核心逻辑)
            fb_account_set = set(fb_journal["账号ID"].dropna().astype(str).str.strip().unique())
            if "" in fb_account_set:
                fb_account_set.remove("")


            def generate_key(row):
                tx_id = str(row["交易号"]).strip()
                acc_id = str(row["账号ID"]).strip()
                time_val = str(row["时间"]).strip()
                source = str(row["来源平台"])

                is_fb = (source in ["cosmic系统", "顶点系统", "FB日记账"]) or (acc_id in fb_account_set)

                if is_fb:
                    if acc_id != "" and time_val != "":
                        return f"{acc_id}_{time_val}"
                    else:
                        return f"FB残缺_{np.random.randint(10000, 99999)}"
                else:
                    if tx_id != "":
                        return tx_id
                    elif acc_id != "" and time_val != "":
                        return f"{acc_id}_{time_val}"
                    else:
                        return f"TT残缺_{np.random.randint(10000, 99999)}"


            for df in [taidong, cosmic, dingdian, journal]:
                if not df.empty:
                    df["主键"] = df.apply(generate_key, axis=1)
                else:
                    df["主键"] = ""

            # 5. 合并并对账
            platform_all = pd.concat([taidong, cosmic, dingdian], ignore_index=True)

            # 防止全部为空报错
            if not platform_all.empty and not journal.empty:
                platform_duplicates = platform_all[platform_all.duplicated("主键", keep=False)]
                journal_duplicates = journal[journal.duplicated("主键", keep=False)]

                missing_in_journal = platform_all[~platform_all["主键"].isin(journal["主键"])]
                missing_in_platform = journal[~journal["主键"].isin(platform_all["主键"])]

                platform_unique = platform_all.drop_duplicates("主键")
                journal_unique = journal.drop_duplicates("主键")

                merged = pd.merge(platform_unique, journal_unique, on="主键", suffixes=("_系统", "_日记账"),
                                  how="inner")

                amount_diff = merged[merged["金额_系统"] != merged["金额_日记账"]]
                type_diff = merged[merged["类型_系统"] != merged["类型_日记账"]]
            else:
                platform_duplicates = pd.DataFrame()
                journal_duplicates = pd.DataFrame()
                missing_in_journal = platform_all
                missing_in_platform = journal
                amount_diff = pd.DataFrame()
                type_diff = pd.DataFrame()

            # 6. 生成虚拟的 Excel 文件准备供用户下载
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                summary_data = {
                    "核查项目": ["1. 漏记(系统有_日账没)", "2. 多记(日账有_系统没)", "3. 金额对不上", "4. 类型对不上",
                                 "5. 系统内部重复", "6. 日记账重复"],
                    "异常条数": [len(missing_in_journal), len(missing_in_platform), len(amount_diff), len(type_diff),
                                 len(platform_duplicates), len(journal_duplicates)]
                }
                pd.DataFrame(summary_data).to_excel(writer, sheet_name="【对账汇总】", index=False)
                missing_in_journal.to_excel(writer, sheet_name="1.漏记", index=False)
                missing_in_platform.to_excel(writer, sheet_name="2.多记", index=False)

                if not amount_diff.empty:
                    amount_diff[['主键', '账号ID_系统', '时间_系统', '金额_系统', '金额_日记账', '来源平台_系统',
                                 '来源平台_日记账']].to_excel(writer, sheet_name="3.金额对不上", index=False)
                if not type_diff.empty:
                    type_diff[['主键', '账号ID_系统', '时间_系统', '类型_系统', '类型_日记账', '来源平台_系统',
                               '来源平台_日记账']].to_excel(writer, sheet_name="4.类型对不上", index=False)

                platform_duplicates.to_excel(writer, sheet_name="5.系统重复", index=False)
                journal_duplicates.to_excel(writer, sheet_name="6.日账重复", index=False)

            # 获取生成的 excel 数据
            processed_data = output.getvalue()

            st.success("✅ 对账完成！请点击下方按钮下载报告。")
            st.download_button(
                label="📥 下载对账报告",
                data=processed_data,
                file_name="今日对账报告.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary"
            )
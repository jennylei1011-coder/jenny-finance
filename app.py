import streamlit as st
import pandas as pd
import numpy as np
import io
import warnings

warnings.filterwarnings('ignore')

st.set_page_config(page_title="财务自动化对账系统 V4", layout="wide")
st.title("📊 财务系统与人工日记账自动核对工具 V4")
st.markdown("""
**使用流程：**
1. 上传 FB / TT 客户档案（可多选文件，只需传一次，勿关闭页面）  
2. 上传系统账单（可多文件）  
3. 上传 FB / TT 日记账（可多文件）  
4. 选择对账平台范围  
5. 点击 **开始对账**
""")

# =========================
# 客户档案上传区（多文件 + 记忆）
# =========================
st.subheader("📁 客户档案（带记忆，支持多文件上传）")
st.info("⚠️ 请勿关闭浏览器标签页或手动刷新，否则需重新上传客户档案。", icon="ℹ️")

col_cus1, col_cus2 = st.columns(2)
with col_cus1:
    fb_customer_files = st.file_uploader("🔵 上传 FB 客户档案（可多选）", type=["xlsx", "xls"], accept_multiple_files=True, key="fb_customer")
with col_cus2:
    tt_customer_files = st.file_uploader("🟠 上传 TT 客户档案（可多选）", type=["xlsx", "xls"], accept_multiple_files=True, key="tt_customer")

# ---- 读取多文件并合并 ----
def load_multiple_excel(files, platform_label):
    """读取多个Excel文件并合并，添加平台标签"""
    if not files:
        return pd.DataFrame()
    frames = []
    for f in files:
        df = pd.read_excel(f, dtype=str)
        if not df.empty:
            df['来源档案平台'] = platform_label   # 内部使用，标记来自FB还是TT
            frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

# 记忆 FB 客户档案
if fb_customer_files:
    fb_customers = load_multiple_excel(fb_customer_files, "FB")
    # 检查必要列
    if not all(col in fb_customers.columns for col in ['账号ID', '账号名称']):
        st.error("❌ FB客户档案缺少“账号ID”或“账号名称”列，请检查文件。")
        st.stop()
    st.session_state["fb_customers"] = fb_customers
    st.success(f"FB客户档案已更新（共 {len(fb_customers)} 条）")
elif "fb_customers" in st.session_state:
    fb_customers = st.session_state["fb_customers"]
    st.info(f"正在使用上一次上传的 FB 客户档案（{len(fb_customers)} 条）")
else:
    fb_customers = None

# 记忆 TT 客户档案
if tt_customer_files:
    tt_customers = load_multiple_excel(tt_customer_files, "TT")
    if not all(col in tt_customers.columns for col in ['账号ID', '账号名称']):
        st.error("❌ TT客户档案缺少“账号ID”或“账号名称”列，请检查文件。")
        st.stop()
    st.session_state["tt_customers"] = tt_customers
    st.success(f"TT客户档案已更新（共 {len(tt_customers)} 条）")
elif "tt_customers" in st.session_state:
    tt_customers = st.session_state["tt_customers"]
    st.info(f"正在使用上一次上传的 TT 客户档案（{len(tt_customers)} 条）")
else:
    tt_customers = None

# =========================
# 系统账单上传区（多文件）
# =========================
st.subheader("🏢 系统账单上传区")
system_files = st.file_uploader("📤 上传系统账单（可多选，支持多工作表Excel）", type=["xlsx", "xls"], accept_multiple_files=True)

# =========================
# 日记账上传区（多文件）
# =========================
st.subheader("📝 人工日记账上传区")
col_j1, col_j2 = st.columns(2)
with col_j1:
    fb_journal_files = st.file_uploader("🔵 上传 FB 日记账（可多选）", type=["xlsx", "xls"], accept_multiple_files=True)
with col_j2:
    tt_journal_files = st.file_uploader("🟠 上传 TT 日记账（可多选）", type=["xlsx", "xls"], accept_multiple_files=True)

# =========================
# 对账范围选择
# =========================
platform_scope = st.selectbox("🔍 选择本次对账平台范围", ["全部平台", "仅 Facebook", "仅 TikTok"])

# =========================
# 核心数据处理函数
# =========================

def normalize_columns(df):
    """智能列名映射，统一为标准名称"""
    mapping = {
        '账号ID': ['账号ID', '广告账户', '账户ID', 'meta_id', 'account_id'],
        '账号名称': ['账号名称', '账户名称', 'account_name'],
        '交易号': ['交易号', '申请ID', 'transaction_id'],
        '金额': ['金额', '充值金额', '操作金额', '操作参数', 'amount_paid', 'account_amount'],
        '类型': ['操作', '类型', '操作类型', 'type'],
        '申请状态': ['申请状态', '代理状态']
    }
    rename = {}
    for std, candidates in mapping.items():
        for c in candidates:
            for col in df.columns:
                if col.lower() == c.lower():
                    rename[col] = std
                    break
    return df.rename(columns=rename)

def parse_system_bill(file):
    """解析一个系统账单文件（支持多工作表）"""
    xls = pd.ExcelFile(file)
    frames = []
    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet, dtype=str)
        if df.empty:
            continue
        df = normalize_columns(df)

        # 过滤 pending 类字段非零的行
        pending_cols = [c for c in df.columns if 'pending' in c.lower()]
        if pending_cols:
            for c in pending_cols:
                df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
            mask = (df[pending_cols] != 0).any(axis=1)
            df = df[~mask]

        # 处理 type 系统
        if '类型' in df.columns:
            df['类型_clean'] = df['类型'].str.lower().str.strip()
            allowed = ['account_topup', 'refund from ad account']
            df = df[df['类型_clean'].isin(allowed)]
            def pick_amount(row):
                t = row['类型_clean']
                if t == 'account_topup':
                    return row.get('account_amount', 0)
                elif t == 'refund from ad account':
                    return row.get('amount_paid', 0)
                return row.get('金额', 0)
            if '金额' not in df.columns:
                df['金额'] = np.nan
            df['金额'] = df.apply(pick_amount, axis=1)
            df.loc[df['类型_clean'] == 'account_topup', '类型'] = '充值'
            df.loc[df['类型_clean'] == 'refund from ad account', '类型'] = '清零'
            df.drop(columns=['类型_clean'], inplace=True)

        # 工作表名强制类型
        sheet_low = sheet.lower()
        if any(kw in sheet_low for kw in ['充值', 'topup']):
            df['类型'] = '充值'
        elif any(kw in sheet_low for kw in ['减款', '清零', 'refund']):
            df['类型'] = '清零'

        # 申请状态过滤
        if '申请状态' in df.columns:
            valid_status = df['申请状态'].str.strip().str.lower().isin(['成功', '已完成'])
            df = df[valid_status]

        frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

def load_system_bills(files):
    """加载所有系统账单文件并合并"""
    if not files:
        return pd.DataFrame()
    all_frames = []
    for f in files:
        df = parse_system_bill(f)
        if not df.empty:
            all_frames.append(df)
    return pd.concat(all_frames, ignore_index=True) if all_frames else pd.DataFrame()

def load_journal(files, source):
    """加载日记账（多文件），合并后统一打来源标签"""
    if not files:
        return pd.DataFrame()
    frames = []
    for f in files:
        df = pd.read_excel(f, dtype=str)
        if df.empty:
            continue
        df = normalize_columns(df)
        df['来源平台'] = source
        if '申请状态' in df.columns:
            df = df[df['申请状态'].str.strip().str.lower().isin(['成功', '已完成'])]
        # 类型清洗
        if '类型' in df.columns:
            df['类型'] = df['类型'].str.strip().str.lower()
            df['类型'] = df['类型'].replace({
                '减款': '清零', 'refund from ad account': '清零',
                '充值': '充值', 'account_topup': '充值'
            })
            df['类型'] = df['类型'].apply(lambda x: x if x in ['充值', '清零'] else '未知')
        # 金额
        if '金额' in df.columns:
            df['金额'] = pd.to_numeric(df['金额'], errors='coerce').fillna(0)
        else:
            df['金额'] = 0
        # 清零类取负
        df.loc[df['类型'] == '清零', '金额'] = -df.loc[df['类型'] == '清零', '金额'].abs()
        frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

def match_platform(id_val, name_val, fb_cust_dict, tt_cust_dict):
    """
    返回 (平台, 异常信息)
    同时要求ID和名称都完全匹配才认为有效
    """
    id_str = str(id_val).strip()
    name_str = str(name_val).strip()

    # 在FB档案中查找完全匹配
    fb_match = id_str in fb_cust_dict and fb_cust_dict[id_str].get('name', '').lower() == name_str.lower()
    tt_match = id_str in tt_cust_dict and tt_cust_dict[id_str].get('name', '').lower() == name_str.lower()

    if fb_match and tt_match:
        # 两边都完全匹配，通常不应该发生，我们报冲突并默认选FB
        return "FB", f"警告：账号ID {id_str} 在FB和TT档案中都存在完全匹配记录，暂时视为FB"
    elif fb_match:
        return "FB", ""
    elif tt_match:
        return "TT", ""
    else:
        # 部分匹配分析
        id_in_fb = id_str in fb_cust_dict
        id_in_tt = id_str in tt_cust_dict
        name_match_fb = any(v.get('name', '').lower() == name_str.lower() for v in fb_cust_dict.values())
        name_match_tt = any(v.get('name', '').lower() == name_str.lower() for v in tt_cust_dict.values())

        if id_in_fb and not name_match_fb:
            return None, "账号ID在FB档案中存在，但名称不匹配"
        elif id_in_tt and not name_match_tt:
            return None, "账号ID在TT档案中存在，但名称不匹配"
        elif name_match_fb and not id_in_fb:
            return None, "账号名称在FB档案中存在，但ID不匹配"
        elif name_match_tt and not id_in_tt:
            return None, "账号名称在TT档案中存在，但ID不匹配"
        else:
            return None, "账号ID和名称均未在客户档案中找到"

# =========================
# 开始对账
# =========================
if st.button("🚀 开始自动对账", type="primary"):
    # 校验
    if not system_files:
        st.error("❌ 请上传系统账单！")
    elif fb_customers is None or tt_customers is None:
        st.error("❌ 请先上传 FB 和 TT 客户档案！")
    elif not fb_journal_files and not tt_journal_files:
        st.error("❌ 请至少上传一个日记账文件！")
    else:
        with st.spinner('系统正在高速核对，请稍候...'):

            # ---------- 1. 构建客户字典 ----------
            fb_dict = {}
            for _, row in fb_customers.iterrows():
                cid = str(row['账号ID']).strip()
                cname = str(row['账号名称']).strip()
                if cid:
                    fb_dict[cid] = {'name': cname}

            tt_dict = {}
            for _, row in tt_customers.iterrows():
                cid = str(row['账号ID']).strip()
                cname = str(row['账号名称']).strip()
                if cid:
                    tt_dict[cid] = {'name': cname}

            # ---------- 2. 读取系统账单 ----------
            sys_df = load_system_bills(system_files)
            if sys_df.empty:
                st.error("系统账单经处理后无有效数据")
                st.stop()
            sys_df['来源平台'] = '系统账单'

            # ---------- 3. 读取日记账 ----------
            fb_jnl = load_journal(fb_journal_files, "FB日记账")
            tt_jnl = load_journal(tt_journal_files, "TT日记账")
            journal = pd.concat([fb_jnl, tt_jnl], ignore_index=True)

            # ---------- 4. 系统账单匹配客户档案 ----------
            matched_platforms = []
            errors = []
            for idx, row in sys_df.iterrows():
                plat, err = match_platform(row.get('账号ID', ''), row.get('账号名称', ''), fb_dict, tt_dict)
                matched_platforms.append(plat)
                if plat is None:
                    errors.append((row.get('账号ID', ''), row.get('账号名称', ''), err))

            sys_df['所属平台'] = matched_platforms

            # 异常上报
            if errors:
                st.error(f"🚨 系统账单中发现 {len(errors)} 条记录与客户档案不匹配，已剔除：")
                for e in errors[:20]:  # 最多展示20条
                    st.write(f"· 账号ID: {e[0]}, 账号名称: {e[1]} → {e[2]}")
                if len(errors) > 20:
                    st.write(f"…… 还有 {len(errors)-20} 条未展示")
                sys_df = sys_df[sys_df['所属平台'].notna()]

            if sys_df.empty:
                st.error("匹配后无有效系统记录，对账中止")
                st.stop()

            # ---------- 5. 对账范围过滤 ----------
            if platform_scope == "仅 Facebook":
                sys_df = sys_df[sys_df['所属平台'] == 'FB']
                journal = journal[journal['来源平台'] == 'FB日记账']
            elif platform_scope == "仅 TikTok":
                sys_df = sys_df[sys_df['所属平台'] == 'TT']
                journal = journal[journal['来源平台'] == 'TT日记账']

            if sys_df.empty:
                st.warning("在当前平台范围内，系统账单无数据，无法对账")
                st.stop()

            # ---------- 6. 数据清洗（时间、金额） ----------
            for df in [sys_df, journal]:
                if not df.empty:
                    if '时间' in df.columns:
                        df['时间'] = pd.to_datetime(df['时间'], errors='coerce', format='mixed').dt.strftime("%Y-%m-%d %H:%M").fillna("")
                    if '账号ID' in df.columns:
                        df['账号ID'] = df['账号ID'].astype(str).str.replace(r'\.0$', '', regex=True)
                    if '金额' in df.columns:
                        df['金额'] = pd.to_numeric(df['金额'], errors='coerce').fillna(0).round(2)
                        if '类型' in df.columns:
                            df.loc[df['类型'] == '清零', '金额'] = -df.loc[df['类型'] == '清零', '金额'].abs()
                            df.loc[df['类型'] == '充值', '金额'] = df.loc[df['类型'] == '充值', '金额'].abs()

            # ---------- 7. 生成主键 ----------
            def gen_key_sys(row):
                plat = row['所属平台']
                acc_id = str(row['账号ID']).strip()
                time_val = str(row['时间']).strip()
                tx_id = str(row.get('交易号', '')).strip()
                if plat == 'FB':
                    if acc_id and time_val:
                        return f"{acc_id}_{time_val}"
                    else:
                        return f"FB残缺_{np.random.randint(10000,99999)}"
                else:  # TT
                    if tx_id:
                        return tx_id
                    elif acc_id and time_val:
                        return f"{acc_id}_{time_val}"
                    else:
                        return f"TT残缺_{np.random.randint(10000,99999)}"

            def gen_key_jnl(row):
                src = row['来源平台']
                acc_id = str(row['账号ID']).strip()
                time_val = str(row['时间']).strip()
                tx_id = str(row.get('交易号', '')).strip()
                if src == 'FB日记账':
                    if acc_id and time_val:
                        return f"{acc_id}_{time_val}"
                    else:
                        return f"FB残缺_{np.random.randint(10000,99999)}"
                else:
                    if tx_id:
                        return tx_id
                    elif acc_id and time_val:
                        return f"{acc_id}_{time_val}"
                    else:
                        return f"TT残缺_{np.random.randint(10000,99999)}"

            sys_df['主键'] = sys_df.apply(gen_key_sys, axis=1)
            if not journal.empty:
                journal['主键'] = journal.apply(gen_key_jnl, axis=1)

            # ---------- 8. 对账 ----------
            if not journal.empty:
                sys_dup = sys_df[sys_df.duplicated('主键', keep=False)]
                jnl_dup = journal[journal.duplicated('主键', keep=False)]
                missing_in_j = sys_df[~sys_df['主键'].isin(journal['主键'])]
                missing_in_s = journal[~journal['主键'].isin(sys_df['主键'])]
                sys_u = sys_df.drop_duplicates('主键')
                jnl_u = journal.drop_duplicates('主键')
                merged = pd.merge(sys_u, jnl_u, on='主键', suffixes=('_系统', '_日记账'), how='inner')
                amt_diff = merged[merged['金额_系统'] != merged['金额_日记账']]
                typ_diff = merged[merged['类型_系统'] != merged['类型_日记账']]
            else:
                sys_dup = jnl_dup = pd.DataFrame()
                missing_in_j = sys_df
                missing_in_s = journal
                amt_diff = typ_diff = pd.DataFrame()

            # ---------- 9. 生成报告 ----------
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                summary = pd.DataFrame({
                    "核查项目": ["1.漏记(系统有日记无)", "2.多记(日记有系统无)", "3.金额不符", "4.类型不符", "5.系统重复", "6.日记账重复"],
                    "异常条数": [len(missing_in_j), len(missing_in_s), len(amt_diff), len(typ_diff), len(sys_dup), len(jnl_dup)]
                })
                summary.to_excel(writer, sheet_name="对账汇总", index=False)
                missing_in_j.to_excel(writer, sheet_name="1.漏记", index=False)
                missing_in_s.to_excel(writer, sheet_name="2.多记", index=False)
                if not amt_diff.empty:
                    amt_diff[['主键','账号ID_系统','时间_系统','金额_系统','金额_日记账']].to_excel(writer, sheet_name="3.金额不符", index=False)
                if not typ_diff.empty:
                    typ_diff[['主键','账号ID_系统','时间_系统','类型_系统','类型_日记账']].to_excel(writer, sheet_name="4.类型不符", index=False)
                sys_dup.to_excel(writer, sheet_name="5.系统重复", index=False)
                jnl_dup.to_excel(writer, sheet_name="6.日记账重复", index=False)

            st.success("✅ 对账完成！请下载报告。")
            st.download_button(
                label="📥 下载对账报告",
                data=output.getvalue(),
                file_name="对账报告.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
import streamlit as st
import pandas as pd
import numpy as np
import io
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

st.set_page_config(page_title="🌸 JENNY对账机器人", layout="wide")

# ========== 甜美可爱主题（简洁字体） ==========
st.markdown("""
<style>
    .main, .stApp {
        background: linear-gradient(135deg, #FFF0F5 0%, #FFE4E1 100%);
    }
    h1 {
        color: #FF69B4 !important;
        text-shadow: 2px 2px 4px rgba(255,182,193,0.5);
    }
    h2, h3, h4 {
        color: #DB7093 !important;
    }
    .stFileUploader, .stSelectbox, .stMultiSelect, .stButton>button, .stDateInput {
        border: 2px solid #FFB6C1 !important;
        border-radius: 20px !important;
        background: rgba(255,255,255,0.8) !important;
        backdrop-filter: blur(5px);
        box-shadow: 0 4px 15px rgba(255,182,193,0.3);
        transition: 0.3s;
    }
    .stFileUploader:hover, .stSelectbox:hover, .stMultiSelect:hover {
        box-shadow: 0 6px 20px rgba(255,105,180,0.4);
    }
    .stButton>button {
        background: linear-gradient(135deg, #FFB6C1, #FF69B4) !important;
        color: white !important;
        font-weight: bold;
        border: none !important;
        border-radius: 30px !important;
        padding: 10px 30px !important;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #FF69B4, #FF1493) !important;
        box-shadow: 0 10px 25px rgba(255,105,180,0.6);
        transform: translateY(-2px);
    }
    .stFileUploader label, .stSelectbox label, .stMultiSelect label, .stDateInput label {
        color: #C71585 !important;
        font-weight: 700;
    }
    .stAlert {
        background: #FFE4E1 !important;
        border: 1px solid #FFB6C1 !important;
        color: #C71585 !important;
        border-radius: 15px !important;
    }
    .css-1d391kg, .css-1lcbmhc, .css-1out211 {
        background: #FFE4E1;
        border-radius: 20px;
    }
    .stDownloadButton>button {
        background: #FFB6C1 !important;
        color: white !important;
        border: none !important;
        border-radius: 30px !important;
        box-shadow: 0 4px 15px rgba(255,182,193,0.3);
    }
    p, span, div {
        color: #4A2545;
    }
    ::-webkit-scrollbar { width: 10px; }
    ::-webkit-scrollbar-track { background: #FFF0F5; }
    ::-webkit-scrollbar-thumb { background: #FFB6C1; border-radius: 10px; }
    ::-webkit-scrollbar-thumb:hover { background: #FF69B4; }
</style>
""", unsafe_allow_html=True)

st.title("🍬 JENNY对账机器人")
st.markdown("""
<div style="background:#FFE4E1; padding:15px; border-radius:20px; margin-bottom:20px;">
🌸 <b>使用流程：</b><br>
1. 上传 FB / TT 客户档案（可多选，只需传一次～）<br>
2. 上传系统账单（支持多文件）<br>
3. 上传 FB / TT 日记账<br>
4. 选择时间、平台、渠道、客户（可选），然后点 <span style="color:#FF69B4;">✨ 开始对账 ✨</span>
</div>
""", unsafe_allow_html=True)

# ========== 客户档案上传区 ==========
st.subheader("📁 客户档案（带记忆，支持多文件上传）")
st.info("⚠️ 请勿关闭页面或刷新，否则需重新上传客户档案哟~", icon="🧸")

col_cus1, col_cus2 = st.columns(2)
with col_cus1:
    fb_customer_files = st.file_uploader("🔵 上传 FB 客户档案（可多选）", type=["xlsx", "xls"], accept_multiple_files=True, key="fb_customer")
with col_cus2:
    tt_customer_files = st.file_uploader("🟠 上传 TT 客户档案（可多选）", type=["xlsx", "xls"], accept_multiple_files=True, key="tt_customer")

# =========================
# 通用工具函数
# =========================
def normalize_columns(df):
    mapping = {
        '账号ID': ['账号ID', '广告账户', '账户ID', 'meta_id', 'account_id'],
        '账号名称': ['账号名称', '账户名称', 'account_name'],
        '交易号': ['交易号', '申请ID', 'transaction_id'],
        '金额': ['金额', '充值金额', '操作金额', '操作参数'],
        '类型': ['操作', '类型', '操作类型', 'type'],
        '申请状态': ['申请状态', '代理状态'],
        '时间': ['时间', '申请时间', '交易时间', '更新时间', 'created_at'],
        '渠道': ['归属广告主', '广告主', '渠道'],
        '客户': ['客户', '匹配客户', '分配客户', '客户标签']
    }
    rename = {}
    col_strs = [str(c) for c in df.columns]
    for std, candidates in mapping.items():
        for c in candidates:
            for i, col_str in enumerate(col_strs):
                if col_str.lower() == c.lower():
                    rename[df.columns[i]] = std
                    break
            else:
                continue
            break
    return df.rename(columns=rename)

def clean_text_columns(df, cols=['账号ID', '账号名称', '交易号', '渠道', '客户']):
    for col in cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip()
            df[col] = df[col].str.replace(r'\.0$', '', regex=True)
            df[col] = df[col].replace({'nan': '', 'None': '', '<NA>': ''})
    return df

def load_multiple_excel(files, platform_label):
    if not files:
        return pd.DataFrame()
    frames = []
    for f in files:
        df = pd.read_excel(f, dtype=str)
        if df.empty:
            continue
        df = normalize_columns(df)
        df['来源档案平台'] = platform_label
        frames.append(df)
    if not frames:
        return pd.DataFrame()
    df_all = pd.concat(frames, ignore_index=True)
    df_all = clean_text_columns(df_all, ['账号ID', '账号名称', '渠道', '客户'])
    return df_all

# FB客户档案记忆
if fb_customer_files:
    fb_customers = load_multiple_excel(fb_customer_files, "FB")
    if not all(col in fb_customers.columns for col in ['账号ID', '账号名称']):
        st.error("❌ FB客户档案缺少“账号ID”或“账号名称”列，请检查文件。")
        st.stop()
    if '渠道' not in fb_customers.columns:
        fb_customers['渠道'] = ''
    if '客户' not in fb_customers.columns:
        fb_customers['客户'] = ''
    st.session_state["fb_customers"] = fb_customers
    st.success(f"🌸 FB客户档案已更新（共 {len(fb_customers)} 条）")
elif "fb_customers" in st.session_state:
    fb_customers = st.session_state["fb_customers"]
    st.info(f"正在使用上一次上传的 FB 客户档案（{len(fb_customers)} 条）")
else:
    fb_customers = None

if tt_customer_files:
    tt_customers = load_multiple_excel(tt_customer_files, "TT")
    if not all(col in tt_customers.columns for col in ['账号ID', '账号名称']):
        st.error("❌ TT客户档案缺少“账号ID”或“账号名称”列，请检查文件。")
        st.stop()
    if '渠道' not in tt_customers.columns:
        tt_customers['渠道'] = ''
    if '客户' not in tt_customers.columns:
        tt_customers['客户'] = ''
    st.session_state["tt_customers"] = tt_customers
    st.success(f"🌸 TT客户档案已更新（共 {len(tt_customers)} 条）")
elif "tt_customers" in st.session_state:
    tt_customers = st.session_state["tt_customers"]
    st.info(f"正在使用上一次上传的 TT 客户档案（{len(tt_customers)} 条）")
else:
    tt_customers = None

# ========== 系统账单上传区 ==========
st.subheader("🏢 系统账单上传区")
system_files = st.file_uploader("📤 上传系统账单（可多选，支持多工作表Excel）", type=["xlsx", "xls"], accept_multiple_files=True)

# ========== 日记账上传区 ==========
st.subheader("📝 人工日记账上传区")
col_j1, col_j2 = st.columns(2)
with col_j1:
    fb_journal_files = st.file_uploader("🔵 上传 FB 日记账（可多选）", type=["xlsx", "xls"], accept_multiple_files=True)
with col_j2:
    tt_journal_files = st.file_uploader("🟠 上传 TT 日记账（可多选）", type=["xlsx", "xls"], accept_multiple_files=True)

platform_scope = st.selectbox("🔍 选择本次对账平台范围", ["全部平台", "仅 Facebook", "仅 TikTok"])

channel_options = ['全部渠道']
if fb_customers is not None or tt_customers is not None:
    all_channels = set()
    if fb_customers is not None and '渠道' in fb_customers.columns:
        all_channels.update(fb_customers['渠道'].dropna().unique())
    if tt_customers is not None and '渠道' in tt_customers.columns:
        all_channels.update(tt_customers['渠道'].dropna().unique())
    all_channels.discard('')
    taidong_set = {'北京齐风', '中顺建业', '希瑞福', '北京和海坤鑫'}
    if taidong_set & all_channels:
        channel_options.append('钛动')
    channel_options += sorted(all_channels)

selected_channels = st.multiselect(
    "📌 选择渠道（可多选，默认全部）",
    options=channel_options,
    default=['全部渠道']
)

client_options = []
if fb_customers is not None or tt_customers is not None:
    all_clients = set()
    if fb_customers is not None and '客户' in fb_customers.columns:
        all_clients.update(fb_customers['客户'].dropna().astype(str).str.strip().unique())
    if tt_customers is not None and '客户' in tt_customers.columns:
        all_clients.update(tt_customers['客户'].dropna().astype(str).str.strip().unique())
    all_clients.discard('')
    client_options = sorted(all_clients)

selected_clients = st.multiselect(
    "🧑 选择客户（可多选，默认全部）",
    options=client_options,
    default=[]
)

use_custom_date = st.checkbox("📅 启用自定义日期范围", value=False)
if use_custom_date:
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        start_date = st.date_input("开始日期")
    with col_t2:
        end_date = st.date_input("结束日期")
else:
    start_date = None
    end_date = None
    st.info("将自动使用系统账和日记账中最早的日期作为开始，最晚的日期作为结束。")

# =========================
# 系统账单处理函数
# =========================
def parse_system_bill(file):
    xls = pd.ExcelFile(file)
    frames = []
    for sheet in xls.sheet_names:
        df = pd.read_excel(xls, sheet_name=sheet, dtype=str)
        if df.empty:
            continue
        df = normalize_columns(df)
        df = clean_text_columns(df)

        is_type_system = False
        if '类型' in df.columns:
            type_vals = df['类型'].str.lower().str.strip()
            if type_vals.isin(['account_topup', 'refund from ad account']).any():
                is_type_system = True

        if is_type_system:
            df['类型_clean'] = df['类型'].str.lower().str.strip()
            allowed = ['account_topup', 'refund from ad account']
            df = df[df['类型_clean'].isin(allowed)]

            pending_cols = [c for c in df.columns if 'pending' in str(c).lower()]
            if pending_cols:
                for c in pending_cols:
                    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
                mask = (df[pending_cols] != 0).any(axis=1)
                df = df[~mask]

            if '时间' in df.columns:
                df['时间'] = df['时间'].astype(str).str.strip()
                df['时间'] = df['时间'].str.split('.').str[0]

            def pick_amount(row):
                t = row['类型_clean']
                if t == 'account_topup':
                    val = row.get('account_amount', np.nan)
                    if pd.isna(val) or str(val).strip() == '':
                        val = row.get('金额', 0)
                    return val
                elif t == 'refund from ad account':
                    val = row.get('amount_paid', np.nan)
                    if pd.isna(val) or str(val).strip() == '':
                        val = row.get('金额', 0)
                    return val
                return 0

            df['金额'] = df.apply(pick_amount, axis=1)
            df['金额'] = pd.to_numeric(df['金额'], errors='coerce').fillna(0)

            df.loc[df['类型_clean'] == 'account_topup', '类型'] = '充值'
            df.loc[df['类型_clean'] == 'refund from ad account', '类型'] = '清零'
            df.drop(columns=['类型_clean'], inplace=True)

        else:
            pending_cols = [c for c in df.columns if 'pending' in str(c).lower()]
            if pending_cols:
                for c in pending_cols:
                    df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)
                mask = (df[pending_cols] != 0).any(axis=1)
                df = df[~mask]

            sheet_low = sheet.lower()
            if any(kw in sheet_low for kw in ['充值', 'topup']):
                df['类型'] = '充值'
            elif any(kw in sheet_low for kw in ['减款', '清零', 'refund']):
                df['类型'] = '清零'

            if '金额' in df.columns:
                df['金额'] = pd.to_numeric(df['金额'], errors='coerce').fillna(0)
            else:
                df['金额'] = pd.Series(0.0, index=df.index)

        if '申请状态' in df.columns:
            valid_status = df['申请状态'].str.strip().str.lower().isin(['成功', '已完成'])
            df = df[valid_status]

        if '金额' not in df.columns:
            df['金额'] = pd.Series(0.0, index=df.index)
        df['金额'] = pd.to_numeric(df['金额'], errors='coerce').fillna(0)

        frames.append(df)

    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

def load_system_bills(files):
    if not files:
        return pd.DataFrame()
    all_frames = []
    for f in files:
        df = parse_system_bill(f)
        if not df.empty:
            all_frames.append(df)
    return pd.concat(all_frames, ignore_index=True) if all_frames else pd.DataFrame()

def load_journal(files, source):
    if not files:
        return pd.DataFrame()
    frames = []
    for f in files:
        df = pd.read_excel(f, dtype=str)
        if df.empty:
            continue
        df = normalize_columns(df)
        df = clean_text_columns(df)
        df['来源平台'] = source

        if '客户' not in df.columns:
            df['客户'] = ''

        if '申请状态' in df.columns:
            df = df[df['申请状态'].str.strip().str.lower().isin(['成功', '已完成'])]

        if '类型' in df.columns:
            df['类型'] = df['类型'].str.strip().str.lower()
            df['类型'] = df['类型'].replace({
                '减款': '清零', 'refund from ad account': '清零',
                '充值': '充值', 'account_topup': '充值'
            })
            df['类型'] = df['类型'].apply(lambda x: x if x in ['充值', '清零'] else '未知')

        if '金额' in df.columns:
            df['金额'] = pd.to_numeric(df['金额'], errors='coerce').fillna(0)
        else:
            df['金额'] = pd.Series(0.0, index=df.index)

        df.loc[df['类型'] == '清零', '金额'] = -df.loc[df['类型'] == '清零', '金额'].abs()
        frames.append(df)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

def match_platform_and_channel_and_client(id_val, name_val, fb_dict, tt_dict):
    id_str = str(id_val).strip()
    name_str = str(name_val).strip()

    fb_info = fb_dict.get(id_str)
    tt_info = tt_dict.get(id_str)

    fb_match = fb_info is not None and fb_info.get('name', '').lower() == name_str.lower()
    tt_match = tt_info is not None and tt_info.get('name', '').lower() == name_str.lower()

    if fb_match and tt_match:
        return "FB", fb_info.get('channel', ''), fb_info.get('client', ''), f"⚠️ 账号ID {id_str} 在FB和TT档案中都完全匹配，暂归为FB"
    elif fb_match:
        return "FB", fb_info.get('channel', ''), fb_info.get('client', ''), ""
    elif tt_match:
        return "TT", tt_info.get('channel', ''), tt_info.get('client', ''), ""
    else:
        return None, '', '', "账号ID或名称与客户档案不匹配，请核实信息"

# =========================
# 开始对账
# =========================
if st.button("✨ 开始自动对账", type="primary"):
    if not system_files:
        st.error("❌ 请上传系统账单！")
    elif fb_customers is None or tt_customers is None:
        st.error("❌ 请先上传 FB 和 TT 客户档案！")
    elif not fb_journal_files and not tt_journal_files:
        st.error("❌ 请至少上传一个日记账文件！")
    else:
        with st.spinner('🍬 JENNY正在甜蜜核对，请稍候...'):
            # 构建客户字典
            fb_dict = {}
            for _, row in fb_customers.iterrows():
                cid = str(row['账号ID']).strip()
                cname = str(row['账号名称']).strip()
                channel = str(row.get('渠道', '')).strip()
                client = str(row.get('客户', '')).strip()
                if cid:
                    fb_dict[cid] = {'name': cname, 'channel': channel, 'client': client, 'plat': 'FB'}
            tt_dict = {}
            for _, row in tt_customers.iterrows():
                cid = str(row['账号ID']).strip()
                cname = str(row['账号名称']).strip()
                channel = str(row.get('渠道', '')).strip()
                client = str(row.get('客户', '')).strip()
                if cid:
                    tt_dict[cid] = {'name': cname, 'channel': channel, 'client': client, 'plat': 'TT'}

            sys_df = load_system_bills(system_files)
            if sys_df.empty:
                st.error("系统账单经处理后无有效数据")
                st.stop()
            sys_df['来源平台'] = '系统账单'

            fb_jnl = load_journal(fb_journal_files, "FB日记账")
            tt_jnl = load_journal(tt_journal_files, "TT日记账")
            journal = pd.concat([fb_jnl, tt_jnl], ignore_index=True)

            # 匹配系统账
            matched_platforms = []
            match_channels = []
            match_clients = []
            errors = []
            for idx, row in sys_df.iterrows():
                plat, ch, cl, err = match_platform_and_channel_and_client(
                    row.get('账号ID', ''), row.get('账号名称', ''), fb_dict, tt_dict
                )
                matched_platforms.append(plat)
                match_channels.append(ch)
                match_clients.append(cl)
                if plat is None:
                    errors.append((row.get('账号ID', ''), row.get('账号名称', ''), err))

            sys_df['所属平台'] = matched_platforms
            sys_df['渠道'] = match_channels
            sys_df['客户'] = match_clients

            if errors:
                st.error(f"🚨 系统账单中发现 {len(errors)} 条记录与客户档案不匹配，已剔除：")
                for e in errors[:20]:
                    st.write(f"· 账号ID: {e[0]}, 账号名称: {e[1]} → {e[2]}")
                sys_df = sys_df[sys_df['所属平台'].notna()]

            if sys_df.empty:
                st.error("匹配后无有效系统记录，对账中止")
                st.stop()

            # 日记账渠道 = 客户
            if not journal.empty:
                journal['渠道'] = journal['客户'] if '客户' in journal.columns else ''
            else:
                journal = pd.DataFrame(columns=['账号ID', '账号名称', '时间', '交易号', '金额', '类型', '来源平台', '渠道', '客户'])

            # --- 调试信息：初始记录数 ---
            st.write(f"🔍 初始系统账单记录数: {len(sys_df)}，初始日记账记录数: {len(journal)}")

            # 时间范围自动计算
            if not use_custom_date:
                time_series = []
                for df in [sys_df, journal]:
                    if not df.empty and '时间' in df.columns:
                        ser = pd.to_datetime(df['时间'], errors='coerce').dropna()
                        if not ser.empty:
                            time_series.append(ser)
                if time_series:
                    all_times = pd.concat(time_series)
                    start_date = all_times.min().date()
                    end_date = all_times.max().date()
                else:
                    start_date = datetime(2026, 1, 1).date()
                    end_date = datetime.today().date()

            st.write(f"📅 使用时间范围: {start_date} 至 {end_date}")

            # 时间过滤
            for idx, df in enumerate([sys_df, journal]):
                if not df.empty and '时间' in df.columns:
                    df['时间_dt'] = pd.to_datetime(df['时间'], errors='coerce')
                    mask = (df['时间_dt'].notna()) & (df['时间_dt'].dt.date >= start_date) & (df['时间_dt'].dt.date <= end_date)
                    df = df[mask].copy()
                    df.drop(columns=['时间_dt'], inplace=True)
                    if idx == 0:
                        sys_df = df
                    else:
                        journal = df

            st.write(f"⏳ 时间过滤后：系统账单 {len(sys_df)} 条，日记账 {len(journal)} 条")

            # 渠道筛选
            if '全部渠道' not in selected_channels:
                filter_channels = set()
                taidong_set = {'北京齐风', '中顺建业', '希瑞福', '北京和海坤鑫'}
                for ch in selected_channels:
                    if ch == '钛动':
                        filter_channels.update(taidong_set)
                    else:
                        filter_channels.add(ch)
                if '渠道' in sys_df.columns:
                    sys_df = sys_df[sys_df['渠道'].isin(filter_channels)]
                if not journal.empty and '渠道' in journal.columns:
                    journal = journal[journal['渠道'].isin(filter_channels)]

            # 客户筛选
            if selected_clients:
                if '客户' in sys_df.columns:
                    sys_df = sys_df[sys_df['客户'].isin(selected_clients)]
                if not journal.empty and '客户' in journal.columns:
                    journal = journal[journal['客户'].isin(selected_clients)]

            st.write(f"🎯 渠道/客户筛选后：系统账单 {len(sys_df)} 条，日记账 {len(journal)} 条")

            # 平台范围过滤
            if platform_scope == "仅 Facebook":
                sys_df = sys_df[sys_df['所属平台'] == 'FB']
                journal = journal[journal['来源平台'] == 'FB日记账'] if not journal.empty else journal
            elif platform_scope == "仅 TikTok":
                sys_df = sys_df[sys_df['所属平台'] == 'TT']
                journal = journal[journal['来源平台'] == 'TT日记账'] if not journal.empty else journal

            st.write(f"📱 平台过滤后：系统账单 {len(sys_df)} 条，日记账 {len(journal)} 条")

            if sys_df.empty:
                st.warning("筛选后系统账单无数据，无法对账")
                st.stop()

            # 最终清洗与格式化
            for df in [sys_df, journal]:
                if not df.empty:
                    if '时间' in df.columns:
                        df['时间'] = pd.to_datetime(df['时间'], errors='coerce', format='mixed').dt.strftime("%Y-%m-%d %H:%M").fillna("")
                    if '金额' in df.columns:
                        df['金额'] = pd.to_numeric(df['金额'], errors='coerce').fillna(0).round(2)
                        if '类型' in df.columns:
                            df.loc[df['类型'] == '清零', '金额'] = -df.loc[df['类型'] == '清零', '金额'].abs()
                            df.loc[df['类型'] == '充值', '金额'] = df.loc[df['类型'] == '充值', '金额'].abs()
                    else:
                        df['金额'] = 0.0

            # 主键生成
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
                else:
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

            # 显示前几条主键示例，方便对比
            st.write("🔑 系统账单前5个主键:", list(sys_df['主键'].head(5)))
            if not journal.empty:
                st.write("🔑 日记账前5个主键:", list(journal['主键'].head(5)))

            # 对账计算
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

            # 生成报告
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

            st.success("🎉 对账完成！请下载报告～")
            st.download_button(
                label="📥 下载对账报告",
                data=output.getvalue(),
                file_name="JENNY对账报告.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # 最终统计
            if not journal.empty:
                matched_count = merged.shape[0]
                st.write(f"✅ 匹配成功 {matched_count} 条，金额不符 {len(amt_diff)} 条，类型不符 {len(typ_diff)} 条")

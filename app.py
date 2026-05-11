import streamlit as st
import pandas as pd
import numpy as np
import io
import warnings
from datetime import datetime

warnings.filterwarnings('ignore')

st.set_page_config(page_title="🌸 JENNY对账机器人", layout="wide")

# ========== 甜美可爱主题（全局） ==========
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

st.title("🍬 JENNY对账机器人 · 甜蜜版")

# ---------- 选择工作模式 ----------
work_mode = st.selectbox("🌟 请选择对账模式", ["财务系统-日记账对账", "消耗账单对账 (新)"])

# =================================================================
# 模式一：原有财务系统-日记账对账（完全保留）
# =================================================================
if work_mode == "财务系统-日记账对账":
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

    # ========== 通用工具函数 ==========
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

    def robust_clean_time(df):
        if '时间' in df.columns:
            df['时间'] = df['时间'].astype(str).str.strip()
            df['时间'] = df['时间'].str.replace(r'\s+', ' ', regex=True)
            df['时间'] = df['时间'].str.split('.').str[0]
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

    # ========== 系统账单处理函数 ==========
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

                df = robust_clean_time(df)

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
                df = robust_clean_time(df)
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

                if '类型' in df.columns:
                    df['类型'] = df['类型'].str.strip().str.lower()
                    df['类型'] = df['类型'].replace({
                        '减款': '清零',
                        'refund': '清零',
                        'topup': '充值'
                    })
                    df['类型'] = df['类型'].apply(lambda x: x if x in ['充值', '清零'] else '未知')

                if '金额' in df.columns:
                    df['金额'] = pd.to_numeric(df['金额'], errors='coerce').fillna(0)
                else:
                    df['金额'] = 0.0

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

            df = robust_clean_time(df)

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

    # ========== 开始对账 ==========
    if st.button("✨ 开始自动对账", type="primary"):
        if not system_files:
            st.error("❌ 请上传系统账单！")
        elif fb_customers is None or tt_customers is None:
            st.error("❌ 请先上传 FB 和 TT 客户档案！")
        elif not fb_journal_files and not tt_journal_files:
            st.error("❌ 请至少上传一个日记账文件！")
        else:
            with st.spinner('🍬 JENNY正在核对，请稍候...'):
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

                def get_channel_from_dict(acc_id):
                    acc_str = str(acc_id).strip()
                    if acc_str in fb_dict:
                        return fb_dict[acc_str].get('channel', '')
                    elif acc_str in tt_dict:
                        return tt_dict[acc_str].get('channel', '')
                    return ''

                def get_client_from_dict(acc_id):
                    acc_str = str(acc_id).strip()
                    if acc_str in fb_dict:
                        return fb_dict[acc_str].get('client', '')
                    elif acc_str in tt_dict:
                        return tt_dict[acc_str].get('client', '')
                    return ''

                if not journal.empty:
                    journal['渠道'] = journal['账号ID'].apply(get_channel_from_dict)
                    if '客户' in journal.columns:
                        mask_empty = journal['客户'].isna() | (journal['客户'] == '')
                        journal.loc[mask_empty, '客户'] = journal.loc[mask_empty, '账号ID'].apply(get_client_from_dict)
                    else:
                        journal['客户'] = journal['账号ID'].apply(get_client_from_dict)
                else:
                    journal = pd.DataFrame(columns=['账号ID', '账号名称', '时间', '交易号', '金额', '类型', '来源平台', '渠道', '客户'])

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

                if sys_df.empty:
                    st.warning("筛选时间范围后，系统账单无数据，无法对账")
                    st.stop()

                if '全部渠道' not in selected_channels and len(selected_channels) > 0:
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

                if sys_df.empty:
                    st.warning("筛选渠道后，系统账单无数据，无法对账")
                    st.stop()

                if selected_clients:
                    if '客户' in sys_df.columns:
                        sys_df = sys_df[sys_df['客户'].isin(selected_clients)]
                    if not journal.empty and '客户' in journal.columns:
                        journal = journal[journal['客户'].isin(selected_clients)]

                if sys_df.empty:
                    st.warning("筛选客户后，系统账单无数据，无法对账")
                    st.stop()

                if platform_scope == "仅 Facebook":
                    sys_df = sys_df[sys_df['所属平台'] == 'FB']
                    journal = journal[journal['来源平台'] == 'FB日记账'] if not journal.empty else journal
                elif platform_scope == "仅 TikTok":
                    sys_df = sys_df[sys_df['所属平台'] == 'TT']
                    journal = journal[journal['来源平台'] == 'TT日记账'] if not journal.empty else journal

                if sys_df.empty:
                    st.warning("在当前平台范围内，系统账单无数据，无法对账")
                    st.stop()

                for df in [sys_df, journal]:
                    if not df.empty:
                        if '时间' in df.columns:
                            df['时间'] = pd.to_datetime(df['时间'], errors='coerce', format='mixed').dt.strftime("%Y-%m-%d %H:%M").fillna("")
                        if '金额' in df.columns:
                            df['金额'] = pd.to_numeric(df['金额'], errors='coerce').fillna(0).round(2)
                        else:
                            df['金额'] = 0.0

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

                if not journal.empty:
                    sys_dup = sys_df[sys_df.duplicated('主键', keep=False)]
                    jnl_dup = journal[journal.duplicated('主键', keep=False)]
                    missing_in_j = sys_df[~sys_df['主键'].isin(journal['主键'])]
                    missing_in_s = journal[~journal['主键'].isin(sys_df['主键'])]
                    sys_u = sys_df.drop_duplicates('主键')
                    jnl_u = journal.drop_duplicates('主键')
                    merged = pd.merge(sys_u, jnl_u, on='主键', suffixes=('_系统', '_日记账'), how='inner')

                    def is_amount_match(row):
                        a_sys = row['金额_系统']
                        a_jnl = row['金额_日记账']
                        t_sys = row['类型_系统']
                        t_jnl = row['类型_日记账']
                        if t_sys != t_jnl:
                            return True
                        if t_sys == '清零':
                            return abs(a_sys - a_jnl) < 0.001
                        else:
                            return abs(a_sys - a_jnl) < 0.001

                    merged['_amt_match'] = merged.apply(is_amount_match, axis=1)
                    amt_diff = merged[~merged['_amt_match']]
                    merged.drop(columns=['_amt_match'], inplace=True)

                    typ_diff = merged[merged['类型_系统'] != merged['类型_日记账']]
                else:
                    sys_dup = jnl_dup = pd.DataFrame()
                    missing_in_j = sys_df
                    missing_in_s = journal
                    amt_diff = typ_diff = pd.DataFrame()

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

                today_str = datetime.today().strftime("%Y%m%d")
                client_str = "_".join(selected_clients) if selected_clients else "全部客户"
                if '全部渠道' in selected_channels or not selected_channels:
                    channel_str = "全部渠道"
                else:
                    channel_str = "_".join(selected_channels)
                if platform_scope == "全部平台":
                    plat_str = "全部平台"
                else:
                    plat_str = platform_scope.replace("仅 ", "")
                report_name = f"{client_str}-{channel_str}-{plat_str}-{today_str}对账报告.xlsx"

                st.success("🎉 对账完成！请下载报告～")
                st.download_button(
                    label="📥 下载对账报告",
                    data=output.getvalue(),
                    file_name=report_name,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

# =================================================================
# 模式二：消耗账单对账（新增客户档案匹配 + 客户选择）
# =================================================================
else:
    st.header("📊 消耗账单清洗 / 对账")

    st.markdown("""
    1. 上传 **FB / TT 客户档案**（可选，用于标注平台和客户）  
    2. 上传 **第一份消耗账单**（可多文件）  
    3. （可选）上传 **第二份消耗账单** 进行差异核对  
    4. 选择客户（需先上传档案），点击按钮开始处理  
    **对账规则**：汇总每个账号ID的总消耗，比较两个账单的总额差异。
    """)

    # ----- 客户档案上传（消耗对账专用） -----
    st.subheader("📁 客户档案（可选，用于匹配平台和客户）")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        cons_fb_files = st.file_uploader("🔵 FB 客户档案", type=["xlsx", "xls"], accept_multiple_files=True, key="cons_fb_cus")
    with col_c2:
        cons_tt_files = st.file_uploader("🟠 TT 客户档案", type=["xlsx", "xls"], accept_multiple_files=True, key="cons_tt_cus")

    # 读取并记忆客户档案
    def load_cons_customer(files, plat):
        if not files:
            return pd.DataFrame()
        frames = []
        for f in files:
            df = pd.read_excel(f, dtype=str)
            if df.empty:
                continue
            # 标准化列名
            rename_map = {
                '账号ID': ['账号ID', '广告账户', '账户ID', 'meta_id', 'account_id'],
                '账号名称': ['账号名称', '账户名称', 'account_name'],
                '渠道': ['归属广告主', '广告主', '渠道'],
                '客户': ['客户', '匹配客户', '分配客户', '客户标签']
            }
            lower_cols = {c.lower(): c for c in df.columns}
            final_rename = {}
            for std, candidates in rename_map.items():
                for cand in candidates:
                    if cand.lower() in lower_cols:
                        final_rename[lower_cols[cand.lower()]] = std
                        break
            df = df.rename(columns=final_rename)
            for col in ['账号ID', '账号名称']:
                if col not in df.columns:
                    df[col] = ''
            df['账号ID'] = df['账号ID'].astype(str).str.strip()
            df['账号名称'] = df['账号名称'].astype(str).str.strip()
            df['平台'] = plat
            frames.append(df)
        if not frames:
            return pd.DataFrame(columns=['账号ID', '账号名称', '渠道', '客户', '平台'])
        return pd.concat(frames, ignore_index=True)

    if cons_fb_files or 'cons_fb_customers' in st.session_state:
        if cons_fb_files:
            fb_cus = load_cons_customer(cons_fb_files, "FB")
            st.session_state['cons_fb_customers'] = fb_cus
        else:
            fb_cus = st.session_state['cons_fb_customers']
    else:
        fb_cus = pd.DataFrame()

    if cons_tt_files or 'cons_tt_customers' in st.session_state:
        if cons_tt_files:
            tt_cus = load_cons_customer(cons_tt_files, "TT")
            st.session_state['cons_tt_customers'] = tt_cus
        else:
            tt_cus = st.session_state['cons_tt_customers']
    else:
        tt_cus = pd.DataFrame()

    # 合并客户档案字典
    customer_dict = {}
    all_client_options = set()
    if not fb_cus.empty:
        for _, row in fb_cus.iterrows():
            cid = row['账号ID']
            if cid:
                customer_dict[cid] = {
                    '平台': 'FB',
                    '客户': row.get('客户', ''),
                    '渠道': row.get('渠道', '')
                }
                if row.get('客户', ''):
                    all_client_options.add(row['客户'])
    if not tt_cus.empty:
        for _, row in tt_cus.iterrows():
            cid = row['账号ID']
            if cid:
                customer_dict[cid] = {
                    '平台': 'TT',
                    '客户': row.get('客户', ''),
                    '渠道': row.get('渠道', '')
                }
                if row.get('客户', ''):
                    all_client_options.add(row['客户'])

    # 显示档案加载情况
    total_customers = len(customer_dict)
    if total_customers > 0:
        st.success(f"🌸 已加载客户档案，共 {total_customers} 个账号ID")
    else:
        st.info("未上传客户档案，将不标注平台和客户")

    # 客户选择（仅在有档案时显示）
    client_options = sorted(list(all_client_options))
    if client_options:
        selected_clients_cons = st.multiselect(
            "🧑 选择要核对的客户（可多选，默认全部）",
            options=client_options,
            default=[]
        )
    else:
        selected_clients_cons = []
        if total_customers > 0:
            st.info("档案中未找到客户信息，无法按客户筛选")
        else:
            st.info("上传档案后，这里可以选择特定客户进行核对")

    # 消耗账单上传区
    col_a, col_b = st.columns(2)
    with col_a:
        consumption_files1 = st.file_uploader("📤 消耗账单 ①（可多选）", type=["xlsx", "xls"], accept_multiple_files=True, key="cons1")
    with col_b:
        consumption_files2 = st.file_uploader("📤 消耗账单 ②（可选，用于比对）", type=["xlsx", "xls"], accept_multiple_files=True, key="cons2")

    def clean_consumption_bill(files):
        """清洗消耗账单，返回DataFrame包含：账号ID、账号名称、消耗、日期、平台、客户"""
        if not files:
            return pd.DataFrame()
        df_list = []
        for f in files:
            df = pd.read_excel(f, dtype=str)
            if df.empty:
                continue
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

            for col in ['账号名称', '账号ID', '消耗', '日期']:
                if col not in df.columns:
                    df[col] = np.nan

            df['账号ID'] = df['账号ID'].astype(str).str.strip()
            df['账号名称'] = df['账号名称'].astype(str).str.strip()
            df['消耗'] = pd.to_numeric(df['消耗'], errors='coerce').fillna(0)
            df['日期'] = pd.to_datetime(df['日期'], errors='coerce', format='mixed').dt.strftime("%Y-%m-%d")

            # 若账号ID列不是纯数字，与账号名称互换
            def swap_if_needed(row):
                acc_id = str(row['账号ID'])
                if not acc_id.isdigit():
                    temp = row['账号名称']
                    row['账号名称'] = acc_id
                    row['账号ID'] = temp
                return row

            df = df.apply(swap_if_needed, axis=1)
            df['账号ID'] = df['账号ID'].astype(str).str.strip()
            df['账号名称'] = df['账号名称'].astype(str).str.strip()

            # 匹配平台和客户
            df['平台'] = df['账号ID'].map(lambda x: customer_dict.get(x, {}).get('平台', '未知') if customer_dict else '未上传档案')
            df['客户'] = df['账号ID'].map(lambda x: customer_dict.get(x, {}).get('客户', '') if customer_dict else '')
            df = df[['账号ID', '账号名称', '消耗', '日期', '平台', '客户']].dropna(subset=['账号ID'])
            df_list.append(df)

        if not df_list:
            return pd.DataFrame(columns=['账号ID', '账号名称', '消耗', '日期', '平台', '客户'])
        return pd.concat(df_list, ignore_index=True)

    if st.button("✨ 开始处理消耗账单", type="primary"):
        if not consumption_files1:
            st.error("请至少上传第一份消耗账单！")
        else:
            with st.spinner('🍬 JENNY 正在甜蜜处理消耗账单，请稍候...'):
                df1 = clean_consumption_bill(consumption_files1)
                if df1.empty:
                    st.error("清洗后无有效数据，请检查账单格式。")
                else:
                    # 根据所选客户过滤（如果选择了客户）
                    if selected_clients_cons:
                        df1 = df1[df1['客户'].isin(selected_clients_cons)]
                        if df1.empty:
                            st.warning("筛选客户后，第一份账单无数据，请重新选择客户或检查账单。")
                            st.stop()

                    if not consumption_files2:
                        st.success(f"✅ 清洗完成，共 {len(df1)} 条有效记录")
                        st.dataframe(df1)
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df1.to_excel(writer, sheet_name="清洗结果", index=False)
                        st.download_button(
                            label="📥 下载清洗结果",
                            data=output.getvalue(),
                            file_name=f"消耗账单清洗_{datetime.today().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    else:
                        df2 = clean_consumption_bill(consumption_files2)
                        if df2.empty:
                            st.error("第二份账单清洗后无有效数据。")
                        else:
                            # 同样按客户过滤第二份
                            if selected_clients_cons:
                                df2 = df2[df2['客户'].isin(selected_clients_cons)]
                                if df2.empty:
                                    st.warning("筛选客户后，第二份账单无数据，无法比对。")
                                    st.stop()

                            # 汇总每个账号ID的总消耗，并保留平台和客户
                            agg1 = df1.groupby('账号ID').agg(
                                账号名称=('账号名称', 'first'),
                                消耗_1=('消耗', 'sum'),
                                平台=('平台', 'first'),
                                客户=('客户', 'first')
                            ).reset_index()
                            agg2 = df2.groupby('账号ID').agg(
                                账号名称=('账号名称', 'first'),
                                消耗_2=('消耗', 'sum'),
                                平台=('平台', 'first'),
                                客户=('客户', 'first')
                            ).reset_index()

                            merged = pd.merge(agg1, agg2, on='账号ID', how='outer', suffixes=('_x', '_y'))
                            # 合并平台和客户字段
                            merged['平台'] = merged['平台_x'].fillna(merged['平台_y'])
                            merged['客户'] = merged['客户_x'].fillna(merged['客户_y'])
                            merged['账号名称'] = merged['账号名称_x'].fillna(merged['账号名称_y'])
                            merged.drop(['平台_x', '平台_y', '客户_x', '客户_y', '账号名称_x', '账号名称_y'], axis=1, inplace=True)

                            merged['消耗_1'] = merged['消耗_1'].fillna(0)
                            merged['消耗_2'] = merged['消耗_2'].fillna(0)
                            merged['差异'] = merged['消耗_1'] - merged['消耗_2']

                            missing_in_2 = merged[merged['消耗_2'] == 0]
                            extra_in_2 = merged[merged['消耗_1'] == 0]
                            diff = merged[(merged['消耗_1'] != 0) & (merged['消耗_2'] != 0) & (abs(merged['差异']) > 0.001)]

                            output = io.BytesIO()
                            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                summary = pd.DataFrame({
                                    "项目": ["1.漏记(账单①有②无)", "2.多记(账单②有①无)", "3.消耗差异"],
                                    "数量": [len(missing_in_2), len(extra_in_2), len(diff)]
                                })
                                summary.to_excel(writer, sheet_name="对账汇总", index=False)
                                cols_out = ['账号ID', '账号名称', '平台', '客户']
                                missing_in_2[cols_out + ['消耗_1']].to_excel(writer, sheet_name="1.漏记", index=False)
                                extra_in_2[cols_out + ['消耗_2']].to_excel(writer, sheet_name="2.多记", index=False)
                                if not diff.empty:
                                    diff[cols_out + ['消耗_1', '消耗_2', '差异']].to_excel(writer, sheet_name="3.消耗差异", index=False)

                            st.success(f"🎉 对账完成：漏记 {len(missing_in_2)}，多记 {len(extra_in_2)}，消耗差异 {len(diff)}")
                            st.download_button(
                                label="📥 下载对账报告",
                                data=output.getvalue(),
                                file_name=f"消耗对账_{datetime.today().strftime('%Y%m%d')}.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                            )

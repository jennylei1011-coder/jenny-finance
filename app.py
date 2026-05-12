import streamlit as st
import pandas as pd
import numpy as np
import io
import warnings
import base64
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from PIL import Image

warnings.filterwarnings('ignore')

APP_DIR = Path(__file__).resolve().parent
ASSET_DIR = APP_DIR / "assets"
TOP_LOGO_PATH = ASSET_DIR / "top-logo.png"
PAGE_ICON_PATH = ASSET_DIR / "favicon.png"

try:
    page_icon = Image.open(PAGE_ICON_PATH) if PAGE_ICON_PATH.exists() else None
except Exception:
    page_icon = None

st.set_page_config(page_title="JENNY对账机器人", page_icon=page_icon, layout="wide")

def image_data_uri(path):
    if not path.exists():
        return ""
    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:image/png;base64,{encoded}"

# ========== 粉色系简洁主题（全局） ==========
st.markdown("""
<style>
    :root {
        --pink-25: #fff9fc;
        --pink-50: #fff2f7;
        --pink-100: #ffe4ee;
        --pink-200: #ffc8dc;
        --pink-400: #ef6f9f;
        --pink-500: #d94f86;
        --pink-600: #bf3d72;
        --ink: #352631;
        --muted: #7f6370;
        --line: rgba(217, 79, 134, 0.16);
        --panel: rgba(255, 255, 255, 0.78);
        --shadow: 0 14px 36px rgba(163, 67, 108, 0.12);
    }

    .stApp {
        background:
            radial-gradient(circle at 6% 2%, rgba(255, 210, 226, 0.72), transparent 24rem),
            radial-gradient(circle at 96% 0%, rgba(255, 235, 244, 0.92), transparent 28rem),
            linear-gradient(135deg, #fffafd 0%, #fff4f8 42%, #fff0f6 100%);
        color: var(--ink);
    }

    .block-container {
        max-width: 1220px;
        padding-top: 1rem;
        padding-bottom: 2rem;
    }

    header[data-testid="stHeader"], footer, #MainMenu {
        visibility: hidden;
    }

    .app-hero {
        position: relative;
        overflow: hidden;
        display: grid;
        grid-template-columns: auto 1fr;
        align-items: center;
        gap: 18px;
        background: rgba(255, 255, 255, 0.72);
        backdrop-filter: blur(16px);
        border: 1px solid var(--line);
        border-radius: 22px;
        padding: 16px 20px;
        margin-bottom: 12px;
        box-shadow: var(--shadow);
    }

    .app-hero:after {
        content: "";
        position: absolute;
        right: -120px;
        top: -150px;
        width: 320px;
        height: 320px;
        background: radial-gradient(circle, rgba(239, 111, 159, 0.15), transparent 64%);
        pointer-events: none;
    }

    .app-hero > * {
        position: relative;
        z-index: 1;
    }

    .hero-logo {
        display: block;
        width: 74px;
        height: 74px;
        object-fit: contain;
        filter: drop-shadow(0 10px 16px rgba(217, 79, 134, 0.18));
    }

    .hero-kicker {
        color: var(--pink-600);
        font-size: 0.74rem;
        font-weight: 800;
        letter-spacing: .08em !important;
        margin-bottom: 3px;
    }

    .hero-title {
        color: var(--ink);
        font-size: 1.62rem;
        line-height: 1.12;
        font-weight: 850;
        margin: 0;
    }

    .hero-subtitle {
        color: var(--muted);
        max-width: 820px;
        margin: 5px 0 0;
        line-height: 1.55;
        font-size: 0.92rem;
    }

    .guide-card {
        background: rgba(255,255,255,0.62);
        border: 1px solid var(--line);
        border-radius: 18px;
        padding: 12px 14px;
        margin: 8px 0 12px;
        box-shadow: 0 8px 22px rgba(177, 77, 116, 0.08);
    }

    .guide-title {
        color: var(--pink-600);
        font-weight: 850;
        margin-bottom: 8px;
        font-size: 0.96rem;
    }

    .guide-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 8px;
    }

    .guide-step {
        min-height: 54px;
        background: #fffafd;
        border: 1px solid rgba(255, 200, 220, 0.74);
        border-radius: 13px;
        padding: 9px 10px;
        color: var(--muted);
        line-height: 1.42;
        font-size: 0.86rem;
    }

    .guide-step b {
        display: block;
        color: var(--ink);
        margin-bottom: 2px;
        font-size: 0.88rem;
    }

    .hint-card {
        background: rgba(255, 250, 253, 0.92);
        border: 1px solid rgba(217, 79, 134, 0.13);
        border-left: 4px solid var(--pink-400);
        border-radius: 13px;
        padding: 9px 11px;
        margin: 6px 0 10px;
        color: var(--muted);
        line-height: 1.55;
        font-size: 0.88rem;
    }

    .hint-card b { color: var(--ink); }

    .field-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 8px;
        margin-top: 8px;
    }

    .field-box {
        background: #fffafd;
        border: 1px solid rgba(255, 200, 220, 0.72);
        border-radius: 12px;
        padding: 9px 10px;
        min-height: 68px;
        color: var(--muted);
        line-height: 1.48;
        font-size: 0.84rem;
    }

    .field-box b {
        display: block;
        color: var(--pink-600);
        margin-bottom: 4px;
    }

    .field-box code {
        background: rgba(255, 228, 238, 0.76);
        color: var(--ink);
        border-radius: 7px;
        padding: 1px 5px;
        font-size: 0.78rem;
        display: inline-block;
        margin: 1px 2px 2px 0;
    }

    .section-title {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 16px 0 8px;
    }

    .section-title .dot {
        width: 8px;
        height: 22px;
        border-radius: 999px;
        background: linear-gradient(180deg, var(--pink-500), var(--pink-200));
        box-shadow: 0 8px 18px rgba(239, 111, 159, 0.24);
    }

    .section-title h2 {
        color: var(--ink) !important;
        font-size: 1.02rem !important;
        line-height: 1.25;
        margin: 0 !important;
        padding: 0 !important;
        border: 0 !important;
    }

    .section-title p {
        color: var(--muted);
        margin: 1px 0 0;
        font-size: 0.82rem;
    }

    h1, h2, h3, h4, p, span, div, label {
        letter-spacing: 0 !important;
    }

    h1, h2, h3, h4 { color: var(--ink) !important; }

    .stFileUploader, .stSelectbox, .stMultiSelect, .stDateInput, .stCheckbox, .stRadio {
        background: rgba(255, 255, 255, 0.68);
        border: 1px solid var(--line);
        border-radius: 16px;
        padding: 8px 10px;
        box-shadow: 0 6px 18px rgba(177, 77, 116, 0.06);
    }

    .stFileUploader:hover, .stSelectbox:hover, .stMultiSelect:hover, .stDateInput:hover {
        border-color: rgba(217, 79, 134, 0.38);
        box-shadow: 0 8px 22px rgba(177, 77, 116, 0.10);
    }

    .stFileUploader label, .stSelectbox label, .stMultiSelect label, .stDateInput label, .stCheckbox label, .stRadio label {
        color: var(--ink) !important;
        font-weight: 750;
        font-size: 0.9rem;
    }

    div[data-testid="stFileUploaderDropzone"] {
        min-height: 74px !important;
        border-radius: 14px !important;
        border-color: rgba(217, 79, 134, 0.20) !important;
        background: #fffafd !important;
        padding: 8px !important;
    }

    div[data-testid="stFileUploaderDropzone"] section {
        padding: 0.35rem !important;
    }

    div[data-testid="stFileUploaderDropzone"] small {
        display: none !important;
    }

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div {
        border-radius: 12px !important;
        border-color: rgba(217, 79, 134, 0.22) !important;
        background-color: rgba(255,255,255,0.94) !important;
        min-height: 38px !important;
    }

    .stButton > button, .stDownloadButton > button {
        width: 100%;
        min-height: 44px;
        border: 0 !important;
        border-radius: 999px !important;
        background: linear-gradient(135deg, var(--pink-600), var(--pink-400)) !important;
        color: white !important;
        font-weight: 850 !important;
        box-shadow: 0 12px 26px rgba(217, 79, 134, 0.25);
        transition: transform 160ms ease, box-shadow 160ms ease, filter 160ms ease;
    }

    .stButton > button:hover, .stDownloadButton > button:hover {
        transform: translateY(-1px);
        filter: brightness(1.02);
        box-shadow: 0 16px 34px rgba(217, 79, 134, 0.30);
    }

    .stAlert {
        border-radius: 14px !important;
        border: 1px solid var(--line) !important;
        background: rgba(255, 250, 253, 0.92) !important;
        color: var(--ink) !important;
        padding: 0.75rem 1rem !important;
    }

    .stDataFrame {
        border: 1px solid var(--line);
        border-radius: 14px;
        overflow: hidden;
    }

    details {
        background: rgba(255,255,255,0.46);
        border: 1px dashed rgba(217,79,134,0.20);
        border-radius: 13px;
        padding: 8px 10px;
        margin-bottom: 8px;
    }

    summary {
        list-style: none;
    }

    summary::-webkit-details-marker { display: none; }

    div[data-testid="stVerticalBlock"] { gap: 0.55rem; }

    ::-webkit-scrollbar { width: 9px; height: 9px; }
    ::-webkit-scrollbar-track { background: var(--pink-50); }
    ::-webkit-scrollbar-thumb { background: var(--pink-200); border-radius: 999px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--pink-400); }

    @media (max-width: 760px) {
        .block-container { padding-top: 0.8rem; }
        .app-hero {
            grid-template-columns: 1fr;
            text-align: center;
            padding: 16px;
        }
        .hero-logo { width: 78px; height: 78px; margin: 0 auto; }
        .hero-title { font-size: 1.42rem; }
        .guide-grid { grid-template-columns: 1fr; }
        .field-grid { grid-template-columns: 1fr; }
    }
</style>
""", unsafe_allow_html=True)

def section_title(title, subtitle=""):
    st.markdown(
        f"""
        <div class="section-title">
            <div class="dot"></div>
            <div>
                <h2>{title}</h2>
                <p>{subtitle}</p>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def guide_card(title, steps):
    step_html = "".join(
        f'<div class="guide-step"><b>{idx}. {step[0]}</b>{step[1]}</div>'
        for idx, step in enumerate(steps, start=1)
    )
    st.markdown(
        f"""
        <div class="guide-card">
            <div class="guide-title">{title}</div>
            <div class="guide-grid">{step_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

def hint_card(text):
    st.markdown(f'<div class="hint-card">{text}</div>', unsafe_allow_html=True)

def field_requirements(title, required, optional=None, aliases=None, note=None):
    optional = optional or []
    aliases = aliases or []

    def code_items(items):
        return " ".join(f"<code>{item}</code>" for item in items)

    blocks = [
        f'<div class="field-box"><b>必填字段</b>{code_items(required)}</div>',
        f'<div class="field-box"><b>可选字段</b>{code_items(optional) if optional else "没有也可以继续处理"}</div>',
        f'<div class="field-box"><b>可识别别名</b>{code_items(aliases) if aliases else "字段名尽量保持清晰即可"}</div>',
    ]
    note_html = f'<div class="hint-card"><b>小提示：</b>{note}</div>' if note else ""
    st.markdown(
        f"""
        <details>
            <summary style="cursor:pointer; color:#db4b87; font-weight:800; margin:6px 0 10px;">查看{title}字段要求</summary>
            <div class="field-grid">{''.join(blocks)}</div>
            {note_html}
        </details>
        """,
        unsafe_allow_html=True,
    )

top_logo_uri = image_data_uri(TOP_LOGO_PATH)
logo_html = f'<img class="hero-logo" src="{top_logo_uri}" alt="JENNY logo">' if top_logo_uri else ""

st.markdown(f"""
<div class="app-hero">
    {logo_html}
    <div>
        <div class="hero-kicker">JENNY FINANCE WORKSPACE</div>
        <h1 class="hero-title">JENNY 对账机器人</h1>
        <p class="hero-subtitle">粉色系高级财务工具台｜上传账单、筛选范围、自动核对、导出 Excel 报告。</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------- 选择工作模式 ----------
work_mode = st.radio(
    "选择对账模式",
    ["财务系统-日记账对账", "消耗账单对账 (新)"],
    horizontal=True,
)

# =================================================================
# 模式一：原有财务系统-日记账对账（持久化下载按钮）
# =================================================================
if work_mode == "财务系统-日记账对账":
    guide_card(
        "财务系统 - 日记账对账流程",
        [
            ("客户档案", "上传 FB / TT 客户档案，可多选，页面打开期间会记住。"),
            ("系统账单", "上传系统账单，支持多文件和多工作表 Excel。"),
            ("人工日记账", "分别上传 FB / TT 日记账，系统会自动清洗字段。"),
            ("筛选导出", "选择时间、平台、渠道、客户后生成对账报告。"),
        ],
    )

    # ========== 客户档案上传区 ==========
    section_title("客户档案", "上传 FB / TT 档案，用于匹配账号、渠道和客户。")
    hint_card("<b>上传前确认：</b>客户档案只需要上传 Excel 文件；暂不支持从截图识别字段。页面刷新后需要重新上传。")
    field_requirements(
        "客户档案",
        required=["账号ID", "账号名称"],
        optional=["渠道", "客户"],
        aliases=["广告账户", "账户ID", "meta_id", "account_id", "账户名称", "account_name", "归属广告主", "广告主"],
        note="按本次对账平台上传对应档案：仅 Facebook 可只传 FB，仅 TikTok 可只传 TT，全部平台需要两份都上传；重复分配会在报告中列出并提示核实。",
    )

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
            '金额': ['金额', '充值金额', '操作金额', '操作参数', '参数', 'amount', 'account_amount', 'amount_paid'],
            '类型': ['操作', '类型', '操作类型', 'operation_type', 'type'],
            '申请状态': ['申请状态', '代理状态', '处理状态'],
            '时间': ['更新时间', '时间', '交易时间', '申请时间', '提交时间', 'created_at'],
            '渠道': ['归属广告主', '广告主', '渠道'],
            '客户': ['客户', '匹配客户', '分配客户', '客户标签']
        }
        rename = {}
        def normalize_col_name(value):
            return str(value).strip().lower().replace(' ', '').replace('\n', '').replace('\r', '')

        col_strs = [normalize_col_name(c) for c in df.columns]
        for std, candidates in mapping.items():
            for c in candidates:
                cand = normalize_col_name(c)
                for i, col_str in enumerate(col_strs):
                    if col_str == cand:
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
                if col == '账号ID':
                    df[col] = df[col].apply(normalize_id_text)
                else:
                    df[col] = df[col].str.replace(r'\.0$', '', regex=True)
                df[col] = df[col].replace({'nan': '', 'None': '', '<NA>': ''})
        return df

    def normalize_id_text(value):
        text = str(value).strip()
        if text.lower() in {'', 'nan', 'none', '<na>'}:
            return ''
        text = text.replace(',', '').replace(' ', '')
        try:
            if any(mark in text.lower() for mark in ['e+', 'e-']):
                return format(Decimal(text), 'f').split('.')[0]
            if text.endswith('.0'):
                return text[:-2]
        except (InvalidOperation, ValueError):
            pass
        return text

    def parse_mixed_datetime_series(series):
        raw = series.astype(str).str.strip().str.replace(r'\s+', ' ', regex=True)
        numeric = pd.to_numeric(raw, errors='coerce')
        text_values = raw.mask(numeric.notna(), '')
        parsed = pd.to_datetime(text_values, errors='coerce', format='mixed')
        excel_mask = numeric.between(20000, 80000) & parsed.isna()
        if excel_mask.any():
            parsed.loc[excel_mask] = pd.to_datetime(numeric.loc[excel_mask], unit='D', origin='1899-12-30', errors='coerce')
        return parsed

    def robust_clean_time(df):
        if '时间' in df.columns:
            df['时间'] = df['时间'].astype(str).str.strip()
            df['时间'] = df['时间'].str.replace(r'\s+', ' ', regex=True)
            numeric_time = pd.to_numeric(df['时间'], errors='coerce')
            df['时间'] = df['时间'].where(numeric_time.notna(), df['时间'].str.split('.').str[0])
        return df

    def normalize_bill_type(value):
        text = str(value).strip().lower()
        if text in {'nan', 'none', '<na>', ''}:
            return '未知'
        if any(kw in text for kw in ['account_topup', 'topup', '充值', '加款', '入账']):
            return '充值'
        if any(kw in text for kw in ['refund from ad account', 'refund', '清零', '减款', '扣款', '退款']):
            return '清零'
        return '未知'

    def clean_amount_series(series):
        cleaned = (
            series.astype(str)
            .str.replace(',', '', regex=False)
            .str.extract(r'(-?\d+(?:\.\d+)?)', expand=False)
        )
        return pd.to_numeric(cleaned, errors='coerce').fillna(0)

    def normalize_match_text(value):
        return str(value).strip().lower().replace(' ', '').replace('\n', '').replace('\r', '')

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

    def empty_customer_frame():
        return pd.DataFrame(columns=['账号ID', '账号名称', '渠道', '客户'])

    # ========== 系统账单上传区 ==========
    section_title("系统账单", "支持多文件、多工作表 Excel。")
    hint_card("<b>系统账单会作为核对基准：</b>请上传原始 Excel，不需要手动拆分工作表。系统会自动过滤未完成或 pending 记录。")
    field_requirements(
        "系统账单",
        required=["账号ID", "账号名称", "金额", "类型/工作表名称"],
        optional=["交易号", "时间", "申请状态"],
        aliases=["广告账户", "账户ID", "申请ID", "transaction_id", "操作类型", "操作参数", "充值金额", "操作金额", "account_amount", "amount_paid", "更新时间", "提交时间", "申请时间", "交易时间"],
        note="只核对“充值/清零”两类操作；绑定、开户、Creation Fee 等其他类型会自动忽略，不纳入报告。",
    )
    system_files = st.file_uploader("上传系统账单（可多选，支持多工作表 Excel）", type=["xlsx", "xls"], accept_multiple_files=True)

    # ========== 日记账上传区 ==========
    section_title("人工日记账", "分别上传 Facebook 和 TikTok 日记账。")
    hint_card("<b>日记账用于和系统账逐条比较：</b>FB 通常按账号ID + 时间匹配；TT 优先按交易号匹配。")
    field_requirements(
        "人工日记账",
        required=["账号ID", "账号名称", "金额", "类型", "时间"],
        optional=["交易号", "客户", "申请状态"],
        aliases=["广告账户", "账户ID", "申请ID", "transaction_id", "操作类型", "操作参数", "充值金额", "操作金额", "申请时间", "交易时间", "更新时间"],
        note="类型请使用“充值/清零”，也可使用 account_topup / refund from ad account；清零金额会自动转为负数。",
    )
    col_j1, col_j2 = st.columns(2)
    with col_j1:
        fb_journal_files = st.file_uploader("🔵 上传 FB 日记账（可多选）", type=["xlsx", "xls"], accept_multiple_files=True)
    with col_j2:
        tt_journal_files = st.file_uploader("🟠 上传 TT 日记账（可多选）", type=["xlsx", "xls"], accept_multiple_files=True)

    section_title("筛选条件", "按平台、渠道、客户和日期缩小本次核对范围。")
    filter_col1, filter_col2 = st.columns([1, 2])
    with filter_col1:
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

    with filter_col2:
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

    filter_col3, filter_col4 = st.columns([2, 1])
    with filter_col3:
        selected_clients = st.multiselect(
            "🧑 选择客户（可多选，默认全部）",
            options=client_options,
            default=[]
        )
    with filter_col4:
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

    hint_card("<b>开始前检查：</b>请确认已上传 FB / TT 客户档案、系统账单，以及至少一个日记账文件；筛选条件不选时默认核对全部数据。")

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
                df['金额'] = clean_amount_series(df['金额'])

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

                if '类型' in df.columns:
                    df['类型'] = df['类型'].apply(normalize_bill_type)
                else:
                    sheet_low = sheet.lower()
                    if any(kw in sheet_low for kw in ['充值', 'topup']):
                        df['类型'] = '充值'
                    elif any(kw in sheet_low for kw in ['减款', '清零', 'refund']):
                        df['类型'] = '清零'
                    else:
                        df['类型'] = '未知'

                df = df[df['类型'].isin(['充值', '清零'])].copy()
                if df.empty:
                    continue

                if '金额' in df.columns:
                    df['金额'] = clean_amount_series(df['金额'])
                else:
                    df['金额'] = 0.0

            if '申请状态' in df.columns:
                valid_status = df['申请状态'].str.strip().str.lower().isin(['成功', '已完成', '已处理'])
                df = df[valid_status]

            if '金额' not in df.columns:
                df['金额'] = pd.Series(0.0, index=df.index)
            df['金额'] = clean_amount_series(df['金额'])

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

    def match_platform_and_channel_and_client(id_val, name_val, fb_dict, tt_dict, fb_name_dict, tt_name_dict):
        id_str = str(id_val).strip()
        name_str = str(name_val).strip()
        name_key = normalize_match_text(name_str)

        fb_info = fb_dict.get(id_str)
        tt_info = tt_dict.get(id_str)
        fb_name_info = fb_name_dict.get(name_key) if name_key else None
        tt_name_info = tt_name_dict.get(name_key) if name_key else None

        fb_match = fb_info is not None and normalize_match_text(fb_info.get('name', '')) == normalize_match_text(name_str)
        tt_match = tt_info is not None and normalize_match_text(tt_info.get('name', '')) == normalize_match_text(name_str)

        if fb_match and tt_match:
            return "FB", fb_info.get('channel', ''), fb_info.get('client', ''), fb_info.get('id', id_str), f"⚠️ 账号ID {id_str} 在FB和TT档案中都完全匹配，暂归为FB"
        elif fb_match:
            return "FB", fb_info.get('channel', ''), fb_info.get('client', ''), fb_info.get('id', id_str), ""
        elif tt_match:
            return "TT", tt_info.get('channel', ''), tt_info.get('client', ''), tt_info.get('id', id_str), ""
        elif fb_info is not None and tt_info is None:
            return "FB", fb_info.get('channel', ''), fb_info.get('client', ''), fb_info.get('id', id_str), f"⚠️ 账号ID {id_str} 已在FB档案中找到，但账号名称不完全一致，已按账号ID匹配"
        elif tt_info is not None and fb_info is None:
            return "TT", tt_info.get('channel', ''), tt_info.get('client', ''), tt_info.get('id', id_str), f"⚠️ 账号ID {id_str} 已在TT档案中找到，但账号名称不完全一致，已按账号ID匹配"
        elif fb_info is not None and tt_info is not None:
            return "FB", fb_info.get('channel', ''), fb_info.get('client', ''), fb_info.get('id', id_str), f"⚠️ 账号ID {id_str} 同时存在于FB和TT档案，账号名称不完全一致，暂按FB匹配"
        elif fb_name_info is not None and tt_name_info is None:
            return "FB", fb_name_info.get('channel', ''), fb_name_info.get('client', ''), fb_name_info.get('id', id_str), f"⚠️ 账号ID {id_str} 未精确匹配，已按账号名称匹配FB档案标准ID"
        elif tt_name_info is not None and fb_name_info is None:
            return "TT", tt_name_info.get('channel', ''), tt_name_info.get('client', ''), tt_name_info.get('id', id_str), f"⚠️ 账号ID {id_str} 未精确匹配，已按账号名称匹配TT档案标准ID"
        elif fb_name_info is not None and tt_name_info is not None:
            return "FB", fb_name_info.get('channel', ''), fb_name_info.get('client', ''), fb_name_info.get('id', id_str), f"⚠️ 账号名称同时存在于FB和TT档案，暂按FB匹配"
        else:
            return None, '', '', id_str, "账号ID和账号名称均未在客户档案中找到，请核实信息"

    # ========== 开始对账 ==========
    if st.button("✨ 开始自动对账", type="primary"):
        for key in ['mode1_report_data', 'mode1_report_name', 'mode1_success']:
            if key in st.session_state:
                del st.session_state[key]
        if not system_files:
            st.error("❌ 请上传系统账单！")
        elif platform_scope == "全部平台" and (fb_customers is None or tt_customers is None):
            st.error("❌ 当前选择“全部平台”，请同时上传 FB 和 TT 客户档案！")
        elif platform_scope == "仅 Facebook" and fb_customers is None:
            st.error("❌ 当前选择“仅 Facebook”，请先上传 FB 客户档案！")
        elif platform_scope == "仅 TikTok" and tt_customers is None:
            st.error("❌ 当前选择“仅 TikTok”，请先上传 TT 客户档案！")
        elif not fb_journal_files and not tt_journal_files:
            st.error("❌ 请至少上传一个日记账文件！")
        else:
            with st.spinner('🍬 JENNY正在核对，请稍候...'):
                if platform_scope == "仅 Facebook":
                    active_fb_customers = fb_customers if fb_customers is not None else empty_customer_frame()
                    active_tt_customers = empty_customer_frame()
                elif platform_scope == "仅 TikTok":
                    active_fb_customers = empty_customer_frame()
                    active_tt_customers = tt_customers if tt_customers is not None else empty_customer_frame()
                else:
                    active_fb_customers = fb_customers if fb_customers is not None else empty_customer_frame()
                    active_tt_customers = tt_customers if tt_customers is not None else empty_customer_frame()

                def find_duplicate_customer_assignments(*customer_frames):
                    records = {}
                    for platform_label, customer_df in customer_frames:
                        if customer_df is None or customer_df.empty:
                            continue
                        for _, row in customer_df.iterrows():
                            cid = normalize_id_text(row.get('账号ID', ''))
                            if not cid:
                                continue
                            cname = str(row.get('账号名称', '')).strip()
                            channel = str(row.get('渠道', '')).strip()
                            client = str(row.get('客户', '')).strip()
                            if not client:
                                continue
                            records.setdefault(cid, []).append({
                                '平台': platform_label,
                                '账号ID': cid,
                                '账号名称': cname,
                                '渠道': channel,
                                '客户': client,
                            })

                    duplicate_rows = []
                    for cid, rows in records.items():
                        clients = sorted({r['客户'] for r in rows if r['客户']})
                        if len(clients) <= 1:
                            continue
                        for r in rows:
                            duplicate_rows.append({
                                **r,
                                '重复客户': ' / '.join(clients),
                                '提示': '请核实，此账号客户分配重复'
                            })
                    return pd.DataFrame(duplicate_rows)

                duplicate_assignments = find_duplicate_customer_assignments(
                    ('FB', active_fb_customers),
                    ('TT', active_tt_customers)
                )
                duplicate_ids = set()
                duplicate_name_keys = set()
                if not duplicate_assignments.empty:
                    duplicate_ids = set(duplicate_assignments['账号ID'].astype(str).str.strip())
                    duplicate_name_keys = {
                        normalize_match_text(name)
                        for name in duplicate_assignments['账号名称'].astype(str)
                        if normalize_match_text(name)
                    }

                fb_dict = {}
                fb_name_dict = {}
                for _, row in active_fb_customers.iterrows():
                    cid = normalize_id_text(row['账号ID'])
                    cname = str(row['账号名称']).strip()
                    channel = str(row.get('渠道', '')).strip()
                    client = str(row.get('客户', '')).strip()
                    if cid:
                        name_key = normalize_match_text(cname)
                        if cid in duplicate_ids or name_key in duplicate_name_keys:
                            continue
                        new_info = {'id': cid, 'name': cname, 'channel': channel, 'client': client, 'plat': 'FB'}
                        if cid not in fb_dict:
                            fb_dict[cid] = new_info
                        if name_key and name_key not in fb_name_dict:
                            fb_name_dict[name_key] = new_info
                tt_dict = {}
                tt_name_dict = {}
                for _, row in active_tt_customers.iterrows():
                    cid = normalize_id_text(row['账号ID'])
                    cname = str(row['账号名称']).strip()
                    channel = str(row.get('渠道', '')).strip()
                    client = str(row.get('客户', '')).strip()
                    if cid:
                        name_key = normalize_match_text(cname)
                        if cid in duplicate_ids or name_key in duplicate_name_keys:
                            continue
                        new_info = {'id': cid, 'name': cname, 'channel': channel, 'client': client, 'plat': 'TT'}
                        if cid not in tt_dict:
                            tt_dict[cid] = new_info
                        if name_key and name_key not in tt_name_dict:
                            tt_name_dict[name_key] = new_info

                sys_df = load_system_bills(system_files)
                if sys_df.empty:
                    st.error("系统账单经处理后无有效数据")
                    st.stop()
                sys_df['来源平台'] = '系统账单'
                sys_df['_原始账号ID'] = sys_df.get('账号ID', '').astype(str)
                sys_df['_原始时间'] = sys_df.get('时间', '').astype(str)

                fb_jnl = load_journal(fb_journal_files, "FB日记账")
                tt_jnl = load_journal(tt_journal_files, "TT日记账")
                journal = pd.concat([fb_jnl, tt_jnl], ignore_index=True)
                if not journal.empty:
                    journal['_原始账号ID'] = journal.get('账号ID', '').astype(str)
                    journal['_原始时间'] = journal.get('时间', '').astype(str)

                duplicate_customer_issue = pd.DataFrame()
                if not duplicate_assignments.empty:
                    duplicate_clients_by_id = (
                        duplicate_assignments
                        .groupby('账号ID')['客户']
                        .apply(lambda s: ' / '.join(sorted(set(str(v).strip() for v in s if str(v).strip()))))
                        .to_dict()
                    )
                    report_duplicate_assignments = duplicate_assignments.copy()
                    if selected_clients:
                        selected_client_set = {str(c).strip() for c in selected_clients if str(c).strip()}

                        def duplicate_in_selected_clients(row):
                            own_client = str(row.get('客户', '')).strip()
                            all_clients = {
                                c.strip()
                                for c in str(row.get('重复客户', '')).split('/')
                                if c.strip()
                            }
                            return own_client in selected_client_set or bool(all_clients & selected_client_set)

                        report_duplicate_assignments = duplicate_assignments[
                            duplicate_assignments.apply(duplicate_in_selected_clients, axis=1)
                        ].copy()

                    report_duplicate_ids = set(report_duplicate_assignments['账号ID'].astype(str).str.strip())
                    report_duplicate_name_keys = {
                        normalize_match_text(name)
                        for name in report_duplicate_assignments['账号名称'].astype(str)
                        if normalize_match_text(name)
                    }
                    duplicate_records = []

                    def is_duplicate_customer_row(row, ids=None, name_keys=None):
                        ids = duplicate_ids if ids is None else ids
                        name_keys = duplicate_name_keys if name_keys is None else name_keys
                        raw_id = normalize_id_text(row.get('账号ID', ''))
                        raw_original_id = normalize_id_text(row.get('_原始账号ID', ''))
                        name_key = normalize_match_text(row.get('账号名称', ''))
                        return raw_id in ids or raw_original_id in ids or name_key in name_keys

                    def collect_duplicate_customer_rows(df, source_name):
                        if df.empty:
                            return
                        if not report_duplicate_ids and not report_duplicate_name_keys:
                            return
                        mask = df.apply(
                            lambda row: is_duplicate_customer_row(row, report_duplicate_ids, report_duplicate_name_keys),
                            axis=1
                        )
                        for _, row in df[mask].iterrows():
                            rid = normalize_id_text(row.get('账号ID', '')) or normalize_id_text(row.get('_原始账号ID', ''))
                            duplicate_records.append({
                                '来源': source_name,
                                '异常类型': '客户分配重复',
                                '账号ID': rid,
                                '账号名称': row.get('账号名称', ''),
                                '类型': row.get('类型', ''),
                                '金额': row.get('金额', ''),
                                '时间': row.get('时间', ''),
                                '原始时间': row.get('_原始时间', ''),
                                '重复客户': duplicate_clients_by_id.get(rid, ''),
                                '提示': '请核实，此账号客户分配重复',
                            })

                    collect_duplicate_customer_rows(sys_df, '系统账')
                    collect_duplicate_customer_rows(journal, '日记账')

                    duplicate_assignment_rows = report_duplicate_assignments.assign(
                        来源='客户档案',
                        异常类型='客户分配重复',
                        类型='',
                        金额='',
                        时间='',
                        原始时间='',
                    )
                    duplicate_customer_issue = pd.concat(
                        [duplicate_assignment_rows, pd.DataFrame(duplicate_records)],
                        ignore_index=True,
                        sort=False
                    )
                    duplicate_cols = ['来源', '异常类型', '账号ID', '账号名称', '类型', '金额', '时间', '原始时间', '渠道', '客户', '重复客户', '提示', '平台']
                    for col in duplicate_cols:
                        if col not in duplicate_customer_issue.columns:
                            duplicate_customer_issue[col] = ''
                    duplicate_customer_issue = duplicate_customer_issue[duplicate_cols]

                    sys_df = sys_df[~sys_df.apply(is_duplicate_customer_row, axis=1)].copy()
                    if not journal.empty:
                        journal = journal[~journal.apply(is_duplicate_customer_row, axis=1)].copy()

                def canonical_journal_id(row):
                    raw_id = normalize_id_text(row.get('账号ID', ''))
                    name_key = normalize_match_text(row.get('账号名称', ''))
                    if raw_id in fb_dict:
                        return fb_dict[raw_id].get('id', raw_id)
                    if raw_id in tt_dict:
                        return tt_dict[raw_id].get('id', raw_id)
                    if name_key in fb_name_dict:
                        return fb_name_dict[name_key].get('id', raw_id)
                    if name_key in tt_name_dict:
                        return tt_name_dict[name_key].get('id', raw_id)
                    return raw_id

                if not journal.empty:
                    journal['账号ID'] = journal.apply(canonical_journal_id, axis=1)

                matched_platforms = []
                match_channels = []
                match_clients = []
                match_ids = []
                errors = []
                for idx, row in sys_df.iterrows():
                    plat, ch, cl, canonical_id, err = match_platform_and_channel_and_client(
                        row.get('账号ID', ''), row.get('账号名称', ''), fb_dict, tt_dict, fb_name_dict, tt_name_dict
                    )
                    matched_platforms.append(plat)
                    match_channels.append(ch)
                    match_clients.append(cl)
                    match_ids.append(canonical_id)
                    if plat is None:
                        errors.append((row.get('账号ID', ''), row.get('账号名称', ''), err))

                sys_df['所属平台'] = matched_platforms
                sys_df['渠道'] = match_channels
                sys_df['客户'] = match_clients
                sys_df['账号ID'] = match_ids

                if errors:
                    st.error(f"🚨 系统账单中发现 {len(errors)} 条记录与客户档案不匹配，已剔除：")
                    for e in errors[:20]:
                        st.write(f"· 账号ID: {e[0]}, 账号名称: {e[1]} → {e[2]}")
                    sys_df = sys_df[sys_df['所属平台'].notna()]

                if sys_df.empty:
                    if duplicate_customer_issue.empty:
                        st.error("匹配后无有效系统记录，对账中止")
                        st.stop()
                    st.warning("匹配后无有效系统记录，但已发现客户分配重复异常，将继续导出异常报告。")

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
                            ser = parse_mixed_datetime_series(df['时间']).dropna()
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
                        df['时间_dt'] = parse_mixed_datetime_series(df['时间'])
                        mask = (df['时间_dt'].notna()) & (df['时间_dt'].dt.date >= start_date) & (df['时间_dt'].dt.date <= end_date)
                        df = df[mask].copy()
                        df.drop(columns=['时间_dt'], inplace=True)
                        if idx == 0:
                            sys_df = df
                        else:
                            journal = df

                if sys_df.empty:
                    if duplicate_customer_issue.empty:
                        st.warning("筛选时间范围后，系统账单无数据，无法对账")
                        st.stop()
                    st.warning("筛选时间范围后系统账单无数据，但已发现客户分配重复异常，将继续导出异常报告。")

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
                    if duplicate_customer_issue.empty:
                        st.warning("筛选渠道后，系统账单无数据，无法对账")
                        st.stop()
                    st.warning("筛选渠道后系统账单无数据，但已发现客户分配重复异常，将继续导出异常报告。")

                if selected_clients:
                    if '客户' in sys_df.columns:
                        sys_df = sys_df[sys_df['客户'].isin(selected_clients)]
                    if not journal.empty and '客户' in journal.columns:
                        journal = journal[journal['客户'].isin(selected_clients)]

                if sys_df.empty:
                    if duplicate_customer_issue.empty:
                        st.warning("筛选客户后，系统账单无数据，无法对账")
                        st.stop()
                    st.warning("筛选客户后系统账单无数据，但已发现客户分配重复异常，将继续导出异常报告。")

                if platform_scope == "仅 Facebook":
                    sys_df = sys_df[sys_df['所属平台'] == 'FB']
                    journal = journal[journal['来源平台'] == 'FB日记账'] if not journal.empty else journal
                elif platform_scope == "仅 TikTok":
                    sys_df = sys_df[sys_df['所属平台'] == 'TT']
                    journal = journal[journal['来源平台'] == 'TT日记账'] if not journal.empty else journal

                if sys_df.empty:
                    if duplicate_customer_issue.empty:
                        st.warning("在当前平台范围内，系统账单无数据，无法对账")
                        st.stop()
                    st.warning("当前平台范围内系统账单无数据，但已发现客户分配重复异常，将继续导出异常报告。")

            for df in [sys_df, journal]:
                if not df.empty:
                    if '时间' in df.columns:
                        parsed_time = parse_mixed_datetime_series(df['时间'])
                        df['_匹配时间'] = parsed_time.dt.floor('min').dt.strftime("%Y-%m-%d %H:%M").fillna("")
                        df['时间'] = df['_匹配时间']
                        if '金额' in df.columns:
                            df['金额'] = pd.to_numeric(df['金额'], errors='coerce').fillna(0).round(2)
                        else:
                            df['金额'] = 0.0

            def gen_key_sys(row):
                plat = row['所属平台']
                acc_id = normalize_id_text(row['账号ID'])
                time_val = str(row.get('_匹配时间', row.get('时间', ''))).strip()
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
                acc_id = normalize_id_text(row['账号ID'])
                time_val = str(row.get('_匹配时间', row.get('时间', ''))).strip()
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

            debug_frames = []
            sys_debug_cols = [c for c in ['_原始账号ID', '账号ID', '账号名称', '_原始时间', '时间', '_匹配时间', '类型', '金额', '所属平台', '渠道', '客户', '主键'] if c in sys_df.columns]
            if sys_debug_cols:
                sys_debug = sys_df[sys_debug_cols].copy()
                sys_debug.insert(0, '来源', '系统账')
                debug_frames.append(sys_debug)
            if not journal.empty:
                jnl_debug_cols = [c for c in ['_原始账号ID', '账号ID', '账号名称', '_原始时间', '时间', '_匹配时间', '类型', '金额', '来源平台', '渠道', '客户', '主键'] if c in journal.columns]
                if jnl_debug_cols:
                    jnl_debug = journal[jnl_debug_cols].copy()
                    jnl_debug.insert(0, '来源', '日记账')
                    debug_frames.append(jnl_debug)
            debug_detail = pd.concat(debug_frames, ignore_index=True) if debug_frames else pd.DataFrame()

            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                summary = pd.DataFrame({
                    "核查项目": ["1.漏记(系统有日记无)", "2.多记(日记有系统无)", "3.金额不符", "4.类型不符", "5.系统重复", "6.日记账重复", "7.客户分配重复"],
                    "异常条数": [len(missing_in_j), len(missing_in_s), len(amt_diff), len(typ_diff), len(sys_dup), len(jnl_dup), len(duplicate_customer_issue)]
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
                duplicate_customer_issue.to_excel(writer, sheet_name="7.客户分配重复", index=False)
                debug_detail.to_excel(writer, sheet_name="调试明细", index=False)

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

            # 持久化存储
            st.session_state['mode1_report_data'] = output.getvalue()
            st.session_state['mode1_report_name'] = report_name
            st.session_state['mode1_success'] = "🎉 对账完成！请下载报告～"

    # ========== 显示持久化的下载按钮 ==========
    if 'mode1_report_data' in st.session_state:
        st.success(st.session_state['mode1_success'])
        st.download_button(
            label="📥 下载对账报告",
            data=st.session_state['mode1_report_data'],
            file_name=st.session_state['mode1_report_name'],
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="mode1_download"
        )

# =================================================================
# 模式二：消耗账单对账（持久化下载按钮）
# =================================================================
else:
    guide_card(
        "消耗账单清洗 / 对账流程",
        [
            ("客户档案", "可选上传 FB / TT 档案，用于标注平台和客户。"),
            ("第一份账单", "上传需要清洗或作为基准的消耗账单。"),
            ("第二份账单", "可选上传，用于核对账号维度的消耗差异。"),
            ("生成结果", "按客户筛选后导出清洗明细或差异报告。"),
        ],
    )

    # ----- 客户档案上传（消耗对账专用） -----
    section_title("客户档案", "可选上传，用于自动标注平台、渠道和客户。")
    hint_card("<b>可选上传：</b>如果不上传客户档案，消耗账单仍可清洗；只是不会自动标注平台和客户。")
    field_requirements(
        "客户档案",
        required=["账号ID", "账号名称"],
        optional=["渠道", "客户"],
        aliases=["广告账户", "账户ID", "meta_id", "account_id", "账户名称", "account_name", "归属广告主", "广告主"],
        note="上传后可以按客户筛选消耗账单，导出的结果也会带上平台和客户信息。",
    )
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
            df.columns = [str(c) for c in df.columns]
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

    def normalize_cons_text(value):
        text = str(value).strip()
        if text.lower() in {'', 'nan', 'none', '<na>', 'nat'}:
            return ''
        return text.lower().replace(' ', '').replace('\n', '').replace('\r', '')

    def normalize_cons_account_id(value):
        text = str(value).strip()
        if text.lower() in {'', 'nan', 'none', '<na>'}:
            return ''
        text = text.replace(',', '').replace(' ', '')
        try:
            if any(mark in text.lower() for mark in ['e+', 'e-']):
                return format(Decimal(text), 'f').split('.')[0]
            if text.endswith('.0'):
                return text[:-2]
        except (InvalidOperation, ValueError):
            pass
        return text

    def looks_like_account_id(value):
        normalized = normalize_cons_account_id(value)
        return normalized.isdigit() and len(normalized) >= 8

    def clean_cons_amount(value):
        text = str(value).replace(',', '').strip()
        match = pd.Series([text]).str.extract(r'(-?\d+(?:\.\d+)?)', expand=False).iloc[0]
        return pd.to_numeric(match, errors='coerce') if pd.notna(match) else 0

    def is_summary_or_empty_consumption_row(row):
        joined = " ".join(str(v) for v in row.values if str(v).strip().lower() not in {'', 'nan', 'none', '<na>'})
        has_summary_word = any(word in joined for word in ['总消耗', '合计', '总计', 'subtotal', 'total'])
        has_account = looks_like_account_id(row.get('账号ID', '')) or normalize_cons_text(row.get('账号名称', '')) != ''
        return has_summary_word or not has_account

    def safe_file_part(value):
        text = str(value).strip()
        for ch in ['\\', '/', ':', '*', '?', '"', '<', '>', '|']:
            text = text.replace(ch, '_')
        return text or '客户'

    def build_consumption_extract_filename(df):
        clients = [
            str(v).strip()
            for v in df['客户'].dropna().unique()
            if str(v).strip() and str(v).strip().lower() not in {'nan', 'none', '<na>'}
        ]
        if len(clients) == 1:
            prefix = safe_file_part(clients[0])
        elif len(clients) > 1:
            prefix = safe_file_part("_".join(clients[:3]))
            if len(clients) > 3:
                prefix = f"{prefix}_等{len(clients)}个客户"
        else:
            prefix = "未匹配客户"
        return f"{prefix}消耗.xlsx"

    def clean_cons_date_series(series):
        raw = series.astype(str).str.strip()
        numeric = pd.to_numeric(raw, errors='coerce')
        parsed = pd.to_datetime(raw, errors='coerce', format='mixed')
        excel_mask = numeric.between(20000, 80000) & parsed.isna()
        if excel_mask.any():
            parsed.loc[excel_mask] = pd.to_datetime(numeric.loc[excel_mask], unit='D', origin='1899-12-30', errors='coerce')
        return parsed.dt.strftime("%Y-%m-%d")

    def normalize_cons_columns(df):
        rename_map = {
            '账号名称': ['广告账户名称', '账户名称', '账号名称', 'account_name', 'ad account name'],
            '账号ID': ['账户ID', '广告账户ID', '广告账户', '账号ID', 'account_id', 'ad account id'],
            '消耗': ['消耗金额', '消耗', '花费(美元)', '花费', 'spend', 'amount_spent', 'cost'],
            '日期': ['消耗时间', '日期', '日期开始', '开始日期', '时间', 'date', 'day', 'created_at']
        }
        def norm_col(value):
            return str(value).strip().lower().replace(' ', '').replace('\n', '').replace('\r', '')
        lower_cols = {norm_col(c): c for c in df.columns}
        final_rename = {}
        for std, candidates in rename_map.items():
            for cand in candidates:
                key = norm_col(cand)
                if key in lower_cols:
                    final_rename[lower_cols[key]] = std
                    break
        return df.rename(columns=final_rename)

    # 合并客户档案字典，并收集所有客户名称
    customer_dict = {}
    customer_name_dict = {}
    all_client_options = set()
    if not fb_cus.empty:
        for _, row in fb_cus.iterrows():
            cid = normalize_cons_account_id(row['账号ID'])
            cname = str(row.get('账号名称', '')).strip()
            if cid:
                client_str = str(row.get('客户', '')).strip()
                customer_dict[cid] = {
                    '平台': 'FB',
                    '账号名称': cname,
                    '客户': client_str,
                    '渠道': str(row.get('渠道', '')).strip()
                }
                cname_key = normalize_cons_text(cname)
                if cname_key:
                    customer_name_dict[cname_key] = customer_dict[cid]
                if client_str:
                    all_client_options.add(client_str)
    if not tt_cus.empty:
        for _, row in tt_cus.iterrows():
            cid = normalize_cons_account_id(row['账号ID'])
            cname = str(row.get('账号名称', '')).strip()
            if cid:
                client_str = str(row.get('客户', '')).strip()
                customer_dict[cid] = {
                    '平台': 'TT',
                    '账号名称': cname,
                    '客户': client_str,
                    '渠道': str(row.get('渠道', '')).strip()
                }
                cname_key = normalize_cons_text(cname)
                if cname_key:
                    customer_name_dict[cname_key] = customer_dict[cid]
                if client_str:
                    all_client_options.add(client_str)

    total_customers = len(customer_dict)
    if total_customers > 0:
        st.success(f"🌸 已加载客户档案，共 {total_customers} 个账号ID")
    else:
        st.info("未上传客户档案，将不标注平台和客户")

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

    # 清洗提取客户数据
    section_title("清洗提取客户数据", "上传系统消耗账，按客户档案逐行识别客户并导出清洗明细。")
    hint_card("<b>处理规则：</b>不汇总账号花费，不做两份账单核对；只保留源数据粒度，并补充平台、渠道、客户信息。")
    field_requirements(
        "系统消耗账",
        required=["账号ID/广告账户ID", "账号名称/广告账户名称", "消耗/花费", "日期/时间"],
        optional=["客户", "渠道", "平台"],
        aliases=["账户ID", "广告账户ID", "广告账户", "账户名称", "广告账户名称", "消耗金额", "花费(美元)", "花费", "日期开始", "消耗时间", "spend", "date", "day"],
        note="如果账号ID变成科学计数法、带 .0，或账号ID和名称列放反，系统会自动清洗并尝试纠正。",
    )
    extract_files = st.file_uploader(
        "📤 上传系统消耗账（可多选，用于清洗提取客户数据）",
        type=["xlsx", "xls"],
        accept_multiple_files=True,
        key="extract_customer_consumption",
    )

    def clean_extract_customer_consumption(files):
        if not files:
            return pd.DataFrame()
        frames = []
        for f in files:
            df = pd.read_excel(f, dtype=str)
            if df.empty:
                continue
            df.columns = [str(c) for c in df.columns]
            df = normalize_cons_columns(df)

            for col in ['账号ID', '账号名称', '消耗', '日期']:
                if col not in df.columns:
                    df[col] = ''

            df = df[~df.apply(is_summary_or_empty_consumption_row, axis=1)].copy()
            if df.empty:
                continue

            df['账号ID'] = df['账号ID'].apply(normalize_cons_account_id)
            df['账号名称'] = df['账号名称'].astype(str).str.strip().replace({'nan': '', 'None': '', '<NA>': ''})

            def fix_id_name(row):
                acc_id = row['账号ID']
                acc_name = str(row['账号名称']).strip()
                if not looks_like_account_id(acc_id) and looks_like_account_id(acc_name):
                    row['账号ID'] = normalize_cons_account_id(acc_name)
                    row['账号名称'] = str(acc_id).strip()
                return row

            df = df.apply(fix_id_name, axis=1)
            df['账号ID'] = df['账号ID'].apply(normalize_cons_account_id)
            df['账号名称'] = df['账号名称'].astype(str).str.strip().replace({'nan': '', 'None': '', '<NA>': ''})
            df['消耗'] = df['消耗'].apply(clean_cons_amount).fillna(0)
            df['日期'] = clean_cons_date_series(df['日期'])

            def match_customer(row):
                acc_id = normalize_cons_account_id(row['账号ID'])
                acc_name = normalize_cons_text(row['账号名称'])
                info = customer_dict.get(acc_id)
                match_type = '账号ID'
                if info is None and acc_name:
                    info = customer_name_dict.get(acc_name)
                    match_type = '账号名称'
                if info is None:
                    return pd.Series({
                        '平台': '未匹配',
                        '渠道': '',
                        '客户': '',
                        '匹配方式': '未匹配'
                    })
                return pd.Series({
                    '平台': info.get('平台', ''),
                    '渠道': info.get('渠道', ''),
                    '客户': info.get('客户', ''),
                    '匹配方式': match_type
                })

            matched = df.apply(match_customer, axis=1)
            df = pd.concat([df, matched], axis=1)
            df = df[(df['账号ID'].apply(looks_like_account_id)) | (df['账号名称'].apply(normalize_cons_text) != '')]
            df['来源文件'] = getattr(f, 'name', '')
            frames.append(df[['日期', '账号ID', '账号名称', '消耗', '平台', '渠道', '客户', '匹配方式', '来源文件']])

        if not frames:
            return pd.DataFrame(columns=['日期', '账号ID', '账号名称', '消耗', '平台', '渠道', '客户', '匹配方式', '来源文件'])
        return pd.concat(frames, ignore_index=True)

    if st.button("✨ 清洗提取客户数据", type="primary"):
        if not extract_files:
            st.error("请先上传系统消耗账。")
        else:
            with st.spinner("JENNY 正在清洗并识别客户，请稍候..."):
                extracted_df = clean_extract_customer_consumption(extract_files)
                if extracted_df.empty:
                    st.error("清洗后无有效数据，请检查账单字段。")
                else:
                    if selected_clients_cons:
                        extracted_df = extracted_df[extracted_df['客户'].isin(selected_clients_cons)]
                        if extracted_df.empty:
                            st.warning("筛选客户后无数据，请重新选择客户或检查客户档案。")
                            st.stop()

                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        extracted_df.to_excel(writer, sheet_name="客户数据清洗明细", index=False)

                    matched_count = int((extracted_df['匹配方式'] != '未匹配').sum())
                    for key in ['mode2_report_data', 'mode2_report_name', 'mode2_detail_data', 'mode2_detail_name', 'mode2_success', 'mode2_show_dataframe']:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.session_state['extract_customer_data'] = output.getvalue()
                    st.session_state['extract_customer_name'] = build_consumption_extract_filename(extracted_df)
                    st.session_state['extract_customer_success'] = f"✅ 清洗完成，共 {len(extracted_df)} 条；已匹配客户 {matched_count} 条"
                    st.session_state['extract_customer_preview'] = extracted_df

    if 'extract_customer_data' in st.session_state:
        st.success(st.session_state['extract_customer_success'])
        st.dataframe(st.session_state['extract_customer_preview'])
        st.download_button(
            label="📥 下载清洗提取客户数据",
            data=st.session_state['extract_customer_data'],
            file_name=st.session_state['extract_customer_name'],
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="extract_customer_download"
        )

    # 消耗账单上传区
    section_title("消耗账单", "上传一份账单会生成清洗明细；上传两份账单会额外生成差异报告。")
    hint_card("<b>处理规则：</b>上传一份账单时输出清洗明细；上传两份账单时会按账号ID汇总消耗并比较差异。")
    field_requirements(
        "消耗账单",
        required=["账号ID", "账号名称", "消耗", "日期"],
        optional=["平台", "客户"],
        aliases=["账户ID", "广告账户ID", "广告账户名称", "账户名称", "消耗金额", "花费(美元)", "花费", "消耗时间", "开始日期"],
        note="如果账号ID和账号名称列放反，系统会尝试自动调换；但建议仍按字段要求整理 Excel，结果会更稳定。",
    )
    col_a, col_b = st.columns(2)
    with col_a:
        consumption_files1 = st.file_uploader("📤 消耗账单 ①（可多选）", type=["xlsx", "xls"], accept_multiple_files=True, key="cons1")
    with col_b:
        consumption_files2 = st.file_uploader("📤 消耗账单 ②（可选，用于比对）", type=["xlsx", "xls"], accept_multiple_files=True, key="cons2")

    hint_card("<b>开始前检查：</b>至少上传消耗账单 ①；如果上传消耗账单 ②，系统会生成两份账单的差异报告。")

    def clean_consumption_bill(files):
        """清洗消耗账单，返回DataFrame包含：账号ID、账号名称、消耗、日期、平台、客户"""
        if not files:
            return pd.DataFrame()
        df_list = []
        for f in files:
            df = pd.read_excel(f, dtype=str)
            if df.empty:
                continue
            df.columns = [str(c) for c in df.columns]
            df = normalize_cons_columns(df)

            for col in ['账号名称', '账号ID', '消耗', '日期']:
                if col not in df.columns:
                    df[col] = np.nan

            df = df[~df.apply(is_summary_or_empty_consumption_row, axis=1)].copy()
            if df.empty:
                continue

            df['账号ID'] = df['账号ID'].apply(normalize_cons_account_id)
            df['账号名称'] = df['账号名称'].astype(str).str.strip()
            df['消耗'] = df['消耗'].apply(clean_cons_amount).fillna(0)
            df['日期'] = clean_cons_date_series(df['日期'])

            def swap_if_needed(row):
                acc_id = row['账号ID']
                acc_name = row['账号名称']
                if not looks_like_account_id(acc_id) and looks_like_account_id(acc_name):
                    temp = row['账号名称']
                    row['账号名称'] = str(acc_id).strip()
                    row['账号ID'] = normalize_cons_account_id(temp)
                return row

            df = df.apply(swap_if_needed, axis=1)
            df['账号ID'] = df['账号ID'].apply(normalize_cons_account_id)
            df['账号名称'] = df['账号名称'].astype(str).str.strip()

            df['平台'] = df['账号ID'].map(lambda x: customer_dict.get(x, {}).get('平台', '未知') if customer_dict else '未上传档案')
            df['客户'] = df['账号ID'].map(lambda x: customer_dict.get(x, {}).get('客户', '') if customer_dict else '')
            df = df[(df['账号ID'].apply(looks_like_account_id)) | (df['账号名称'].apply(normalize_cons_text) != '')]
            df = df[['账号ID', '账号名称', '消耗', '日期', '平台', '客户']]
            df_list.append(df)

        if not df_list:
            return pd.DataFrame(columns=['账号ID', '账号名称', '消耗', '日期', '平台', '客户'])
        return pd.concat(df_list, ignore_index=True)

    if st.button("✨ 开始处理消耗账单", type="primary"):
        if not consumption_files1:
            st.error("请至少上传第一份消耗账单！")
        else:
            with st.spinner('🍬 JENNY 正在处理消耗账单，请稍候...'):
                for key in ['extract_customer_data', 'extract_customer_name', 'extract_customer_success', 'extract_customer_preview']:
                    if key in st.session_state:
                        del st.session_state[key]
                df1 = clean_consumption_bill(consumption_files1)
                if df1.empty:
                    st.error("清洗后无有效数据，请检查账单格式。")
                else:
                    if selected_clients_cons:
                        df1 = df1[df1['客户'].isin(selected_clients_cons)]
                        if df1.empty:
                            st.warning("筛选客户后，第一份账单无数据，请重新选择客户或检查账单。")
                            st.stop()

                    # 只有一份账单时，保存清洗结果
                    if not consumption_files2:
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='openpyxl') as writer:
                            df1.to_excel(writer, sheet_name="清洗结果", index=False)
                        st.session_state['mode2_detail_data'] = output.getvalue()
                        st.session_state['mode2_detail_name'] = f"消耗账单清洗_{datetime.today().strftime('%Y%m%d')}.xlsx"
                        st.session_state['mode2_success'] = f"✅ 清洗完成，共 {len(df1)} 条有效记录"
                        st.session_state['mode2_show_dataframe'] = df1
                        # 清除可能有冲突的报告数据
                        if 'mode2_report_data' in st.session_state:
                            del st.session_state['mode2_report_data']
                        if 'mode2_report_name' in st.session_state:
                            del st.session_state['mode2_report_name']
                    else:
                        df2 = clean_consumption_bill(consumption_files2)
                        if df2.empty:
                            st.error("第二份账单清洗后无有效数据。")
                        else:
                            if selected_clients_cons:
                                df2 = df2[df2['客户'].isin(selected_clients_cons)]
                                if df2.empty:
                                    st.warning("筛选客户后，第二份账单无数据，无法比对。")
                                    st.stop()

                            # 汇总
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

                            # 对账报告
                            output_report = io.BytesIO()
                            with pd.ExcelWriter(output_report, engine='openpyxl') as writer:
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

                            # 清洗明细（两个账单）
                            output_detail = io.BytesIO()
                            with pd.ExcelWriter(output_detail, engine='openpyxl') as writer:
                                df1.to_excel(writer, sheet_name="账单①清洗明细", index=False)
                                df2.to_excel(writer, sheet_name="账单②清洗明细", index=False)

                            # 持久化存储
                            st.session_state['mode2_report_data'] = output_report.getvalue()
                            st.session_state['mode2_report_name'] = f"消耗对账_{datetime.today().strftime('%Y%m%d')}.xlsx"
                            st.session_state['mode2_detail_data'] = output_detail.getvalue()
                            st.session_state['mode2_detail_name'] = f"消耗账单清洗明细_{datetime.today().strftime('%Y%m%d')}.xlsx"
                            st.session_state['mode2_success'] = f"🎉 对账完成：漏记 {len(missing_in_2)}，多记 {len(extra_in_2)}，消耗差异 {len(diff)}"
                            st.session_state['mode2_show_dataframe'] = None  # 不显示明细表，直接下载
                            # 清除可能冲突的单份清洗标记
                            if 'mode2_only_detail' in st.session_state:
                                del st.session_state['mode2_only_detail']

    # ========== 显示持久化的下载按钮 ==========
    if 'mode2_report_data' in st.session_state:
        # 有两份账单，显示对账报告和明细下载
        st.success(st.session_state['mode2_success'])
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                label="📥 下载对账报告",
                data=st.session_state['mode2_report_data'],
                file_name=st.session_state['mode2_report_name'],
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="mode2_report_dl"
            )
        with col_dl2:
            st.download_button(
                label="📥 下载清洗明细",
                data=st.session_state['mode2_detail_data'],
                file_name=st.session_state['mode2_detail_name'],
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="mode2_detail_dl"
            )
    elif 'mode2_detail_data' in st.session_state:
        # 只有一份账单，显示清洗结果和下载
        st.success(st.session_state['mode2_success'])
        if 'mode2_show_dataframe' in st.session_state and st.session_state['mode2_show_dataframe'] is not None:
            st.dataframe(st.session_state['mode2_show_dataframe'])
        st.download_button(
            label="📥 下载清洗明细",
            data=st.session_state['mode2_detail_data'],
            file_name=st.session_state['mode2_detail_name'],
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="mode2_single_dl"
        )

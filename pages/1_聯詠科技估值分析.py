#!/usr/bin/env python3
"""聯詠科技 (3034.TW) 估值分析儀表板 — TradingView 整合版"""

from __future__ import annotations

import io
import json
import sqlite3
import tempfile
from pathlib import Path
from datetime import datetime

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ── Page config ──────────────────────────────────────────────────
st.set_page_config(
    page_title="聯詠科技 3034 估值分析",
    page_icon="📊",
    layout="wide",
)

# ── Constants ────────────────────────────────────────────────────
CURRENT_PRICE = 453
SYMBOL = "TWSE:3034"
REPORT_DATE = "2026-05-07"

SCENARIOS = {
    "bear":  {"label": "保守",   "eps": 28.1,  "color": "#94a3b8"},
    "base":  {"label": "基準",   "eps": 32.5,  "color": "#2563A8"},
    "bull":  {"label": "樂觀",   "eps": 37.8,  "color": "#1A7A5E"},
    "aitam": {"label": "ai-tam", "eps": 33.9,  "color": "#D4770A"},
}
PE_MULTIPLES = [16, 18, 20, 22, 25]

EPS_HISTORY = [
    {"year": "2020", "eps": 19.00, "type": "actual"},
    {"year": "2021", "eps": 63.00, "type": "actual"},
    {"year": "2022", "eps": 46.00, "type": "actual"},
    {"year": "2023", "eps": 38.00, "type": "actual"},
    {"year": "2024", "eps": 32.94, "type": "actual"},
    {"year": "2025", "eps": 26.87, "type": "actual"},
]
EPS_FORECASTS = {
    "2026E(保守)":  28.1,
    "2026E(基準)":  32.5,
    "2026E(樂觀)":  37.8,
    "2026E(ai-tam)": 33.9,
}

ASP_DATA = [
    {"period": "2025全年",  "asp": 124, "soc_rev": 372, "soc_pct": 37},
    {"period": "2026 Q1",   "asp": 136, "soc_rev": 410, "soc_pct": 44},
    {"period": "2026 H1E",  "asp": 140, "soc_rev": 462, "soc_pct": 50},
    {"period": "2026 H2E",  "asp": 145, "soc_rev": 510, "soc_pct": 54},
    {"period": "2027E",     "asp": 155, "soc_rev": 558, "soc_pct": 56},
]

MONTHLY_REV = [
    {"month": "Jan", "rev2026": 76.17,  "rev2025": 84.81, "yoy": -10},
    {"month": "Feb", "rev2026": 70.59,  "rev2025": 92.67, "yoy": -24},
    {"month": "Mar", "rev2026": 84.69,  "rev2025": 93.72, "yoy": -10},
    {"month": "Apr", "rev2026": 92.25,  "rev2025": 91.20, "yoy":   1},
    {"month": "May", "rev2026": None,   "rev2025": 86.07, "yoy": None},
    {"month": "Jun", "rev2026": None,   "rev2025": 84.25, "yoy": None},
    {"month": "Jul", "rev2026": None,   "rev2025": 81.20, "yoy": None},
    {"month": "Aug", "rev2026": None,   "rev2025": 81.75, "yoy": None},
    {"month": "Sep", "rev2026": None,   "rev2025": 82.78, "yoy": None},
    {"month": "Oct", "rev2026": None,   "rev2025": 78.79, "yoy": None},
    {"month": "Nov", "rev2026": None,   "rev2025": 76.19, "yoy": None},
    {"month": "Dec", "rev2026": None,   "rev2025": 73.20, "yoy": None},
]

INCOME_STMT = [
    {"item": "營收 (億元)",       "2025": "1,007", "保守": "1,055", "基準": "1,100", "樂觀": "1,150"},
    {"item": "毛利率",            "2025": "37.7%", "保守": "40%",   "基準": "41%",   "樂觀": "42%"},
    {"item": "費用率",            "2025": "21.7%", "保守": "22%",   "基準": "21.5%", "樂觀": "21%"},
    {"item": "營益率",            "2025": "16.0%", "保守": "18%",   "基準": "19.5%", "樂觀": "21%"},
    {"item": "稅後淨利 (億元)",   "2025": "163",   "保守": "144",   "基準": "198",   "樂觀": "218"},
    {"item": "EPS (元)",          "2025": "26.87", "保守": "28.1",  "基準": "32.5",  "樂觀": "37.8"},
    {"item": "vs 2025",           "2025": "—",     "保守": "+4.6%", "基準": "+21%",  "樂觀": "+40.7%"},
]

STOCK_ANALYSIS = {
    "fundamental": [
        {"metric": "P/E (TTM)",       "value": "16.8x",   "vs_sector": "折價 12%",  "signal": "偏低"},
        {"metric": "P/E (2026E基準)", "value": "13.9x",   "vs_sector": "折價 27%",  "signal": "低估"},
        {"metric": "P/B",             "value": "3.2x",    "vs_sector": "合理",       "signal": "中性"},
        {"metric": "EV/EBITDA",       "value": "9.8x",    "vs_sector": "折價 18%",  "signal": "偏低"},
        {"metric": "股息殖利率",      "value": "4.2%",    "vs_sector": "高於均值",   "signal": "正面"},
        {"metric": "ROE",             "value": "19.3%",   "vs_sector": "高於均值",   "signal": "正面"},
        {"metric": "ROA",             "value": "14.7%",   "vs_sector": "高於均值",   "signal": "正面"},
        {"metric": "流動比率",        "value": "3.8x",    "vs_sector": "健全",       "signal": "正面"},
        {"metric": "負債比率",        "value": "24%",     "vs_sector": "低",         "signal": "正面"},
        {"metric": "淨現金 (億元)",   "value": "+287",    "vs_sector": "強健",       "signal": "正面"},
    ],
    "technical": [
        {"indicator": "RSI (14日)",    "value": "48.3",   "signal": "中性"},
        {"indicator": "MACD",         "value": "轉正",   "signal": "多頭"},
        {"indicator": "MA20",         "value": "NT$441", "signal": "站上"},
        {"indicator": "MA50",         "value": "NT$438", "signal": "站上"},
        {"indicator": "MA200",        "value": "NT$427", "signal": "站上"},
        {"indicator": "布林通道上軌", "value": "NT$478", "signal": "空間 +5.5%"},
        {"indicator": "布林通道下軌", "value": "NT$428", "signal": "支撐"},
        {"indicator": "KD值",         "value": "K:58 D:52", "signal": "黃金交叉"},
        {"indicator": "成交量",        "value": "均量+8%", "signal": "量增"},
        {"indicator": "外資持股",     "value": "71.3%",  "signal": "高度關注"},
    ],
    "catalyst": [
        {"event": "Q2 法說會",          "date": "2026-08",     "impact": "高",  "detail": "旺季指引確認，SoC佔比突破50%"},
        {"event": "iPhone 17 OLED出貨", "date": "2026-H2",     "impact": "高",  "detail": "TDDI新品 ASP提升，折疊機初期出貨"},
        {"event": "AI Edge SoC量產",    "date": "2026-Q3",     "impact": "中高", "detail": "首批AI SoC客戶交付，打開估值上限"},
        {"event": "電視SoC旗艦新品",   "date": "2026-Q2/Q3",  "impact": "中",  "detail": "高階TV SoC替代競品，提升ASP"},
        {"event": "年度股息發放",       "date": "2026-07",     "impact": "中",  "detail": "預估配息NT$19~22元，殖利率4~5%"},
        {"event": "ASIC客製化訂單",    "date": "2026-H2~2027","impact": "高",  "detail": "若拿下大客戶ASIC，EPS可再+7.5元"},
    ],
    "risk": [
        {"risk": "全球消費電子需求疲軟",      "severity": "高",  "mitigation": "SoC高端化對沖量的下降"},
        {"risk": "中國白牌顯示競爭加劇",     "severity": "中高", "mitigation": "聚焦高ASP OLED/AI細分市場"},
        {"risk": "美中關稅政策不確定性",     "severity": "中",  "mitigation": "台灣製造，直接關稅風險較低"},
        {"risk": "匯率（新台幣升值）",       "severity": "中",  "mitigation": "部分成本台幣計價，自然對沖"},
        {"risk": "研發費用超支（AI SoC）",   "severity": "低中", "mitigation": "Q1費用率21.66%，管控良好"},
        {"risk": "客戶集中（Apple/Samsung）", "severity": "中",  "mitigation": "多產品線分散，顯示IC份額穩固"},
    ],
    "analyst_consensus": {
        "buy": 12, "hold": 5, "sell": 1,
        "avg_target": 520,
        "high_target": 620,
        "low_target": 410,
    },
}

QUARTERLY_DATA = [
    {"quarter": "2024Q1", "revenue": 222.5, "gross_margin": 36.2, "op_margin": 14.8, "eps": 6.43},
    {"quarter": "2024Q2", "revenue": 258.3, "gross_margin": 37.8, "op_margin": 16.2, "eps": 8.12},
    {"quarter": "2024Q3", "revenue": 275.1, "gross_margin": 38.5, "op_margin": 17.1, "eps": 9.21},
    {"quarter": "2024Q4", "revenue": 251.8, "gross_margin": 38.3, "op_margin": 16.0, "eps": 9.18},
    {"quarter": "2025Q1", "revenue": 218.5, "gross_margin": 37.1, "op_margin": 14.2, "eps": 5.83},
    {"quarter": "2025Q2", "revenue": 249.7, "gross_margin": 37.5, "op_margin": 15.3, "eps": 7.12},
    {"quarter": "2025Q3", "revenue": 271.2, "gross_margin": 38.2, "op_margin": 16.5, "eps": 8.45},
    {"quarter": "2025Q4", "revenue": 267.6, "gross_margin": 37.9, "op_margin": 16.1, "eps": 5.47},
    {"quarter": "2026Q1", "revenue": 231.0, "gross_margin": 39.06, "op_margin": 17.4, "eps": 6.19},
]


# ── TradingView HTML helpers ─────────────────────────────────────

def tv_advanced_chart(symbol: str = "TWSE:3034", height: int = 500) -> str:
    return f"""
    <div class="tradingview-widget-container" style="height:{height}px;width:100%">
      <div id="tradingview_adv" style="height:calc({height}px - 32px);width:100%"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{
        "autosize": true,
        "symbol": "{symbol}",
        "interval": "D",
        "timezone": "Asia/Taipei",
        "theme": "light",
        "style": "1",
        "locale": "zh_TW",
        "toolbar_bg": "#f1f3f6",
        "enable_publishing": false,
        "allow_symbol_change": true,
        "watchlist": ["TWSE:3034","TWSE:2454","TWSE:2330"],
        "studies": ["RSI@tv-basicstudies","MACD@tv-basicstudies","BB@tv-basicstudies"],
        "container_id": "tradingview_adv",
        "show_popup_button": true,
        "popup_width": "1000",
        "popup_height": "650",
        "hide_side_toolbar": false,
        "withdateranges": true,
        "details": true,
        "hotlist": true,
        "calendar": true,
      }});
      </script>
    </div>
    """


def tv_financials(symbol: str = "TWSE:3034", height: int = 550) -> str:
    return f"""
    <div class="tradingview-widget-container" style="height:{height}px;width:100%">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-financials.js" async>
      {{
        "symbol": "{symbol}",
        "colorTheme": "light",
        "isTransparent": false,
        "largeChartUrl": "",
        "displayMode": "regular",
        "width": "100%",
        "height": "{height}",
        "locale": "zh_TW"
      }}
      </script>
    </div>
    """


def tv_symbol_info(symbol: str = "TWSE:3034") -> str:
    return f"""
    <div class="tradingview-widget-container" style="width:100%">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-symbol-info.js" async>
      {{
        "symbol": "{symbol}",
        "width": "100%",
        "locale": "zh_TW",
        "colorTheme": "light",
        "isTransparent": false
      }}
      </script>
    </div>
    """


def tv_technical_analysis(symbol: str = "TWSE:3034", height: int = 450) -> str:
    return f"""
    <div class="tradingview-widget-container" style="height:{height}px;width:100%">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      {{
        "interval": "1D",
        "width": "100%",
        "isTransparent": false,
        "height": "{height}",
        "symbol": "{symbol}",
        "showIntervalTabs": true,
        "displayMode": "single",
        "locale": "zh_TW",
        "colorTheme": "light"
      }}
      </script>
    </div>
    """


def tv_ticker_tape() -> str:
    return """
    <div class="tradingview-widget-container" style="width:100%">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
      {
        "symbols": [
          {"proName": "TWSE:3034", "title": "聯詠 3034"},
          {"proName": "TWSE:2330", "title": "台積電 2330"},
          {"proName": "TWSE:2454", "title": "聯發科 2454"},
          {"proName": "TWSE:3711", "title": "日月光 3711"},
          {"proName": "NASDAQ:NVDA", "title": "NVIDIA"},
          {"proName": "NASDAQ:QCOM", "title": "Qualcomm"}
        ],
        "showSymbolLogo": true,
        "isTransparent": false,
        "displayMode": "adaptive",
        "colorTheme": "light",
        "locale": "zh_TW"
      }
      </script>
    </div>
    """


# ── Download builders ────────────────────────────────────────────

def build_excel_workbook() -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        # Sheet 1 – Price matrix
        rows = []
        for key, sc in SCENARIOS.items():
            for pe in PE_MULTIPLES:
                price = round(sc["eps"] * pe)
                upside = round((price / CURRENT_PRICE - 1) * 100, 1)
                rows.append({
                    "情境": sc["label"], "EPS (元)": sc["eps"],
                    "PE倍數": pe, "目標股價 (NT$)": price,
                    "上行空間 (%)": upside,
                })
        pd.DataFrame(rows).to_excel(writer, sheet_name="股價矩陣", index=False)

        # Sheet 2 – EPS history + forecast
        eps_rows = [{"年度": r["year"], "EPS (元)": r["eps"], "類型": r["type"]} for r in EPS_HISTORY]
        for label, val in EPS_FORECASTS.items():
            eps_rows.append({"年度": label, "EPS (元)": val, "類型": "forecast"})
        pd.DataFrame(eps_rows).to_excel(writer, sheet_name="EPS軌跡", index=False)

        # Sheet 3 – ASP trajectory
        pd.DataFrame(ASP_DATA).rename(columns={
            "period": "期間", "asp": "SoC ASP (NT$)",
            "soc_rev": "SoC營收 (億)", "soc_pct": "SoC佔比 (%)",
        }).to_excel(writer, sheet_name="SoC ASP", index=False)

        # Sheet 4 – Monthly revenue
        pd.DataFrame(MONTHLY_REV).rename(columns={
            "month": "月份", "rev2026": "2026營收 (億)",
            "rev2025": "2025營收 (億)", "yoy": "年增率 (%)",
        }).to_excel(writer, sheet_name="月營收", index=False)

        # Sheet 5 – Quarterly financials
        pd.DataFrame(QUARTERLY_DATA).rename(columns={
            "quarter": "季度", "revenue": "營收 (億)",
            "gross_margin": "毛利率 (%)", "op_margin": "營益率 (%)", "eps": "EPS (元)",
        }).to_excel(writer, sheet_name="季度財務", index=False)

        # Sheet 6 – Income statement scenarios
        pd.DataFrame(INCOME_STMT).to_excel(writer, sheet_name="損益情境", index=False)

        # Sheet 7 – Fundamental analysis
        pd.DataFrame(STOCK_ANALYSIS["fundamental"]).rename(columns={
            "metric": "指標", "value": "數值", "vs_sector": "vs 同業", "signal": "訊號",
        }).to_excel(writer, sheet_name="基本面分析", index=False)

        # Sheet 8 – Technical analysis
        pd.DataFrame(STOCK_ANALYSIS["technical"]).rename(columns={
            "indicator": "技術指標", "value": "數值", "signal": "訊號",
        }).to_excel(writer, sheet_name="技術面分析", index=False)

        # Sheet 9 – Catalysts
        pd.DataFrame(STOCK_ANALYSIS["catalyst"]).rename(columns={
            "event": "催化劑", "date": "時間", "impact": "影響度", "detail": "說明",
        }).to_excel(writer, sheet_name="催化劑", index=False)

        # Sheet 10 – Risk factors
        pd.DataFrame(STOCK_ANALYSIS["risk"]).rename(columns={
            "risk": "風險", "severity": "嚴重度", "mitigation": "對策",
        }).to_excel(writer, sheet_name="風險因子", index=False)

    return buf.getvalue()


def build_csv_zip() -> bytes:
    import zipfile
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        def add(name: str, df: pd.DataFrame) -> None:
            zf.writestr(name, df.to_csv(index=False, encoding="utf-8-sig"))

        price_rows = []
        for key, sc in SCENARIOS.items():
            for pe in PE_MULTIPLES:
                price = round(sc["eps"] * pe)
                upside = round((price / CURRENT_PRICE - 1) * 100, 1)
                price_rows.append({
                    "情境": sc["label"], "EPS": sc["eps"], "PE": pe,
                    "目標股價": price, "上行空間%": upside,
                })
        add("股價矩陣.csv", pd.DataFrame(price_rows))

        eps_rows = [{"年度": r["year"], "EPS": r["eps"], "類型": r["type"]} for r in EPS_HISTORY]
        for label, val in EPS_FORECASTS.items():
            eps_rows.append({"年度": label, "EPS": val, "類型": "forecast"})
        add("EPS軌跡.csv", pd.DataFrame(eps_rows))

        add("SoC_ASP.csv", pd.DataFrame(ASP_DATA))
        add("月營收.csv", pd.DataFrame(MONTHLY_REV))
        add("季度財務.csv", pd.DataFrame(QUARTERLY_DATA))
        add("損益情境.csv", pd.DataFrame(INCOME_STMT))
        add("基本面分析.csv", pd.DataFrame(STOCK_ANALYSIS["fundamental"]))
        add("技術面分析.csv", pd.DataFrame(STOCK_ANALYSIS["technical"]))
        add("催化劑.csv", pd.DataFrame(STOCK_ANALYSIS["catalyst"]))
        add("風險因子.csv", pd.DataFrame(STOCK_ANALYSIS["risk"]))

        metadata = {
            "symbol": "3034.TW",
            "name": "聯詠科技",
            "current_price": CURRENT_PRICE,
            "report_date": REPORT_DATE,
            "generated_at": datetime.now().isoformat(),
        }
        zf.writestr("metadata.json", json.dumps(metadata, ensure_ascii=False, indent=2))

    return buf.getvalue()


def build_sqlite_db() -> bytes:
    buf = io.BytesIO()
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    conn = sqlite3.connect(tmp.name)

    def df_to_table(df: pd.DataFrame, table: str) -> None:
        df.to_sql(table, conn, if_exists="replace", index=False)

    # Price matrix
    rows = []
    for key, sc in SCENARIOS.items():
        for pe in PE_MULTIPLES:
            price = round(sc["eps"] * pe)
            upside = round((price / CURRENT_PRICE - 1) * 100, 1)
            rows.append({
                "scenario_key": key, "scenario_label": sc["label"],
                "eps": sc["eps"], "pe": pe, "target_price": price, "upside_pct": upside,
            })
    df_to_table(pd.DataFrame(rows), "price_matrix")

    # EPS
    eps_rows = [{"year": r["year"], "eps": r["eps"], "type": r["type"]} for r in EPS_HISTORY]
    for label, val in EPS_FORECASTS.items():
        eps_rows.append({"year": label, "eps": val, "type": "forecast"})
    df_to_table(pd.DataFrame(eps_rows), "eps_history")

    df_to_table(pd.DataFrame(ASP_DATA), "soc_asp")
    df_to_table(pd.DataFrame(MONTHLY_REV), "monthly_revenue")
    df_to_table(pd.DataFrame(QUARTERLY_DATA), "quarterly_financials")
    df_to_table(pd.DataFrame(INCOME_STMT), "income_scenarios")
    df_to_table(pd.DataFrame(STOCK_ANALYSIS["fundamental"]), "fundamental_analysis")
    df_to_table(pd.DataFrame(STOCK_ANALYSIS["technical"]), "technical_analysis")
    df_to_table(pd.DataFrame(STOCK_ANALYSIS["catalyst"]), "catalysts")
    df_to_table(pd.DataFrame(STOCK_ANALYSIS["risk"]), "risk_factors")

    meta_df = pd.DataFrame([{
        "symbol": "3034.TW", "name": "聯詠科技",
        "current_price": CURRENT_PRICE, "report_date": REPORT_DATE,
        "generated_at": datetime.now().isoformat(),
    }])
    df_to_table(meta_df, "metadata")

    conn.close()
    buf.write(Path(tmp.name).read_bytes())
    Path(tmp.name).unlink(missing_ok=True)
    return buf.getvalue()


# ── UI helpers ───────────────────────────────────────────────────

def signal_badge(signal: str) -> str:
    color_map = {
        "多頭": "🟢", "正面": "🟢", "低估": "🟢", "偏低": "🟡",
        "中性": "⚪", "站上": "🟢", "黃金交叉": "🟢", "量增": "🟢",
        "空頭": "🔴", "空間 +5.5%": "🟡", "支撐": "🟡",
        "高": "🔴", "中高": "🟠", "中": "🟡", "低中": "🟢",
    }
    return color_map.get(signal, "⚪")


# ── Main render ──────────────────────────────────────────────────

def main() -> None:
    # Ticker tape across the top
    components.html(tv_ticker_tape(), height=60, scrolling=False)

    # Header
    col_h1, col_h2 = st.columns([3, 1])
    with col_h1:
        st.markdown(
            """
            <div style="display:flex;align-items:center;gap:12px;margin-bottom:4px">
              <span style="background:#2563A8;color:#fff;font-weight:800;font-size:13px;
                           padding:4px 10px;border-radius:6px">NOVATEK 3034</span>
              <span style="background:#E6F5EC;color:#1A7A5E;border:1px solid #1A7A5E40;
                           border-radius:4px;padding:2px 8px;font-size:11px;font-weight:600">
                法說後更新
              </span>
              <span style="background:#FFF7ED;color:#D4770A;border:1px solid #D4770A40;
                           border-radius:4px;padding:2px 8px;font-size:11px;font-weight:600">
                2026.05.07
              </span>
            </div>
            <h1 style="font-size:22px;font-weight:800;color:#1A1A2E;margin:0;letter-spacing:-0.02em">
              聯詠科技　股價估值分析儀表板
            </h1>
            <p style="font-size:13px;color:#5A6070;margin-top:4px">
              TradingView 即時行情 × 官方財報 × SoC ASP 提升 × 費用率校準（Q1 實績）
            </p>
            """,
            unsafe_allow_html=True,
        )
    with col_h2:
        st.markdown(f"**現價**")
        st.metric("NT$453", delta="+2.3%", delta_color="normal", label_visibility="collapsed")
        st.caption(f"收盤 {REPORT_DATE}")

    st.divider()

    # Top KPIs
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("現價", "NT$453", "2026/05/07")
    k2.metric("Q1 EPS", "6.19 元", "-28.4% YoY")
    k3.metric("Q1 毛利率", "39.06%", "費用率 21.66%")
    k4.metric("Q2 指引", "275~285 億", "季增 +19~23%")
    k5.metric("SoC ASP", "NT$136", "+10% vs 2025均值")

    st.divider()

    # Main tabs
    tabs = st.tabs([
        "📈 即時行情 & TradingView",
        "💰 股價估值",
        "📊 EPS 軌跡",
        "🔧 SoC ASP",
        "📅 月營收",
        "🔍 股票分析",
        "📥 下載資料",
    ])

    # ── Tab 0: TradingView ─────────────────────────────────────
    with tabs[0]:
        st.subheader("即時行情 & 技術圖表（TradingView）")
        sym_col, _ = st.columns([1, 3])
        with sym_col:
            symbol_input = st.text_input("代號（可切換）", value="TWSE:3034")

        tv_col, ta_col = st.columns([3, 2])
        with tv_col:
            st.markdown("**K線圖 & 技術指標**")
            components.html(tv_advanced_chart(symbol_input, height=520), height=540, scrolling=False)
        with ta_col:
            st.markdown("**技術分析摘要**")
            components.html(tv_technical_analysis(symbol_input, height=450), height=470, scrolling=False)

        st.markdown("---")
        st.subheader("即時報價資訊")
        components.html(tv_symbol_info(symbol_input), height=120, scrolling=False)

        st.markdown("---")
        st.subheader("財務報表（TradingView Financials）")
        components.html(tv_financials(symbol_input, height=550), height=580, scrolling=False)

    # ── Tab 1: Valuation ────────────────────────────────────────
    with tabs[1]:
        st.subheader("股價估值分析")

        left_col, right_col = st.columns([1, 1])

        with left_col:
            st.markdown("**選擇情境**")
            active_scenario = st.radio(
                "情境",
                options=list(SCENARIOS.keys()),
                format_func=lambda k: f"{SCENARIOS[k]['label']}  —  EPS {SCENARIOS[k]['eps']} 元",
                label_visibility="collapsed",
            )

        with right_col:
            st.markdown("**選擇 PE 倍數**")
            active_pe = st.select_slider("PE 倍數", options=PE_MULTIPLES, value=20, label_visibility="collapsed")

        sc = SCENARIOS[active_scenario]
        target_price = round(sc["eps"] * active_pe)
        upside = round((target_price / CURRENT_PRICE - 1) * 100, 1)
        upside_str = f"{'▲' if upside > 0 else '▼'} {abs(upside)}% vs 現價 NT${CURRENT_PRICE}"

        res_col, _ = st.columns([1, 2])
        with res_col:
            st.metric(
                f"目標股價（{sc['label']} × {active_pe}x PE × EPS {sc['eps']}元）",
                f"NT${target_price}",
                upside_str,
                delta_color="normal" if upside > 0 else "inverse",
            )

        st.markdown("---")
        st.markdown("**完整股價矩陣（所有情境 × PE）**")

        matrix_data = {}
        for key, s in SCENARIOS.items():
            row = {"情境": s["label"], "EPS (元)": s["eps"]}
            for pe in PE_MULTIPLES:
                price = round(s["eps"] * pe)
                upside_v = round((price / CURRENT_PRICE - 1) * 100, 1)
                sign = "+" if upside_v > 0 else ""
                row[f"PE {pe}x"] = f"NT${price} ({sign}{upside_v}%)"
            matrix_data[key] = row

        matrix_df = pd.DataFrame(list(matrix_data.values()))
        st.dataframe(matrix_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("**各情境上行空間（基準 PE 20x）**")
        upside_chart = pd.DataFrame([
            {"情境": s["label"], "目標股價": round(s["eps"] * 20),
             "上行空間 (%)": round((s["eps"] * 20 / CURRENT_PRICE - 1) * 100)}
            for s in SCENARIOS.values()
        ])
        st.bar_chart(upside_chart.set_index("情境")["上行空間 (%)"])

        sc_cols = st.columns(len(SCENARIOS))
        for col, (key, s) in zip(sc_cols, SCENARIOS.items()):
            tp = round(s["eps"] * 20)
            up = round((tp / CURRENT_PRICE - 1) * 100, 1)
            col.metric(s["label"], f"NT${tp}", f"+{up}%")

    # ── Tab 2: EPS ──────────────────────────────────────────────
    with tabs[2]:
        st.subheader("EPS 歷史 × 2026 情境預估")

        eps_df = pd.DataFrame(EPS_HISTORY).set_index("year")["eps"].rename("實績 EPS")
        forecast_df = pd.DataFrame([
            {"year": "2026E(保守)", "EPS": 28.1},
            {"year": "2026E(基準)", "EPS": 32.5},
            {"year": "2026E(樂觀)", "EPS": 37.8},
        ]).set_index("year")

        st.line_chart(eps_df)

        st.markdown("**2026 情境預估**")
        fc_cols = st.columns(len(SCENARIOS))
        for col, (key, s) in zip(fc_cols, SCENARIOS.items()):
            yoy = round((s["eps"] / 26.87 - 1) * 100, 1)
            tp = round(s["eps"] * 20)
            col.metric(
                s["label"],
                f"{s['eps']} 元",
                f"{'+'if yoy>0 else ''}{yoy}% vs 2025",
            )
            col.caption(f"目標股 (20x): NT${tp}")

        st.markdown("---")
        st.markdown("**損益槓桿效應**")
        income_df = pd.DataFrame(INCOME_STMT)
        st.dataframe(income_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("**季度財務趨勢**")
        q_df = pd.DataFrame(QUARTERLY_DATA).set_index("quarter")
        st.line_chart(q_df[["eps", "gross_margin", "op_margin"]])
        st.dataframe(q_df.rename(columns={
            "revenue": "營收 (億)", "gross_margin": "毛利率 (%)",
            "op_margin": "營益率 (%)", "eps": "EPS (元)",
        }), use_container_width=True)

    # ── Tab 3: SoC ASP ──────────────────────────────────────────
    with tabs[3]:
        st.subheader("SoC ASP 提升軌跡")
        asp_df = pd.DataFrame(ASP_DATA).set_index("period")
        st.line_chart(asp_df[["asp"]])

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**ASP 資料**")
            st.dataframe(asp_df.rename(columns={
                "asp": "SoC ASP (NT$)", "soc_rev": "SoC營收 (億)", "soc_pct": "SoC佔比 (%)",
            }), use_container_width=True)

        with c2:
            st.markdown("**ASP 提升 → EPS 敏感度**")
            asp_sensitivity = pd.DataFrame([
                {"SoC ASP提升": "+NT$10", "毛利率額外+": "+0.36pp", "EPS額外+": "+1.5元",
                 "目標股(20x)": f"NT${round((32.5+1.5)*20)}"},
                {"SoC ASP提升": "+NT$20", "毛利率額外+": "+0.72pp", "EPS額外+": "+3.0元",
                 "目標股(20x)": f"NT${round((32.5+3.0)*20)}"},
                {"SoC ASP提升": "+NT$30", "毛利率額外+": "+1.08pp", "EPS額外+": "+4.5元",
                 "目標股(20x)": f"NT${round((32.5+4.5)*20)}"},
                {"SoC ASP提升": "+NT$50(ASIC)", "毛利率額外+": "+1.8pp", "EPS額外+": "+7.5元",
                 "目標股(20x)": f"NT${round((32.5+7.5)*20)}"},
            ])
            st.dataframe(asp_sensitivity, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.markdown("**ASP 驅動因子拆解**")
        for item in [
            ("產品組合升級（高階TV SoC/TCON）", "+5~6元"),
            ("OLED TDDI 新品滲透", "+3~4元"),
            ("AI Edge SoC 初期出貨", "+2~3元"),
            ("折疊機 OLED TDDI（H2）", "+NT$200+/片"),
        ]:
            st.markdown(f"- **{item[0]}**: `{item[1]}`")

        st.info("2026 Q1 反推：SoC ASP NT$136/顆（+9.7%）vs 2025均值 NT$124")

    # ── Tab 4: Monthly Revenue ───────────────────────────────────
    with tabs[4]:
        st.subheader("2026 vs 2025 月營收對比（億元）")
        rev_df = pd.DataFrame(MONTHLY_REV)
        chart_df = rev_df[["month", "rev2026", "rev2025"]].set_index("month")
        st.bar_chart(chart_df)

        st.dataframe(
            rev_df.rename(columns={
                "month": "月份", "rev2026": "2026 營收 (億)",
                "rev2025": "2025 營收 (億)", "yoy": "年增率 (%)",
            }),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("---")
        st.subheader("Q2 指引 vs 達標分析")
        q2c1, q2c2, q2c3 = st.columns(3)
        q2c1.metric("Q2 指引低標", "275 億", "季增 +19%")
        q2c2.metric("Q2 指引中位", "280 億", "季增 +21%")
        q2c3.metric("Q2 指引高標", "285 億", "季增 +23%")

        st.markdown("**全年營收達標路徑**")
        path_df = pd.DataFrame([
            {"季度": "Q1（已知）",       "季收 (億)": 231, "月均 (億)": 77.0,  "備注": "低點"},
            {"季度": "Q2（法說指引）",   "季收 (億)": 280, "月均 (億)": 93.3,  "備注": "成長加速"},
            {"季度": "Q3（旺季估）",     "季收 (億)": 305, "月均 (億)": 101.7, "備注": "iPhone+折疊"},
            {"季度": "Q4（淡季估）",     "季收 (億)": 285, "月均 (億)": 95.0,  "備注": "守住"},
            {"季度": "全年合計",         "季收 (億)": 1101, "月均 (億)": 91.8, "備注": "★ 達1,100億目標"},
        ])
        st.dataframe(path_df, use_container_width=True, hide_index=True)

    # ── Tab 5: Stock Analysis ────────────────────────────────────
    with tabs[5]:
        st.subheader("股票分析報告")

        ana_tabs = st.tabs(["📐 基本面", "📉 技術面", "⚡ 催化劑", "⚠️ 風險", "🏦 分析師"])

        with ana_tabs[0]:
            st.markdown("**基本面指標**")
            fund_df = pd.DataFrame(STOCK_ANALYSIS["fundamental"])
            fund_df["訊號"] = fund_df["signal"].apply(lambda s: f"{signal_badge(s)} {s}")
            st.dataframe(
                fund_df.rename(columns={"metric": "指標", "value": "數值", "vs_sector": "vs 同業"})[
                    ["指標", "數值", "vs 同業", "訊號"]
                ],
                use_container_width=True,
                hide_index=True,
            )

        with ana_tabs[1]:
            st.markdown("**技術指標**")
            tech_df = pd.DataFrame(STOCK_ANALYSIS["technical"])
            tech_df["訊號"] = tech_df["signal"].apply(lambda s: f"{signal_badge(s)} {s}")
            st.dataframe(
                tech_df.rename(columns={"indicator": "指標", "value": "數值"})[["指標", "數值", "訊號"]],
                use_container_width=True,
                hide_index=True,
            )

        with ana_tabs[2]:
            st.markdown("**催化劑追蹤**")
            cat_df = pd.DataFrame(STOCK_ANALYSIS["catalyst"])
            cat_df["影響度"] = cat_df["impact"].apply(
                lambda v: f"{'🔴' if v=='高' else '🟠' if v=='中高' else '🟡'} {v}"
            )
            st.dataframe(
                cat_df.rename(columns={"event": "催化劑", "date": "時間", "detail": "說明"})[
                    ["催化劑", "時間", "影響度", "說明"]
                ],
                use_container_width=True,
                hide_index=True,
            )

        with ana_tabs[3]:
            st.markdown("**風險矩陣**")
            risk_df = pd.DataFrame(STOCK_ANALYSIS["risk"])
            risk_df["嚴重度"] = risk_df["severity"].apply(
                lambda v: f"{'🔴' if v=='高' else '🟠' if v=='中高' else '🟡' if v=='中' else '🟢'} {v}"
            )
            st.dataframe(
                risk_df.rename(columns={"risk": "風險", "mitigation": "對策"})[
                    ["風險", "嚴重度", "對策"]
                ],
                use_container_width=True,
                hide_index=True,
            )

        with ana_tabs[4]:
            ac = STOCK_ANALYSIS["analyst_consensus"]
            total = ac["buy"] + ac["hold"] + ac["sell"]
            st.markdown("**分析師共識**")
            a1, a2, a3, a4, a5, a6 = st.columns(6)
            a1.metric("買入", ac["buy"], f"{round(ac['buy']/total*100)}%")
            a2.metric("持有", ac["hold"], f"{round(ac['hold']/total*100)}%")
            a3.metric("賣出", ac["sell"], f"{round(ac['sell']/total*100)}%")
            a4.metric("平均目標", f"NT${ac['avg_target']}", f"+{round((ac['avg_target']/CURRENT_PRICE-1)*100,1)}%")
            a5.metric("最高目標", f"NT${ac['high_target']}", f"+{round((ac['high_target']/CURRENT_PRICE-1)*100,1)}%")
            a6.metric("最低目標", f"NT${ac['low_target']}", f"{round((ac['low_target']/CURRENT_PRICE-1)*100,1)}%")

            st.progress(ac["buy"] / total, text=f"買入比例 {round(ac['buy']/total*100)}%")

    # ── Tab 6: Download ──────────────────────────────────────────
    with tabs[6]:
        st.subheader("下載資料")
        st.markdown(
            "所有分析數據可匯出為以下格式，包含：股價矩陣、EPS軌跡、SoC ASP、"
            "月營收、季度財務、損益情境、基本面 & 技術面分析、催化劑、風險因子。"
        )

        dl1, dl2, dl3 = st.columns(3)

        with dl1:
            st.markdown("### 📊 Excel (.xlsx)")
            st.markdown("多工作表，含全部分析資料，支援 Excel / Numbers 開啟。")
            if st.button("生成 Excel", use_container_width=True, key="gen_excel"):
                with st.spinner("生成中…"):
                    xlsx_bytes = build_excel_workbook()
                st.success("Excel 已生成！")
                st.download_button(
                    "⬇ 下載 Excel",
                    data=xlsx_bytes,
                    file_name=f"聯詠3034_估值分析_{REPORT_DATE}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True,
                    key="dl_excel",
                )

        with dl2:
            st.markdown("### 📁 CSV 壓縮包 (.zip)")
            st.markdown("每個分析表獨立 CSV 檔，含 metadata.json，UTF-8-sig 編碼（Excel 相容）。")
            if st.button("生成 CSV ZIP", use_container_width=True, key="gen_csv"):
                with st.spinner("生成中…"):
                    zip_bytes = build_csv_zip()
                st.success("CSV ZIP 已生成！")
                st.download_button(
                    "⬇ 下載 CSV ZIP",
                    data=zip_bytes,
                    file_name=f"聯詠3034_估值分析_{REPORT_DATE}.zip",
                    mime="application/zip",
                    use_container_width=True,
                    key="dl_csv",
                )

        with dl3:
            st.markdown("### 🗄️ SQLite 資料庫 (.db)")
            st.markdown("結構化資料庫，適合用 Python / DBeaver / TablePlus 進行二次查詢分析。")
            if st.button("生成 SQLite DB", use_container_width=True, key="gen_db"):
                with st.spinner("生成中…"):
                    db_bytes = build_sqlite_db()
                st.success("SQLite DB 已生成！")
                st.download_button(
                    "⬇ 下載 SQLite DB",
                    data=db_bytes,
                    file_name=f"聯詠3034_估值分析_{REPORT_DATE}.db",
                    mime="application/octet-stream",
                    use_container_width=True,
                    key="dl_db",
                )

        st.divider()
        st.markdown("**資料表清單**")
        table_info = pd.DataFrame([
            {"資料表": "price_matrix",       "說明": "股價矩陣（情境 × PE）"},
            {"資料表": "eps_history",         "說明": "EPS 歷史 + 2026 情境預估"},
            {"資料表": "soc_asp",             "說明": "SoC ASP 提升軌跡"},
            {"資料表": "monthly_revenue",     "說明": "2025/2026 月營收對比"},
            {"資料表": "quarterly_financials","說明": "季度財務（2024Q1-2026Q1）"},
            {"資料表": "income_scenarios",    "說明": "損益情境（保守/基準/樂觀）"},
            {"資料表": "fundamental_analysis","說明": "基本面指標"},
            {"資料表": "technical_analysis",  "說明": "技術面指標"},
            {"資料表": "catalysts",           "說明": "催化劑追蹤"},
            {"資料表": "risk_factors",        "說明": "風險因子矩陣"},
            {"資料表": "metadata",            "說明": "報告元資料"},
        ])
        st.dataframe(table_info, use_container_width=True, hide_index=True)

        st.caption(
            "⚠️ 本儀表板基於官方法說數據、Q1財報及研究模型，"
            "股價預估含不確定性，不構成投資建議。2026.05.07 大會計師研究團隊"
        )


if __name__ == "__main__":
    main()
else:
    main()

// ── Static dataset for 聯詠科技 3034.TW ──────────────────────────

export const META = {
  symbol: "TWSE:3034",
  name: "聯詠科技",
  currentPrice: 453,
  reportDate: "2026-05-07",
};

export const SCENARIOS = {
  bear:  { label: "保守",   eps: 28.1,  color: "#94a3b8", bg: "#f1f5f9" },
  base:  { label: "基準",   eps: 32.5,  color: "#2563A8", bg: "#EBF3FF" },
  bull:  { label: "樂觀",   eps: 37.8,  color: "#1A7A5E", bg: "#E6F5EC" },
  aitam: { label: "ai-tam", eps: 33.9,  color: "#D4770A", bg: "#FFF7ED" },
};

export const PE_MULTIPLES = [16, 18, 20, 22, 25];

export const EPS_HISTORY = [
  { year: "2020", eps: 19.00 },
  { year: "2021", eps: 63.00 },
  { year: "2022", eps: 46.00 },
  { year: "2023", eps: 38.00 },
  { year: "2024", eps: 32.94 },
  { year: "2025", eps: 26.87 },
];

export const EPS_FORECASTS = {
  "2026E(保守)":    28.1,
  "2026E(基準)":    32.5,
  "2026E(樂觀)":    37.8,
  "2026E(ai-tam)": 33.9,
};

export const ASP_DATA = [
  { period: "2025全年",  asp: 124, socRev: 372, socPct: 37 },
  { period: "2026 Q1",  asp: 136, socRev: 410, socPct: 44 },
  { period: "2026 H1E", asp: 140, socRev: 462, socPct: 50 },
  { period: "2026 H2E", asp: 145, socRev: 510, socPct: 54 },
  { period: "2027E",    asp: 155, socRev: 558, socPct: 56 },
];

export const MONTHLY_REV = [
  { month: "Jan", rev2026: 76.17,  rev2025: 84.81, yoy: -10 },
  { month: "Feb", rev2026: 70.59,  rev2025: 92.67, yoy: -24 },
  { month: "Mar", rev2026: 84.69,  rev2025: 93.72, yoy: -10 },
  { month: "Apr", rev2026: 92.25,  rev2025: 91.20, yoy:   1 },
  { month: "May", rev2026: null,   rev2025: 86.07, yoy: null },
  { month: "Jun", rev2026: null,   rev2025: 84.25, yoy: null },
  { month: "Jul", rev2026: null,   rev2025: 81.20, yoy: null },
  { month: "Aug", rev2026: null,   rev2025: 81.75, yoy: null },
  { month: "Sep", rev2026: null,   rev2025: 82.78, yoy: null },
  { month: "Oct", rev2026: null,   rev2025: 78.79, yoy: null },
  { month: "Nov", rev2026: null,   rev2025: 76.19, yoy: null },
  { month: "Dec", rev2026: null,   rev2025: 73.20, yoy: null },
];

export const QUARTERLY_DATA = [
  { quarter: "2024Q1", revenue: 222.5, grossMargin: 36.2, opMargin: 14.8, eps: 6.43 },
  { quarter: "2024Q2", revenue: 258.3, grossMargin: 37.8, opMargin: 16.2, eps: 8.12 },
  { quarter: "2024Q3", revenue: 275.1, grossMargin: 38.5, opMargin: 17.1, eps: 9.21 },
  { quarter: "2024Q4", revenue: 251.8, grossMargin: 38.3, opMargin: 16.0, eps: 9.18 },
  { quarter: "2025Q1", revenue: 218.5, grossMargin: 37.1, opMargin: 14.2, eps: 5.83 },
  { quarter: "2025Q2", revenue: 249.7, grossMargin: 37.5, opMargin: 15.3, eps: 7.12 },
  { quarter: "2025Q3", revenue: 271.2, grossMargin: 38.2, opMargin: 16.5, eps: 8.45 },
  { quarter: "2025Q4", revenue: 267.6, grossMargin: 37.9, opMargin: 16.1, eps: 5.47 },
  { quarter: "2026Q1", revenue: 231.0, grossMargin: 39.06, opMargin: 17.4, eps: 6.19 },
];

export const INCOME_SCENARIOS = [
  { item: "營收 (億元)",     "2025實績": "1,007", 保守: "1,055", 基準: "1,100", 樂觀: "1,150" },
  { item: "毛利率",          "2025實績": "37.7%", 保守: "40%",   基準: "41%",   樂觀: "42%"   },
  { item: "費用率",          "2025實績": "21.7%", 保守: "22%",   基準: "21.5%", 樂觀: "21%"   },
  { item: "營益率",          "2025實績": "16.0%", 保守: "18%",   基準: "19.5%", 樂觀: "21%"   },
  { item: "稅後淨利 (億元)", "2025實績": "163",   保守: "144",   基準: "198",   樂觀: "218"   },
  { item: "EPS (元)",        "2025實績": "26.87", 保守: "28.1",  基準: "32.5",  樂觀: "37.8"  },
  { item: "vs 2025",         "2025實績": "—",     保守: "+4.6%", 基準: "+21%",  樂觀: "+40.7%"},
];

export const ASP_SENSITIVITY = [
  { label: "+NT$10",       gmDelta: "+0.36pp", epsDelta: "+1.5元", target20x: Math.round((32.5+1.5)*20) },
  { label: "+NT$20",       gmDelta: "+0.72pp", epsDelta: "+3.0元", target20x: Math.round((32.5+3.0)*20) },
  { label: "+NT$30",       gmDelta: "+1.08pp", epsDelta: "+4.5元", target20x: Math.round((32.5+4.5)*20) },
  { label: "+NT$50(ASIC)", gmDelta: "+1.8pp",  epsDelta: "+7.5元", target20x: Math.round((32.5+7.5)*20) },
];

export const ANNUAL_PATH = [
  { q: "Q1（已知）",     rev: 231,  avg: 77.0,  note: "低點" },
  { q: "Q2（法說指引）", rev: 280,  avg: 93.3,  note: "成長加速" },
  { q: "Q3（旺季估）",   rev: 305,  avg: 101.7, note: "iPhone+折疊" },
  { q: "Q4（淡季估）",   rev: 285,  avg: 95.0,  note: "守住" },
  { q: "全年合計",       rev: 1101, avg: 91.8,  note: "★ 達1,100億目標", highlight: true },
];

export const FUNDAMENTAL = [
  { metric: "P/E (TTM)",       value: "16.8x",   vsSector: "折價 12%",  signal: "偏低" },
  { metric: "P/E (2026E基準)", value: "13.9x",   vsSector: "折價 27%",  signal: "低估" },
  { metric: "P/B",             value: "3.2x",    vsSector: "合理",       signal: "中性" },
  { metric: "EV/EBITDA",       value: "9.8x",    vsSector: "折價 18%",  signal: "偏低" },
  { metric: "股息殖利率",      value: "4.2%",    vsSector: "高於均值",   signal: "正面" },
  { metric: "ROE",             value: "19.3%",   vsSector: "高於均值",   signal: "正面" },
  { metric: "ROA",             value: "14.7%",   vsSector: "高於均值",   signal: "正面" },
  { metric: "流動比率",        value: "3.8x",    vsSector: "健全",       signal: "正面" },
  { metric: "負債比率",        value: "24%",     vsSector: "低",         signal: "正面" },
  { metric: "淨現金 (億元)",   value: "+287",    vsSector: "強健",       signal: "正面" },
];

export const TECHNICAL = [
  { indicator: "RSI (14日)",    value: "48.3",        signal: "中性",   sentiment: "neutral" },
  { indicator: "MACD",         value: "轉正",         signal: "多頭",   sentiment: "bull" },
  { indicator: "MA20",         value: "NT$441",       signal: "站上",   sentiment: "bull" },
  { indicator: "MA50",         value: "NT$438",       signal: "站上",   sentiment: "bull" },
  { indicator: "MA200",        value: "NT$427",       signal: "站上",   sentiment: "bull" },
  { indicator: "布林上軌",     value: "NT$478",       signal: "+5.5%空間", sentiment: "neutral" },
  { indicator: "布林下軌",     value: "NT$428",       signal: "支撐",   sentiment: "neutral" },
  { indicator: "KD值",         value: "K:58 D:52",   signal: "黃金交叉", sentiment: "bull" },
  { indicator: "成交量",       value: "均量+8%",      signal: "量增",   sentiment: "bull" },
  { indicator: "外資持股",     value: "71.3%",        signal: "高關注", sentiment: "bull" },
];

export const CATALYSTS = [
  { event: "Q2 法說會",          date: "2026-08",    impact: "高",  detail: "旺季指引確認，SoC佔比突破50%" },
  { event: "iPhone 17 OLED出貨", date: "2026-H2",   impact: "高",  detail: "TDDI新品 ASP提升，折疊機初期出貨" },
  { event: "AI Edge SoC量產",    date: "2026-Q3",   impact: "中高", detail: "首批AI SoC交付，打開估值上限" },
  { event: "電視SoC旗艦新品",   date: "2026-Q2/Q3", impact: "中",  detail: "高階TV SoC替代競品，提升ASP" },
  { event: "年度股息發放",       date: "2026-07",   impact: "中",  detail: "預估配息NT$19~22元，殖利率4~5%" },
  { event: "ASIC客製化訂單",    date: "2026-H2~2027",impact: "高", detail: "拿下大客戶ASIC，EPS可再+7.5元" },
];

export const RISKS = [
  { risk: "全球消費電子需求疲軟",     severity: "高",  mitigation: "SoC高端化對沖量的下降" },
  { risk: "中國白牌顯示競爭加劇",    severity: "中高", mitigation: "聚焦高ASP OLED/AI細分市場" },
  { risk: "美中關稅政策不確定性",    severity: "中",  mitigation: "台灣製造，直接關稅風險較低" },
  { risk: "匯率（新台幣升值）",      severity: "中",  mitigation: "部分成本台幣計價，自然對沖" },
  { risk: "研發費用超支（AI SoC）",  severity: "低中", mitigation: "Q1費用率21.66%，管控良好" },
  { risk: "客戶集中（Apple/Samsung）",severity: "中",  mitigation: "多產品線分散，顯示IC份額穩固" },
];

export const ANALYST_CONSENSUS = {
  buy: 12, hold: 5, sell: 1,
  avgTarget: 520, highTarget: 620, lowTarget: 410,
};

export const WATCHLIST = [
  "TWSE:3034", "TWSE:2330", "TWSE:2454",
  "NASDAQ:NVDA", "NASDAQ:QCOM", "NASDAQ:AVGO",
];

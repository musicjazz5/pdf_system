import { useState, useEffect, Component } from "react";
import { KPI, Tag } from "./components/Primitives.jsx";
import TabTradingView from "./components/TabTradingView.jsx";
import TabValuation   from "./components/TabValuation.jsx";
import TabEPS         from "./components/TabEPS.jsx";
import TabASP         from "./components/TabASP.jsx";
import TabRevenue     from "./components/TabRevenue.jsx";
import TabAnalysis    from "./components/TabAnalysis.jsx";
import TabDownload    from "./components/TabDownload.jsx";

const TABS = [
  { id: "tv",        label: "📈 即時行情",  component: TabTradingView },
  { id: "valuation", label: "💰 股價估值",  component: TabValuation },
  { id: "eps",       label: "📊 EPS軌跡",   component: TabEPS },
  { id: "asp",       label: "🔧 SoC ASP",  component: TabASP },
  { id: "revenue",   label: "📅 月營收",    component: TabRevenue },
  { id: "analysis",  label: "🔍 股票分析",  component: TabAnalysis },
  { id: "download",  label: "📥 下載資料",  component: TabDownload },
];

// ── Error boundary ───────────────────────────────────────────────
class ErrorBoundary extends Component {
  constructor(props) { super(props); this.state = { error: null }; }
  static getDerivedStateFromError(error) { return { error }; }
  render() {
    if (this.state.error) {
      return (
        <div style={{ padding: 24, background: "#FEF2F2", borderRadius: 12, margin: 16, border: "1px solid #FCA5A5" }}>
          <div style={{ fontWeight: 700, color: "#C0392B", marginBottom: 8 }}>⚠️ 渲染錯誤</div>
          <pre style={{ fontSize: 12, color: "#7F1D1D", whiteSpace: "pre-wrap" }}>
            {this.state.error.message}
          </pre>
        </div>
      );
    }
    return this.props.children;
  }
}

// ── TradingView ticker tape via useEffect script injection ───────
function TickerTape() {
  useEffect(() => {
    const container = document.getElementById("tv-ticker-tape");
    if (!container || container.dataset.loaded) return;
    container.dataset.loaded = "1";

    const widget = document.createElement("div");
    widget.className = "tradingview-widget-container__widget";
    container.appendChild(widget);

    const script = document.createElement("script");
    script.type = "text/javascript";
    script.src = "https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js";
    script.async = true;
    script.textContent = JSON.stringify({
      symbols: [
        { proName: "TWSE:3034",   title: "聯詠 3034" },
        { proName: "TWSE:2330",   title: "台積電 2330" },
        { proName: "TWSE:2454",   title: "聯發科 2454" },
        { proName: "NASDAQ:NVDA", title: "NVIDIA" },
        { proName: "NASDAQ:QCOM", title: "Qualcomm" },
        { proName: "NASDAQ:AVGO", title: "Broadcom" },
      ],
      showSymbolLogo: true,
      isTransparent: false,
      displayMode: "adaptive",
      colorTheme: "light",
      locale: "zh_TW",
    });
    container.appendChild(script);
  }, []);

  return <div id="tv-ticker-tape" className="tradingview-widget-container" style={{ minHeight: 46 }} />;
}

// ── Main app ─────────────────────────────────────────────────────
export default function App() {
  const [activeTab, setActiveTab] = useState("tv");
  const ActiveComponent = TABS.find((t) => t.id === activeTab)?.component ?? TabTradingView;

  return (
    <div style={{
      fontFamily: "'Noto Sans TC','PingFang TC',system-ui,sans-serif",
      background: "#F7F9FC",
      minHeight: "100vh",
    }}>
      <ErrorBoundary>
        <TickerTape />
      </ErrorBoundary>

      <div style={{ maxWidth: 980, margin: "0 auto", padding: "20px 16px" }}>

        {/* Header */}
        <div style={{ marginBottom: 20 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8, flexWrap: "wrap" }}>
            <div style={{
              background: "#2563A8", color: "#fff",
              fontWeight: 800, fontSize: 13, padding: "4px 10px",
              borderRadius: 6, letterSpacing: "0.05em",
            }}>NOVATEK 3034</div>
            <Tag color="#1A7A5E">法說後更新</Tag>
            <Tag color="#D4770A">2026.05.07</Tag>
            <Tag color="#7C3AED">TradingView 整合版</Tag>
          </div>
          <h1 style={{ fontSize: 22, fontWeight: 800, color: "#1A1A2E", margin: "0 0 4px", letterSpacing: "-0.02em" }}>
            聯詠科技　股價估值分析儀表板
          </h1>
          <div style={{ fontSize: 13, color: "#5A6070" }}>
            即時行情 × 官方財報 × SoC ASP 提升 × 費用率校準（Q1 實績）
          </div>
        </div>

        {/* KPIs */}
        <div style={{ display: "flex", gap: 10, marginBottom: 20, flexWrap: "wrap" }}>
          <KPI label="現價"      value="NT$453"    sub="2026/05/07 收盤"    color="#1A1A2E" />
          <KPI label="Q1 EPS"   value="6.19元"    sub="官方確認"            color="#2563A8" badge="YoY -28.4%" />
          <KPI label="Q1 毛利率" value="39.06%"   sub="費用率 21.66%"       color="#1A7A5E" />
          <KPI label="Q2 指引"  value="275~285億"  sub="季增 19~23%"         color="#D4770A" badge="三線齊揚" />
          <KPI label="SoC ASP"  value="NT$136"    sub="vs 2025均值 NT$124"  color="#7C3AED" badge="ASP +10%" />
        </div>

        {/* Tab bar */}
        <div style={{
          display: "flex", gap: 4, marginBottom: 20,
          background: "#E2E8F0", borderRadius: 10, padding: 4,
          flexWrap: "wrap",
        }}>
          {TABS.map((t) => (
            <button key={t.id} onClick={() => setActiveTab(t.id)} style={{
              flex: 1, minWidth: 80,
              padding: "8px 4px", borderRadius: 7, border: "none", cursor: "pointer",
              fontSize: 12, fontWeight: activeTab === t.id ? 700 : 500,
              background: activeTab === t.id ? "#fff" : "transparent",
              color: activeTab === t.id ? "#2563A8" : "#5A6070",
              boxShadow: activeTab === t.id ? "0 1px 4px rgba(0,0,0,0.1)" : "none",
              transition: "all 0.15s",
              whiteSpace: "nowrap",
            }}>{t.label}</button>
          ))}
        </div>

        {/* Active tab content — each tab is independently error-bounded */}
        <ErrorBoundary key={activeTab}>
          <ActiveComponent />
        </ErrorBoundary>

        {/* Footer */}
        <div style={{
          marginTop: 24, padding: "12px 16px",
          background: "#F1F5F9", borderRadius: 8,
          fontSize: 11, color: "#94a3b8",
        }}>
          ⚠️ 本儀表板基於官方法說數據、Q1財報及研究模型，股價預估含不確定性，
          不構成投資建議。2026.05.07 大會計師研究團隊
        </div>
      </div>
    </div>
  );
}

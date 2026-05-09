import { useRef, useState } from "react";
import { useTVAdvancedChart } from "../hooks/useTradingView.js";
import { Card, SectionTitle } from "./Primitives.jsx";

// Embed a standalone TradingView widget via iframe (no script conflicts)
function TVEmbed({ src, height = 420 }) {
  return (
    <iframe
      src={src}
      style={{ width: "100%", height, border: "none", borderRadius: 10 }}
      allowTransparency
      allowFullScreen
      scrolling="no"
      frameBorder="0"
      title="TradingView"
    />
  );
}

function buildAdvancedChartUrl(symbol) {
  const params = new URLSearchParams({
    symbol,
    interval: "D",
    timezone: "Asia/Taipei",
    theme: "light",
    style: "1",
    locale: "zh_TW",
    toolbar_bg: "#f1f3f6",
    enable_publishing: "false",
    withdateranges: "true",
    hide_side_toolbar: "false",
    allow_symbol_change: "true",
    details: "true",
    hotlist: "true",
    calendar: "true",
    studies: "RSI%40tv-basicstudies,MACD%40tv-basicstudies,BB%40tv-basicstudies",
    show_popup_button: "true",
  });
  return `https://www.tradingview.com/widgetembed/?${params}`;
}

function buildTechAnalysisUrl(symbol) {
  const params = new URLSearchParams({
    symbol,
    interval: "1D",
    width: "100%",
    isTransparent: "false",
    showIntervalTabs: "true",
    displayMode: "single",
    locale: "zh_TW",
    colorTheme: "light",
  });
  return `https://www.tradingview.com/embed-widget/technical-analysis/?${params}`;
}

function buildFinancialsUrl(symbol) {
  const params = new URLSearchParams({
    symbol,
    colorTheme: "light",
    isTransparent: "false",
    displayMode: "regular",
    locale: "zh_TW",
  });
  return `https://www.tradingview.com/embed-widget/financials/?${params}`;
}

function buildSymbolInfoUrl(symbol) {
  const params = new URLSearchParams({
    symbol,
    locale: "zh_TW",
    colorTheme: "light",
    isTransparent: "false",
  });
  return `https://www.tradingview.com/embed-widget/symbol-info/?${params}`;
}

const WATCHLIST = ["TWSE:3034", "TWSE:2330", "TWSE:2454", "NASDAQ:NVDA", "NASDAQ:QCOM", "NASDAQ:AVGO"];

export default function TabTradingView() {
  const [symbol, setSymbol] = useState("TWSE:3034");
  const [inputVal, setInputVal] = useState("TWSE:3034");

  const apply = () => setSymbol(inputVal.trim().toUpperCase() || "TWSE:3034");

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

      {/* Symbol selector */}
      <Card>
        <SectionTitle accent="#7C3AED">即時行情 & TradingView 圖表</SectionTitle>
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap", alignItems: "center", marginBottom: 12 }}>
          <input
            value={inputVal}
            onChange={(e) => setInputVal(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && apply()}
            placeholder="例如 TWSE:3034"
            style={{
              padding: "8px 14px", borderRadius: 8, border: "1.5px solid #E2E8F0",
              fontSize: 13, fontWeight: 600, width: 200, outline: "none",
            }}
          />
          <button onClick={apply} style={{
            padding: "8px 18px", borderRadius: 8, background: "#2563A8",
            color: "#fff", border: "none", fontWeight: 700, cursor: "pointer", fontSize: 13,
          }}>切換</button>
          <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
            {WATCHLIST.map((s) => (
              <button key={s} onClick={() => { setInputVal(s); setSymbol(s); }} style={{
                padding: "5px 10px", borderRadius: 6, fontSize: 11, fontWeight: 600,
                border: `1.5px solid ${symbol === s ? "#2563A8" : "#E2E8F0"}`,
                background: symbol === s ? "#EBF3FF" : "#fff",
                color: symbol === s ? "#2563A8" : "#5A6070",
                cursor: "pointer",
              }}>{s.split(":")[1]}</button>
            ))}
          </div>
        </div>
      </Card>

      {/* Main chart + technical analysis side-by-side */}
      <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>
        <Card style={{ flex: 3, minWidth: 320, padding: 0, overflow: "hidden" }}>
          <div style={{ padding: "14px 20px 0", borderBottom: "1px solid #E2E8F0" }}>
            <SectionTitle>K線圖 & 技術指標</SectionTitle>
          </div>
          <TVEmbed src={buildAdvancedChartUrl(symbol)} height={520} />
        </Card>

        <Card style={{ flex: 2, minWidth: 280, padding: 0, overflow: "hidden" }}>
          <div style={{ padding: "14px 20px 0", borderBottom: "1px solid #E2E8F0" }}>
            <SectionTitle accent="#D4770A">技術分析摘要</SectionTitle>
          </div>
          <TVEmbed src={buildTechAnalysisUrl(symbol)} height={520} />
        </Card>
      </div>

      {/* Symbol info bar */}
      <Card style={{ padding: 0, overflow: "hidden" }}>
        <TVEmbed src={buildSymbolInfoUrl(symbol)} height={108} />
      </Card>

      {/* Financials */}
      <Card style={{ padding: 0, overflow: "hidden" }}>
        <div style={{ padding: "14px 20px 0", borderBottom: "1px solid #E2E8F0" }}>
          <SectionTitle accent="#1A7A5E">財務報表（TradingView Financials）</SectionTitle>
        </div>
        <TVEmbed src={buildFinancialsUrl(symbol)} height={560} />
      </Card>
    </div>
  );
}

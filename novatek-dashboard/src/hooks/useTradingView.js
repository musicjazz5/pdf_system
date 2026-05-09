import { useEffect, useRef } from "react";

let tvScriptLoaded = false;
const TV_SRC = "https://s3.tradingview.com/tv.js";

function loadTVScript() {
  return new Promise((resolve) => {
    if (tvScriptLoaded) { resolve(); return; }
    const s = document.createElement("script");
    s.src = TV_SRC;
    s.onload = () => { tvScriptLoaded = true; resolve(); };
    document.head.appendChild(s);
  });
}

/**
 * Mounts a TradingView Advanced Chart widget into `containerRef`.
 * Re-creates the widget whenever `symbol` changes.
 */
export function useTVAdvancedChart(containerRef, symbol, options = {}) {
  useEffect(() => {
    if (!containerRef.current) return;
    containerRef.current.innerHTML = "";
    const inner = document.createElement("div");
    inner.id = `tv_chart_${Date.now()}`;
    inner.style.cssText = "width:100%;height:100%";
    containerRef.current.appendChild(inner);

    loadTVScript().then(() => {
      if (!window.TradingView) return;
      new window.TradingView.widget({
        autosize: true,
        symbol,
        interval: "D",
        timezone: "Asia/Taipei",
        theme: "light",
        style: "1",
        locale: "zh_TW",
        toolbar_bg: "#f1f3f6",
        enable_publishing: false,
        allow_symbol_change: true,
        watchlist: ["TWSE:3034", "TWSE:2330", "TWSE:2454", "NASDAQ:NVDA", "NASDAQ:QCOM"],
        studies: ["RSI@tv-basicstudies", "MACD@tv-basicstudies", "BB@tv-basicstudies"],
        container_id: inner.id,
        show_popup_button: true,
        popup_width: "1000",
        popup_height: "650",
        withdateranges: true,
        details: true,
        hotlist: true,
        calendar: true,
        ...options,
      });
    });
  }, [symbol]);
}

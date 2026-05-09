import { useState } from "react";
import { FUNDAMENTAL, TECHNICAL, CATALYSTS, RISKS, ANALYST_CONSENSUS, META } from "../data/novatek.js";
import { Card, SectionTitle, Tag, SignalBadge, SeverityBadge, ImpactBadge } from "./Primitives.jsx";

const SUB_TABS = ["📐 基本面", "📉 技術面", "⚡ 催化劑", "⚠️ 風險", "🏦 分析師"];

export default function TabAnalysis() {
  const [sub, setSub] = useState(0);
  const P = META.currentPrice;
  const ac = ANALYST_CONSENSUS;
  const total = ac.buy + ac.hold + ac.sell;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

      {/* Sub-tab bar */}
      <div style={{ display: "flex", gap: 4, background: "#E2E8F0", borderRadius: 10, padding: 4 }}>
        {SUB_TABS.map((t, i) => (
          <button key={i} onClick={() => setSub(i)} style={{
            flex: 1, padding: "8px 0", borderRadius: 7, border: "none", cursor: "pointer",
            fontSize: 12, fontWeight: sub === i ? 700 : 500,
            background: sub === i ? "#fff" : "transparent",
            color: sub === i ? "#2563A8" : "#5A6070",
            boxShadow: sub === i ? "0 1px 4px rgba(0,0,0,0.1)" : "none",
            transition: "all 0.15s",
          }}>{t}</button>
        ))}
      </div>

      {/* 基本面 */}
      {sub === 0 && (
        <Card>
          <SectionTitle>基本面指標</SectionTitle>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr style={{ background: "#1E2A4A" }}>
                {["指標", "數值", "vs 同業", "訊號"].map((h, i) => (
                  <th key={i} style={{ padding: "9px 14px", color: "#fff", textAlign: i === 0 ? "left" : "center", fontWeight: 600 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {FUNDAMENTAL.map((r, ri) => (
                <tr key={ri} style={{ background: ri % 2 === 0 ? "#fff" : "#F7F9FC" }}>
                  <td style={{ padding: "9px 14px", fontWeight: 600 }}>{r.metric}</td>
                  <td style={{ padding: "9px 14px", textAlign: "center", fontWeight: 700, color: "#2563A8" }}>{r.value}</td>
                  <td style={{ padding: "9px 14px", textAlign: "center", color: "#5A6070" }}>{r.vsSector}</td>
                  <td style={{ padding: "9px 14px", textAlign: "center" }}>
                    <SignalBadge signal={r.signal} sentiment={r.signal === "正面" || r.signal === "低估" ? "bull" : r.signal === "中性" ? "neutral" : "neutral"} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}

      {/* 技術面 */}
      {sub === 1 && (
        <Card>
          <SectionTitle accent="#D4770A">技術面指標</SectionTitle>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr style={{ background: "#1E2A4A" }}>
                {["指標", "數值", "訊號"].map((h, i) => (
                  <th key={i} style={{ padding: "9px 14px", color: "#fff", textAlign: i === 0 ? "left" : "center", fontWeight: 600 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {TECHNICAL.map((r, ri) => (
                <tr key={ri} style={{ background: ri % 2 === 0 ? "#fff" : "#F7F9FC" }}>
                  <td style={{ padding: "9px 14px", fontWeight: 600 }}>{r.indicator}</td>
                  <td style={{ padding: "9px 14px", textAlign: "center", fontWeight: 700 }}>{r.value}</td>
                  <td style={{ padding: "9px 14px", textAlign: "center" }}>
                    <SignalBadge signal={r.signal} sentiment={r.sentiment} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}

      {/* 催化劑 */}
      {sub === 2 && (
        <Card>
          <SectionTitle accent="#1A7A5E">催化劑追蹤</SectionTitle>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {CATALYSTS.map((c, i) => (
              <div key={i} style={{
                padding: "14px 16px", borderRadius: 10,
                border: "1px solid #E2E8F0", background: "#F7F9FC",
              }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 6, marginBottom: 6 }}>
                  <span style={{ fontWeight: 700, fontSize: 14, color: "#1A1A2E" }}>{c.event}</span>
                  <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
                    <span style={{ fontSize: 11, color: "#94a3b8" }}>{c.date}</span>
                    <ImpactBadge impact={c.impact} />
                  </div>
                </div>
                <div style={{ fontSize: 12, color: "#5A6070" }}>{c.detail}</div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* 風險 */}
      {sub === 3 && (
        <Card>
          <SectionTitle accent="#C0392B">風險矩陣</SectionTitle>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr style={{ background: "#1E2A4A" }}>
                {["風險", "嚴重度", "對策"].map((h, i) => (
                  <th key={i} style={{ padding: "9px 14px", color: "#fff", textAlign: i === 0 ? "left" : "center", fontWeight: 600 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {RISKS.map((r, ri) => (
                <tr key={ri} style={{ background: ri % 2 === 0 ? "#fff" : "#F7F9FC" }}>
                  <td style={{ padding: "9px 14px", fontWeight: 600 }}>{r.risk}</td>
                  <td style={{ padding: "9px 14px", textAlign: "center" }}><SeverityBadge severity={r.severity} /></td>
                  <td style={{ padding: "9px 14px", color: "#5A6070", fontSize: 12 }}>{r.mitigation}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>
      )}

      {/* 分析師 */}
      {sub === 4 && (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <Card>
            <SectionTitle>分析師共識</SectionTitle>
            <div style={{ display: "flex", gap: 12, flexWrap: "wrap", marginBottom: 16 }}>
              {[
                { label: "買入", val: ac.buy,  color: "#1A7A5E", pct: Math.round(ac.buy/total*100) },
                { label: "持有", val: ac.hold, color: "#D4770A", pct: Math.round(ac.hold/total*100) },
                { label: "賣出", val: ac.sell, color: "#C0392B", pct: Math.round(ac.sell/total*100) },
              ].map((item) => (
                <div key={item.label} style={{
                  flex: 1, minWidth: 80, background: item.color + "10",
                  border: `1.5px solid ${item.color}30`, borderRadius: 10,
                  padding: "14px", textAlign: "center",
                }}>
                  <div style={{ fontSize: 11, color: "#5A6070", fontWeight: 600 }}>{item.label}</div>
                  <div style={{ fontSize: 28, fontWeight: 900, color: item.color }}>{item.val}</div>
                  <div style={{ fontSize: 12, color: item.color, fontWeight: 600 }}>{item.pct}%</div>
                </div>
              ))}
            </div>

            {/* consensus bar */}
            <div style={{ borderRadius: 8, overflow: "hidden", height: 12, display: "flex", marginBottom: 16 }}>
              <div style={{ flex: ac.buy, background: "#1A7A5E" }} />
              <div style={{ flex: ac.hold, background: "#D4770A" }} />
              <div style={{ flex: ac.sell, background: "#C0392B" }} />
            </div>

            <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
              {[
                { label: "平均目標價", val: ac.avgTarget, color: "#2563A8" },
                { label: "最高目標價", val: ac.highTarget, color: "#1A7A5E" },
                { label: "最低目標價", val: ac.lowTarget, color: "#C0392B" },
              ].map((item) => (
                <div key={item.label} style={{
                  flex: 1, background: item.color + "08",
                  border: `1.5px solid ${item.color}25`,
                  borderRadius: 10, padding: "14px", textAlign: "center",
                }}>
                  <div style={{ fontSize: 11, color: "#5A6070", fontWeight: 600 }}>{item.label}</div>
                  <div style={{ fontSize: 22, fontWeight: 800, color: item.color }}>NT${item.val}</div>
                  <div style={{ fontSize: 12, color: item.val > P ? "#1A7A5E" : "#C0392B", fontWeight: 600 }}>
                    {item.val > P ? "+" : ""}{+((item.val / P - 1) * 100).toFixed(1)}%
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}

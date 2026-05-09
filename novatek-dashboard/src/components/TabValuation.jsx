import { useState } from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine, Cell,
} from "recharts";
import { SCENARIOS, PE_MULTIPLES, META } from "../data/novatek.js";
import { Card, SectionTitle, CustomTooltip, Btn } from "./Primitives.jsx";

const P = META.currentPrice;

function PriceMatrix({ activeScenario, activePE }) {
  return (
    <div style={{ overflowX: "auto" }}>
      <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
        <thead>
          <tr style={{ background: "#1E2A4A" }}>
            <th style={{ padding: "10px 14px", color: "#fff", textAlign: "left", fontWeight: 600 }}>情境 / EPS</th>
            {PE_MULTIPLES.map((pe) => (
              <th key={pe} style={{ padding: "10px 14px", color: "#fff", textAlign: "center", fontWeight: 600 }}>
                PE {pe}x
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {Object.entries(SCENARIOS).map(([key, sc], ri) => (
            <tr key={key} style={{ background: ri % 2 === 0 ? "#fff" : "#F7F9FC" }}>
              <td style={{ padding: "10px 14px", fontWeight: 700 }}>
                <span style={{ color: sc.color }}>● </span>
                {sc.label} ({sc.eps}元)
              </td>
              {PE_MULTIPLES.map((pe) => {
                const price = Math.round(sc.eps * pe);
                const upside = +((price / P - 1) * 100).toFixed(1);
                const isActive = activeScenario === key && activePE === pe;
                const isAbove = price > P;
                return (
                  <td key={pe} style={{
                    padding: "10px 14px", textAlign: "center",
                    background: isActive ? sc.color : "transparent",
                    borderRadius: isActive ? 6 : 0,
                  }}>
                    <div style={{ fontWeight: 800, fontSize: 14, color: isActive ? "#fff" : (isAbove ? "#1A7A5E" : "#C0392B") }}>
                      {price}
                    </div>
                    <div style={{ fontSize: 10, color: isActive ? "rgba(255,255,255,0.8)" : "#94a3b8" }}>
                      {upside > 0 ? "+" : ""}{upside}%
                    </div>
                  </td>
                );
              })}
            </tr>
          ))}
          <tr style={{ background: "#FFF7ED", borderTop: "2px solid #D4770A" }}>
            <td style={{ padding: "8px 14px", fontWeight: 700, color: "#D4770A", fontSize: 12 }}>
              ★ 現價 NT${P}（參考線）
            </td>
            {PE_MULTIPLES.map((pe) => (
              <td key={pe} style={{ padding: "8px 14px", textAlign: "center", fontSize: 11, color: "#D4770A", fontWeight: 600 }}>
                EPS={(P / pe).toFixed(1)}
              </td>
            ))}
          </tr>
        </tbody>
      </table>
    </div>
  );
}

export default function TabValuation() {
  const [activeScenario, setActiveScenario] = useState("base");
  const [activePE, setActivePE] = useState(20);

  const sc = SCENARIOS[activeScenario];
  const targetPrice = Math.round(sc.eps * activePE);
  const upside = +((targetPrice / P - 1) * 100).toFixed(1);

  const barData = Object.entries(SCENARIOS).map(([k, s]) => ({
    name: s.label,
    upside: +((s.eps * 20 / P - 1) * 100).toFixed(0),
    price: Math.round(s.eps * 20),
    color: s.color,
  }));

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

      {/* Scenario + PE selectors */}
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
        <Card style={{ flex: 1, minWidth: 260 }}>
          <SectionTitle>選擇情境</SectionTitle>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {Object.entries(SCENARIOS).map(([key, s]) => (
              <button key={key} onClick={() => setActiveScenario(key)} style={{
                display: "flex", justifyContent: "space-between", alignItems: "center",
                padding: "10px 14px", borderRadius: 8, cursor: "pointer",
                border: `1.5px solid ${activeScenario === key ? s.color : "#E2E8F0"}`,
                background: activeScenario === key ? s.bg : "#fff",
                transition: "all 0.15s",
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <div style={{ width: 10, height: 10, borderRadius: "50%", background: s.color }} />
                  <span style={{ fontWeight: 600, color: "#1A1A2E", fontSize: 13 }}>{s.label}</span>
                </div>
                <span style={{ fontWeight: 800, color: s.color, fontSize: 15 }}>EPS {s.eps}元</span>
              </button>
            ))}
          </div>
        </Card>

        <Card style={{ flex: 1, minWidth: 260 }}>
          <SectionTitle>選擇 PE 倍數</SectionTitle>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
            {PE_MULTIPLES.map((pe) => (
              <Btn key={pe} active={activePE === pe} color={sc.color} onClick={() => setActivePE(pe)}>
                {pe}x
              </Btn>
            ))}
          </div>
          <div style={{
            marginTop: 20, padding: 16, background: sc.bg,
            borderRadius: 10, border: `1.5px solid ${sc.color}30`,
          }}>
            <div style={{ fontSize: 12, color: "#5A6070", marginBottom: 4 }}>目標股價</div>
            <div style={{ fontSize: 36, fontWeight: 900, color: sc.color, letterSpacing: "-0.03em" }}>
              NT${targetPrice}
            </div>
            <div style={{ fontSize: 13, fontWeight: 700, marginTop: 4, color: upside >= 0 ? "#1A7A5E" : "#C0392B" }}>
              {upside >= 0 ? "▲" : "▼"} {Math.abs(upside)}% vs 現價 NT${P}
            </div>
            <div style={{ fontSize: 12, color: "#5A6070", marginTop: 2 }}>
              {sc.label} × {activePE}x PE × EPS {sc.eps}元
            </div>
          </div>
        </Card>
      </div>

      {/* Full price matrix */}
      <Card>
        <SectionTitle>完整股價矩陣（所有情境 × PE）</SectionTitle>
        <PriceMatrix activeScenario={activeScenario} activePE={activePE} />
      </Card>

      {/* Upside bar chart */}
      <Card>
        <SectionTitle accent="#1A7A5E">各情境上行空間（基準 PE 20x）</SectionTitle>
        <ResponsiveContainer width="100%" height={180}>
          <BarChart data={barData} barSize={48}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
            <XAxis dataKey="name" tick={{ fontSize: 12, fontWeight: 600 }} />
            <YAxis tickFormatter={(v) => `${v}%`} tick={{ fontSize: 11 }} domain={[0, 80]} />
            <Tooltip content={<CustomTooltip />} />
            <ReferenceLine y={0} stroke="#CBD5E1" />
            <Bar dataKey="upside" name="上行空間%" radius={[6, 6, 0, 0]}>
              {barData.map((d, i) => <Cell key={i} fill={d.color} />)}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 12 }}>
          {Object.entries(SCENARIOS).map(([k, s]) => {
            const tp = Math.round(s.eps * 20);
            const up = +((tp / P - 1) * 100).toFixed(0);
            return (
              <div key={k} style={{
                flex: 1, minWidth: 100, background: s.bg,
                border: `1px solid ${s.color}30`, borderRadius: 8,
                padding: "8px 12px", textAlign: "center",
              }}>
                <div style={{ fontSize: 11, color: s.color, fontWeight: 700 }}>{s.label}</div>
                <div style={{ fontSize: 18, fontWeight: 800, color: s.color }}>NT${tp}</div>
                <div style={{ fontSize: 11, color: "#1A7A5E", fontWeight: 600 }}>+{up}%</div>
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
}

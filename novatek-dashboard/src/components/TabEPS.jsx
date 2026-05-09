import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine, BarChart, Bar,
} from "recharts";
import { SCENARIOS, EPS_HISTORY, INCOME_SCENARIOS, QUARTERLY_DATA } from "../data/novatek.js";
import { Card, SectionTitle, CustomTooltip } from "./Primitives.jsx";

const chartData = [
  ...EPS_HISTORY,
  { year: "2026E", bear: 28.1, base: 32.5, bull: 37.8, aitam: 33.9 },
];

export default function TabEPS() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

      {/* EPS line chart */}
      <Card>
        <SectionTitle>EPS 歷史 × 2026 情境預估</SectionTitle>
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis dataKey="year" tick={{ fontSize: 12 }} />
            <YAxis tickFormatter={(v) => `${v}元`} tick={{ fontSize: 11 }} domain={[0, 70]} />
            <Tooltip formatter={(v, n) => [`${v}元`, n]} />
            <Line dataKey="eps" name="實績EPS" stroke="#1A1A2E" strokeWidth={2.5} dot={{ r: 5 }} connectNulls />
            <Line dataKey="base" name="基準情境" stroke="#2563A8" strokeWidth={2} strokeDasharray="6 3" dot={{ r: 5 }} connectNulls />
            <Line dataKey="bull" name="樂觀情境" stroke="#1A7A5E" strokeWidth={2} strokeDasharray="6 3" dot={{ r: 5 }} connectNulls />
            <Line dataKey="bear" name="保守情境" stroke="#94a3b8" strokeWidth={2} strokeDasharray="6 3" dot={{ r: 5 }} connectNulls />
            <Line dataKey="aitam" name="ai-tam" stroke="#D4770A" strokeWidth={1.5} strokeDasharray="4 4" dot={{ r: 4 }} connectNulls />
            <ReferenceLine y={26.87} stroke="#C0392B" strokeDasharray="3 3"
              label={{ value: "2025: 26.87", position: "insideTopRight", fontSize: 10, fill: "#C0392B" }} />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      {/* Scenario cards */}
      <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
        {Object.entries(SCENARIOS).map(([k, s]) => {
          const yoy = +((s.eps / 26.87 - 1) * 100).toFixed(1);
          return (
            <Card key={k} style={{ flex: 1, minWidth: 120, background: s.bg, border: `1.5px solid ${s.color}30` }}>
              <div style={{ fontSize: 11, color: s.color, fontWeight: 700, marginBottom: 4 }}>{s.label}情境</div>
              <div style={{ fontSize: 24, fontWeight: 900, color: s.color }}>{s.eps}元</div>
              <div style={{ fontSize: 11, color: "#5A6070", marginTop: 4 }}>
                vs 2025: {yoy >= 0 ? "+" : ""}{yoy}%
              </div>
              <div style={{ marginTop: 8, fontSize: 11, color: "#5A6070" }}>
                目標股 (20x): <b style={{ color: s.color }}>NT${Math.round(s.eps * 20)}</b>
              </div>
            </Card>
          );
        })}
      </div>

      {/* Income statement scenarios table */}
      <Card>
        <SectionTitle>損益槓桿效應</SectionTitle>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
            <thead>
              <tr style={{ background: "#1E2A4A" }}>
                {["項目", "2025實績", "保守", "基準", "樂觀"].map((h, i) => (
                  <th key={i} style={{ padding: "9px 12px", color: "#fff", textAlign: i === 0 ? "left" : "center", fontWeight: 600 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {INCOME_SCENARIOS.map((row, ri) => (
                <tr key={ri} style={{ background: ri % 2 === 0 ? "#fff" : "#F7F9FC" }}>
                  {Object.values(row).map((cell, ci) => (
                    <td key={ci} style={{
                      padding: "9px 12px",
                      textAlign: ci === 0 ? "left" : "center",
                      fontWeight: ri === 5 ? 800 : (ci === 0 ? 600 : 400),
                      color: ri === 5
                        ? (ci === 2 ? "#94a3b8" : ci === 3 ? "#2563A8" : ci === 4 ? "#1A7A5E" : "#1A1A2E")
                        : "#1A1A2E",
                      fontSize: ri === 5 ? 13 : 12,
                    }}>{cell}</td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>

      {/* Quarterly trend */}
      <Card>
        <SectionTitle accent="#7C3AED">季度財務趨勢</SectionTitle>
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={QUARTERLY_DATA} barCategoryGap="30%">
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
            <XAxis dataKey="quarter" tick={{ fontSize: 10 }} interval={0} angle={-25} textAnchor="end" height={42} />
            <YAxis tick={{ fontSize: 11 }} />
            <Tooltip content={<CustomTooltip />} />
            <Bar dataKey="eps" name="EPS (元)" fill="#2563A8" radius={[4, 4, 0, 0]} />
            <Bar dataKey="grossMargin" name="毛利率%" fill="#1A7A5E" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
        <div style={{ overflowX: "auto", marginTop: 12 }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
            <thead>
              <tr style={{ background: "#1E2A4A" }}>
                {["季度", "營收(億)", "毛利率%", "營益率%", "EPS(元)"].map((h, i) => (
                  <th key={i} style={{ padding: "8px 12px", color: "#fff", textAlign: i === 0 ? "left" : "center", fontWeight: 600 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {QUARTERLY_DATA.map((r, ri) => (
                <tr key={ri} style={{ background: ri % 2 === 0 ? "#fff" : "#F7F9FC" }}>
                  <td style={{ padding: "8px 12px", fontWeight: 700 }}>{r.quarter}</td>
                  <td style={{ padding: "8px 12px", textAlign: "center" }}>{r.revenue}</td>
                  <td style={{ padding: "8px 12px", textAlign: "center" }}>{r.grossMargin}%</td>
                  <td style={{ padding: "8px 12px", textAlign: "center" }}>{r.opMargin}%</td>
                  <td style={{ padding: "8px 12px", textAlign: "center", fontWeight: 800, color: "#2563A8" }}>{r.eps}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

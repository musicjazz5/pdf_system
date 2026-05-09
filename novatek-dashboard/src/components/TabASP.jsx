import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import { ASP_DATA, ASP_SENSITIVITY } from "../data/novatek.js";
import { Card, SectionTitle, CustomTooltip } from "./Primitives.jsx";

const DRIVERS = [
  { label: "產品組合升級（高階TV SoC/TCON）", val: "+5~6元",     color: "#2563A8" },
  { label: "OLED TDDI 新品滲透",             val: "+3~4元",     color: "#1A7A5E" },
  { label: "AI Edge SoC 初期出貨",           val: "+2~3元",     color: "#7C3AED" },
  { label: "折疊機 OLED TDDI（H2）",         val: "+NT$200+/片", color: "#D4770A" },
];

export default function TabASP() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

      <Card>
        <SectionTitle accent="#7C3AED">SoC ASP 提升軌跡</SectionTitle>
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={ASP_DATA}>
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" />
            <XAxis dataKey="period" tick={{ fontSize: 11 }} />
            <YAxis yAxisId="asp" tickFormatter={(v) => `NT$${v}`} tick={{ fontSize: 11 }} domain={[110, 165]} />
            <YAxis yAxisId="pct" orientation="right" tickFormatter={(v) => `${v}%`} tick={{ fontSize: 11 }} domain={[30, 65]} />
            <Tooltip content={<CustomTooltip />} />
            <Line yAxisId="asp" dataKey="asp" name="SoC ASP" stroke="#7C3AED" strokeWidth={2.5} dot={{ r: 6 }} />
            <Line yAxisId="pct" dataKey="socPct" name="SoC佔比%" stroke="#D4770A" strokeWidth={2} strokeDasharray="5 3" dot={{ r: 5 }} />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      <div style={{ display: "flex", gap: 12, flexWrap: "wrap" }}>
        <Card style={{ flex: 1, minWidth: 260 }}>
          <SectionTitle accent="#7C3AED">ASP 提升 EPS 敏感度</SectionTitle>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 12 }}>
            <thead>
              <tr style={{ background: "#1E2A4A" }}>
                {["SoC ASP提升", "毛利率額外+", "EPS額外+", "目標股(20x)"].map((h) => (
                  <th key={h} style={{ padding: "8px 10px", color: "#fff", textAlign: "center", fontWeight: 600 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {ASP_SENSITIVITY.map((row, ri) => (
                <tr key={ri} style={{ background: ri % 2 === 0 ? "#fff" : "#F7F9FC" }}>
                  <td style={{ padding: "8px 10px", textAlign: "center", fontWeight: 600 }}>{row.label}</td>
                  <td style={{ padding: "8px 10px", textAlign: "center" }}>{row.gmDelta}</td>
                  <td style={{ padding: "8px 10px", textAlign: "center" }}>{row.epsDelta}</td>
                  <td style={{ padding: "8px 10px", textAlign: "center", fontWeight: 800, color: "#1A7A5E" }}>
                    NT${row.target20x}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </Card>

        <Card style={{ flex: 1, minWidth: 260 }}>
          <SectionTitle>ASP 驅動因子拆解</SectionTitle>
          {DRIVERS.map((d, i) => (
            <div key={i} style={{
              display: "flex", justifyContent: "space-between", alignItems: "center",
              padding: "8px 0", borderBottom: i < DRIVERS.length - 1 ? "1px solid #E2E8F0" : "none",
            }}>
              <span style={{ fontSize: 12, color: "#5A6070", flex: 1 }}>{d.label}</span>
              <span style={{ fontSize: 13, fontWeight: 700, color: d.color, marginLeft: 8 }}>{d.val}</span>
            </div>
          ))}
          <div style={{ marginTop: 12, padding: 10, background: "#EBF3FF", borderRadius: 8 }}>
            <div style={{ fontSize: 11, color: "#2563A8", fontWeight: 600 }}>2026 Q1 反推</div>
            <div style={{ fontSize: 16, fontWeight: 800, color: "#2563A8" }}>NT$136/顆（+9.7%）</div>
            <div style={{ fontSize: 11, color: "#5A6070" }}>vs 2025均值 NT$124</div>
          </div>
        </Card>
      </div>

      {/* ASP data table */}
      <Card>
        <SectionTitle>SoC ASP 完整數據</SectionTitle>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr style={{ background: "#1E2A4A" }}>
              {["期間", "SoC ASP (NT$)", "SoC 營收 (億)", "SoC 佔比 (%)"].map((h) => (
                <th key={h} style={{ padding: "9px 14px", color: "#fff", textAlign: "center", fontWeight: 600 }}>{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ASP_DATA.map((r, ri) => (
              <tr key={ri} style={{ background: ri % 2 === 0 ? "#fff" : "#F7F9FC" }}>
                <td style={{ padding: "9px 14px", textAlign: "center", fontWeight: 700 }}>{r.period}</td>
                <td style={{ padding: "9px 14px", textAlign: "center", color: "#7C3AED", fontWeight: 700 }}>{r.asp}</td>
                <td style={{ padding: "9px 14px", textAlign: "center" }}>{r.socRev}</td>
                <td style={{ padding: "9px 14px", textAlign: "center", color: "#1A7A5E", fontWeight: 600 }}>{r.socPct}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>
    </div>
  );
}

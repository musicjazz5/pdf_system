import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, ReferenceLine, Cell,
} from "recharts";
import { MONTHLY_REV, ANNUAL_PATH } from "../data/novatek.js";
import { Card, SectionTitle, CustomTooltip } from "./Primitives.jsx";

function barColor(entry) {
  if (entry.rev2026 === null) return "#E2E8F0";
  if (entry.yoy > 0) return "#1A7A5E";
  if (entry.yoy > -15) return "#2563A8";
  return "#94a3b8";
}

export default function TabRevenue() {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

      <Card>
        <SectionTitle>2026 vs 2025 月營收對比（億元）</SectionTitle>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={MONTHLY_REV} barCategoryGap="25%">
            <CartesianGrid strokeDasharray="3 3" stroke="#E2E8F0" vertical={false} />
            <XAxis dataKey="month" tick={{ fontSize: 11 }} />
            <YAxis tick={{ fontSize: 11 }} domain={[0, 110]} />
            <Tooltip content={<CustomTooltip unit="" />} />
            <ReferenceLine y={91.7} stroke="#D4770A" strokeDasharray="4 3"
              label={{ value: "1,100億目標月均", position: "insideTopRight", fontSize: 9, fill: "#D4770A" }} />
            <Bar dataKey="rev2026" name="2026" radius={[4, 4, 0, 0]}>
              {MONTHLY_REV.map((e, i) => <Cell key={i} fill={barColor(e)} />)}
            </Bar>
            <Bar dataKey="rev2025" name="2025" fill="#E2E8F0" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
        <div style={{ display: "flex", gap: 8, marginTop: 8, flexWrap: "wrap" }}>
          {[
            { color: "#1A7A5E", label: "2026（年增）" },
            { color: "#2563A8", label: "2026（年減<15%）" },
            { color: "#94a3b8", label: "2026（年減>15%）" },
            { color: "#E2E8F0", label: "2026（未公布）" },
          ].map((item) => (
            <div key={item.label} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 11, color: "#5A6070" }}>
              <div style={{ width: 10, height: 10, borderRadius: 2, background: item.color }} />
              {item.label}
            </div>
          ))}
        </div>
      </Card>

      {/* Q2 guidance */}
      <Card>
        <SectionTitle accent="#D4770A">Q2 指引 vs 達標分析</SectionTitle>
        <div style={{ display: "flex", gap: 12, marginBottom: 16, flexWrap: "wrap" }}>
          {[
            { label: "Q2 指引低標", val: "275億", color: "#94a3b8", sub: "季增+19%" },
            { label: "Q2 指引中位", val: "280億", color: "#2563A8", sub: "季增+21%" },
            { label: "Q2 指引高標", val: "285億", color: "#1A7A5E", sub: "季增+23%" },
          ].map((item) => (
            <div key={item.label} style={{
              flex: 1, background: item.color + "10",
              border: `1.5px solid ${item.color}30`,
              borderRadius: 8, padding: 12, textAlign: "center",
            }}>
              <div style={{ fontSize: 10, color: "#5A6070", fontWeight: 600 }}>{item.label}</div>
              <div style={{ fontSize: 22, fontWeight: 900, color: item.color }}>{item.val}</div>
              <div style={{ fontSize: 11, color: item.color }}>{item.sub}</div>
            </div>
          ))}
        </div>

        <div style={{ background: "#FFF7ED", borderRadius: 8, padding: "12px 16px", border: "1px solid #D4770A30" }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: "#D4770A", marginBottom: 8 }}>
            全年營收達標路徑（月均需求）
          </div>
          {ANNUAL_PATH.map((row, i) => (
            <div key={i} style={{
              display: "flex", justifyContent: "space-between",
              padding: "7px 10px",
              background: row.highlight ? "#D4770A18" : "transparent",
              borderRadius: 6, marginBottom: 2,
              flexWrap: "wrap", gap: 4,
            }}>
              <span style={{ fontSize: 12, fontWeight: row.highlight ? 700 : 400, color: row.highlight ? "#D4770A" : "#5A6070" }}>
                {row.q}
              </span>
              <span style={{ fontSize: 12, fontWeight: 600, color: "#1A1A2E" }}>{row.rev}億</span>
              <span style={{ fontSize: 12, color: "#5A6070" }}>月均 {row.avg}億</span>
              <span style={{ fontSize: 11, color: row.highlight ? "#D4770A" : "#94a3b8" }}>{row.note}</span>
            </div>
          ))}
        </div>
      </Card>

      {/* Monthly data table */}
      <Card>
        <SectionTitle>月營收明細</SectionTitle>
        <div style={{ overflowX: "auto" }}>
          <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
            <thead>
              <tr style={{ background: "#1E2A4A" }}>
                {["月份", "2026 (億)", "2025 (億)", "年增率"].map((h) => (
                  <th key={h} style={{ padding: "9px 14px", color: "#fff", textAlign: "center", fontWeight: 600 }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {MONTHLY_REV.map((r, ri) => (
                <tr key={ri} style={{ background: ri % 2 === 0 ? "#fff" : "#F7F9FC" }}>
                  <td style={{ padding: "9px 14px", textAlign: "center", fontWeight: 700 }}>{r.month}</td>
                  <td style={{ padding: "9px 14px", textAlign: "center", color: barColor(r), fontWeight: r.rev2026 ? 700 : 400 }}>
                    {r.rev2026 ?? "—"}
                  </td>
                  <td style={{ padding: "9px 14px", textAlign: "center" }}>{r.rev2025}</td>
                  <td style={{ padding: "9px 14px", textAlign: "center", color: r.yoy > 0 ? "#1A7A5E" : (r.yoy === null ? "#94a3b8" : "#C0392B"), fontWeight: 600 }}>
                    {r.yoy !== null ? `${r.yoy > 0 ? "+" : ""}${r.yoy}%` : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}

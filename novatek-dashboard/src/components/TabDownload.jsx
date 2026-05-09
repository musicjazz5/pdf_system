import { useState } from "react";
import { downloadExcel, downloadCSVZip, downloadSQLite } from "../utils/download.js";
import { Card, SectionTitle, DownloadBtn } from "./Primitives.jsx";

const TABLES = [
  { name: "price_matrix",        desc: "股價矩陣（情境 × PE）" },
  { name: "eps_history",         desc: "EPS 歷史 + 2026 情境預估" },
  { name: "soc_asp",             desc: "SoC ASP 提升軌跡" },
  { name: "monthly_revenue",     desc: "2025/2026 月營收對比" },
  { name: "quarterly_financials",desc: "季度財務（2024Q1–2026Q1）" },
  { name: "income_scenarios",    desc: "損益情境（保守/基準/樂觀）" },
  { name: "asp_sensitivity",     desc: "ASP 提升 EPS 敏感度" },
  { name: "fundamental",         desc: "基本面指標" },
  { name: "technical",           desc: "技術面指標" },
  { name: "catalysts",           desc: "催化劑追蹤" },
  { name: "risk_factors",        desc: "風險因子矩陣" },
  { name: "metadata",            desc: "報告元資料" },
];

export default function TabDownload() {
  const [loading, setLoading] = useState({ excel: false, csv: false, db: false });

  const run = (key, fn) => async () => {
    setLoading((p) => ({ ...p, [key]: true }));
    try { await fn(); } finally {
      setLoading((p) => ({ ...p, [key]: false }));
    }
  };

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

      <Card>
        <SectionTitle>下載分析資料</SectionTitle>
        <p style={{ fontSize: 13, color: "#5A6070", marginTop: 0, marginBottom: 20 }}>
          所有分析數據可一鍵匯出為以下格式，包含股價矩陣、EPS軌跡、SoC ASP、月營收、
          季度財務、損益情境、基本面、技術面、催化劑與風險因子共 12 張資料表。
        </p>

        <div style={{ display: "flex", gap: 16, flexWrap: "wrap" }}>

          {/* Excel */}
          <div style={{
            flex: 1, minWidth: 220, background: "#EBF3FF",
            border: "1.5px solid #2563A830", borderRadius: 12, padding: "20px",
          }}>
            <div style={{ fontSize: 28, marginBottom: 8 }}>📊</div>
            <div style={{ fontWeight: 800, color: "#2563A8", fontSize: 16, marginBottom: 6 }}>Excel (.xlsx)</div>
            <div style={{ fontSize: 12, color: "#5A6070", marginBottom: 16, lineHeight: 1.6 }}>
              多工作表格式，含全部分析資料，支援 Excel / Numbers / WPS 開啟。
              共 12 個工作表。
            </div>
            <DownloadBtn color="#2563A8" loading={loading.excel} onClick={run("excel", downloadExcel)}>
              ⬇ 下載 Excel
            </DownloadBtn>
          </div>

          {/* CSV ZIP */}
          <div style={{
            flex: 1, minWidth: 220, background: "#E6F5EC",
            border: "1.5px solid #1A7A5E30", borderRadius: 12, padding: "20px",
          }}>
            <div style={{ fontSize: 28, marginBottom: 8 }}>📁</div>
            <div style={{ fontWeight: 800, color: "#1A7A5E", fontSize: 16, marginBottom: 6 }}>CSV 壓縮包 (.zip)</div>
            <div style={{ fontSize: 12, color: "#5A6070", marginBottom: 16, lineHeight: 1.6 }}>
              每個資料表獨立 CSV 檔，含 metadata.json。
              UTF-8-BOM 編碼，Excel 直接開啟不亂碼。
            </div>
            <DownloadBtn color="#1A7A5E" loading={loading.csv} onClick={run("csv", downloadCSVZip)}>
              ⬇ 下載 CSV ZIP
            </DownloadBtn>
          </div>

          {/* SQLite */}
          <div style={{
            flex: 1, minWidth: 220, background: "#FFF7ED",
            border: "1.5px solid #D4770A30", borderRadius: 12, padding: "20px",
          }}>
            <div style={{ fontSize: 28, marginBottom: 8 }}>🗄️</div>
            <div style={{ fontWeight: 800, color: "#D4770A", fontSize: 16, marginBottom: 6 }}>SQLite 資料庫 (.db)</div>
            <div style={{ fontSize: 12, color: "#5A6070", marginBottom: 16, lineHeight: 1.6 }}>
              結構化資料庫，適合 Python / DBeaver / TablePlus 二次查詢。
              初次下載需載入 WebAssembly，稍候片刻。
            </div>
            <DownloadBtn color="#D4770A" loading={loading.db} onClick={run("db", downloadSQLite)}>
              ⬇ 下載 SQLite DB
            </DownloadBtn>
          </div>
        </div>
      </Card>

      {/* Table list */}
      <Card>
        <SectionTitle accent="#1A1A2E">資料表清單</SectionTitle>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 13 }}>
          <thead>
            <tr style={{ background: "#1E2A4A" }}>
              <th style={{ padding: "9px 14px", color: "#fff", textAlign: "left", fontWeight: 600 }}>#</th>
              <th style={{ padding: "9px 14px", color: "#fff", textAlign: "left", fontWeight: 600 }}>資料表</th>
              <th style={{ padding: "9px 14px", color: "#fff", textAlign: "left", fontWeight: 600 }}>說明</th>
            </tr>
          </thead>
          <tbody>
            {TABLES.map((t, i) => (
              <tr key={i} style={{ background: i % 2 === 0 ? "#fff" : "#F7F9FC" }}>
                <td style={{ padding: "9px 14px", color: "#94a3b8" }}>{i + 1}</td>
                <td style={{ padding: "9px 14px", fontFamily: "monospace", color: "#2563A8", fontWeight: 600 }}>{t.name}</td>
                <td style={{ padding: "9px 14px", color: "#5A6070" }}>{t.desc}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </Card>

      {/* SQL quick-start */}
      <Card>
        <SectionTitle accent="#7C3AED">Python 快速查詢範例</SectionTitle>
        <pre style={{
          background: "#1E2A4A", color: "#a5f3fc", borderRadius: 8,
          padding: "16px 20px", fontSize: 12, overflowX: "auto", margin: 0,
        }}>{`import sqlite3, pandas as pd

con = sqlite3.connect("聯詠3034_估值分析_2026-05-07.db")

# 所有基準情境 × PE 20x 的目標股價
df = pd.read_sql("""
  SELECT scenario_label, pe, target_price, upside_pct
  FROM   price_matrix
  WHERE  scenario_key = 'base'
  ORDER  BY pe
""", con)
print(df)

# EPS 歷史趨勢
eps = pd.read_sql("SELECT * FROM eps_history ORDER BY year", con)
print(eps)
con.close()`}</pre>
      </Card>
    </div>
  );
}

import * as XLSX from "xlsx";
import {
  META, SCENARIOS, PE_MULTIPLES, EPS_HISTORY, EPS_FORECASTS,
  ASP_DATA, MONTHLY_REV, QUARTERLY_DATA, INCOME_SCENARIOS,
  FUNDAMENTAL, TECHNICAL, CATALYSTS, RISKS, ASP_SENSITIVITY,
} from "../data/novatek.js";

// ── helpers ─────────────────────────────────────────────────────

function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

function priceMatrixRows() {
  const rows = [];
  Object.entries(SCENARIOS).forEach(([key, sc]) => {
    PE_MULTIPLES.forEach((pe) => {
      const price = Math.round(sc.eps * pe);
      const upside = +((price / META.currentPrice - 1) * 100).toFixed(1);
      rows.push({ 情境: sc.label, EPS: sc.eps, PE倍數: pe, 目標股價: price, 上行空間: upside });
    });
  });
  return rows;
}

function epsRows() {
  const rows = EPS_HISTORY.map((r) => ({ 年度: r.year, EPS: r.eps, 類型: "actual" }));
  Object.entries(EPS_FORECASTS).forEach(([label, val]) =>
    rows.push({ 年度: label, EPS: val, 類型: "forecast" })
  );
  return rows;
}

// ── Excel ────────────────────────────────────────────────────────

export function downloadExcel() {
  const wb = XLSX.utils.book_new();

  const addSheet = (data, name) => {
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(data), name);
  };

  addSheet(priceMatrixRows(), "股價矩陣");
  addSheet(epsRows(), "EPS軌跡");
  addSheet(ASP_DATA.map((r) => ({ 期間: r.period, "SoC ASP(NT$)": r.asp, "SoC營收(億)": r.socRev, "SoC佔比(%)": r.socPct })), "SoC ASP");
  addSheet(MONTHLY_REV.map((r) => ({ 月份: r.month, "2026營收(億)": r.rev2026, "2025營收(億)": r.rev2025, "年增率(%)": r.yoy })), "月營收");
  addSheet(QUARTERLY_DATA.map((r) => ({ 季度: r.quarter, "營收(億)": r.revenue, "毛利率(%)": r.grossMargin, "營益率(%)": r.opMargin, "EPS(元)": r.eps })), "季度財務");
  addSheet(INCOME_SCENARIOS, "損益情境");
  addSheet(ASP_SENSITIVITY.map((r) => ({ "ASP提升": r.label, "毛利率+": r.gmDelta, "EPS+": r.epsDelta, "目標股(20x)": `NT$${r.target20x}` })), "ASP敏感度");
  addSheet(FUNDAMENTAL.map((r) => ({ 指標: r.metric, 數值: r.value, "vs同業": r.vsSector, 訊號: r.signal })), "基本面");
  addSheet(TECHNICAL.map((r) => ({ 指標: r.indicator, 數值: r.value, 訊號: r.signal })), "技術面");
  addSheet(CATALYSTS.map((r) => ({ 催化劑: r.event, 時間: r.date, 影響度: r.impact, 說明: r.detail })), "催化劑");
  addSheet(RISKS.map((r) => ({ 風險: r.risk, 嚴重度: r.severity, 對策: r.mitigation })), "風險因子");
  addSheet([{ 代號: META.symbol, 名稱: META.name, 現價: META.currentPrice, 報告日期: META.reportDate }], "元資料");

  const out = XLSX.write(wb, { bookType: "xlsx", type: "array" });
  triggerDownload(
    new Blob([out], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" }),
    `聯詠3034_估值分析_${META.reportDate}.xlsx`
  );
}

// ── CSV ZIP ──────────────────────────────────────────────────────

function toCSV(data) {
  if (!data.length) return "";
  const headers = Object.keys(data[0]);
  const lines = [headers.join(",")];
  data.forEach((row) => {
    lines.push(headers.map((h) => {
      const v = row[h] ?? "";
      return typeof v === "string" && v.includes(",") ? `"${v}"` : v;
    }).join(","));
  });
  return "﻿" + lines.join("\n"); // UTF-8 BOM for Excel compat
}

export async function downloadCSVZip() {
  // Dynamic import keeps bundle lean – only loaded on demand
  const { default: JSZip } = await import("jszip");
  const zip = new JSZip();

  const add = (name, data) => zip.file(name, toCSV(data));

  add("股價矩陣.csv", priceMatrixRows());
  add("EPS軌跡.csv", epsRows());
  add("SoC_ASP.csv", ASP_DATA);
  add("月營收.csv", MONTHLY_REV);
  add("季度財務.csv", QUARTERLY_DATA);
  add("損益情境.csv", INCOME_SCENARIOS);
  add("ASP敏感度.csv", ASP_SENSITIVITY);
  add("基本面.csv", FUNDAMENTAL);
  add("技術面.csv", TECHNICAL);
  add("催化劑.csv", CATALYSTS);
  add("風險因子.csv", RISKS);
  zip.file("metadata.json", JSON.stringify({ ...META, generatedAt: new Date().toISOString() }, null, 2));

  const blob = await zip.generateAsync({ type: "blob", compression: "DEFLATE" });
  triggerDownload(blob, `聯詠3034_估值分析_${META.reportDate}.zip`);
}

// ── SQLite ───────────────────────────────────────────────────────

export async function downloadSQLite() {
  const initSqlJs = (await import("sql.js")).default;
  const SQL = await initSqlJs({
    locateFile: (f) => `https://cdnjs.cloudflare.com/ajax/libs/sql.js/1.12.0/${f}`,
  });
  const db = new SQL.Database();

  const createAndInsert = (table, rows) => {
    if (!rows.length) return;
    const cols = Object.keys(rows[0]);
    db.run(`CREATE TABLE IF NOT EXISTS ${table} (${cols.map((c) => `"${c}" TEXT`).join(", ")})`);
    const stmt = db.prepare(`INSERT INTO ${table} VALUES (${cols.map(() => "?").join(",")})`);
    rows.forEach((row) => stmt.run(cols.map((c) => row[c] ?? null)));
    stmt.free();
  };

  createAndInsert("price_matrix", priceMatrixRows());
  createAndInsert("eps_history", epsRows());
  createAndInsert("soc_asp", ASP_DATA);
  createAndInsert("monthly_revenue", MONTHLY_REV);
  createAndInsert("quarterly_financials", QUARTERLY_DATA);
  createAndInsert("income_scenarios", INCOME_SCENARIOS);
  createAndInsert("asp_sensitivity", ASP_SENSITIVITY);
  createAndInsert("fundamental", FUNDAMENTAL);
  createAndInsert("technical", TECHNICAL);
  createAndInsert("catalysts", CATALYSTS);
  createAndInsert("risk_factors", RISKS);
  createAndInsert("metadata", [{ ...META, generatedAt: new Date().toISOString() }]);

  const buf = db.export();
  db.close();
  triggerDownload(
    new Blob([buf], { type: "application/octet-stream" }),
    `聯詠3034_估值分析_${META.reportDate}.db`
  );
}

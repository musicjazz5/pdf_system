// Shared primitive components

export const Tag = ({ children, color = "#2563A8" }) => (
  <span style={{
    background: color + "18", color,
    border: `1px solid ${color}40`,
    borderRadius: 4, padding: "2px 8px",
    fontSize: 11, fontWeight: 600, letterSpacing: "0.05em",
    whiteSpace: "nowrap",
  }}>{children}</span>
);

export const Card = ({ children, style = {} }) => (
  <div style={{
    background: "#fff", border: "1px solid #E2E8F0",
    borderRadius: 12, padding: "20px 24px",
    boxShadow: "0 1px 3px rgba(0,0,0,0.06)", ...style,
  }}>{children}</div>
);

export const SectionTitle = ({ children, accent = "#2563A8" }) => (
  <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
    <div style={{ width: 4, height: 20, background: accent, borderRadius: 2 }} />
    <span style={{ fontSize: 15, fontWeight: 700, color: "#1A1A2E", letterSpacing: "-0.01em" }}>
      {children}
    </span>
  </div>
);

export const KPI = ({ label, value, sub, color = "#2563A8", badge }) => (
  <div style={{
    background: color + "08", border: `1.5px solid ${color}25`,
    borderRadius: 10, padding: "14px 18px",
    flex: 1, minWidth: 120,
  }}>
    <div style={{ fontSize: 11, color: "#5A6070", letterSpacing: "0.06em", fontWeight: 600, marginBottom: 4 }}>
      {label}
    </div>
    <div style={{ fontSize: 22, fontWeight: 800, color, letterSpacing: "-0.02em", lineHeight: 1.1 }}>
      {value}
    </div>
    {sub && <div style={{ fontSize: 11, color: "#5A6070", marginTop: 3 }}>{sub}</div>}
    {badge && <div style={{ marginTop: 6 }}><Tag color={color}>{badge}</Tag></div>}
  </div>
);

export const CustomTooltip = ({ active, payload, label, unit = "" }) => {
  if (!active || !payload?.length) return null;
  return (
    <div style={{
      background: "#1A1A2E", borderRadius: 8, padding: "10px 14px",
      color: "#fff", fontSize: 12, boxShadow: "0 8px 24px rgba(0,0,0,0.3)",
    }}>
      <div style={{ fontWeight: 700, marginBottom: 6, color: "#94a3b8" }}>{label}</div>
      {payload.map((p, i) => (
        <div key={i} style={{ color: p.color || "#fff" }}>
          {p.name}: <b>{p.value != null ? `${unit}${p.value}` : "—"}</b>
        </div>
      ))}
    </div>
  );
};

export const SignalBadge = ({ signal, sentiment }) => {
  const dot = sentiment === "bull" ? "🟢" : sentiment === "bear" ? "🔴" : "⚪";
  return <span style={{ fontSize: 12 }}>{dot} {signal}</span>;
};

export const SeverityBadge = ({ severity }) => {
  const map = { 高: { emoji: "🔴", color: "#C0392B" }, 中高: { emoji: "🟠", color: "#D4770A" }, 中: { emoji: "🟡", color: "#D4770A" }, 低中: { emoji: "🟢", color: "#1A7A5E" } };
  const { emoji, color } = map[severity] || { emoji: "⚪", color: "#94a3b8" };
  return <span style={{ color, fontWeight: 700, fontSize: 12 }}>{emoji} {severity}</span>;
};

export const ImpactBadge = ({ impact }) => {
  const map = { 高: "#C0392B", 中高: "#D4770A", 中: "#D4770A" };
  return <Tag color={map[impact] || "#94a3b8"}>{impact}</Tag>;
};

export const Btn = ({ children, active, color, onClick, style = {} }) => (
  <button onClick={onClick} style={{
    padding: "8px 16px", borderRadius: 8, cursor: "pointer",
    border: `1.5px solid ${active ? color : "#E2E8F0"}`,
    background: active ? color : "#fff",
    color: active ? "#fff" : "#5A6070",
    fontWeight: 700, fontSize: 14,
    transition: "all 0.15s", ...style,
  }}>{children}</button>
);

export const DownloadBtn = ({ children, onClick, color = "#2563A8", loading }) => (
  <button onClick={onClick} disabled={loading} style={{
    display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
    width: "100%", padding: "12px 20px",
    background: loading ? "#E2E8F0" : color,
    color: loading ? "#94a3b8" : "#fff",
    border: "none", borderRadius: 10,
    fontSize: 14, fontWeight: 700, cursor: loading ? "not-allowed" : "pointer",
    transition: "all 0.15s",
  }}>
    {loading ? "⏳ 生成中…" : children}
  </button>
);

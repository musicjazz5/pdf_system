#!/usr/bin/env python3
"""
AI 水冷散熱供應鏈 — PDF 研究報告產生器
=============================================
使用方式：
    python3 pdf_report_generator.py

依賴套件：
    pip install weasyprint pypdf

支援功能：
    1. generate_cover_page()   — 封面
    2. generate_section()      — 章節內容（含表格、瀑布圖、指標卡、說明框）
    3. merge_pdfs()            — 合併多份 PDF
    4. ReportBuilder           — 高階 Builder，組合完整報告
"""

import datetime
import os
import subprocess
import tempfile

try:
    import weasyprint
except Exception:
    weasyprint = None

try:
    from pypdf import PdfWriter, PdfReader
except Exception:
    PdfWriter = None
    PdfReader = None


# ─────────────────────────────────────────────
# 全域 CSS（所有頁面共用）
# ─────────────────────────────────────────────
BASE_CSS = """
@page {
  size: A4;
  margin: 16mm 18mm 16mm 18mm;
  @bottom-right {
    content: counter(page) " / " counter(pages);
    font-size: 8pt; color: #888;
  }
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: "Noto Sans CJK TC","WenQuanYi Zen Hei","Noto Sans",serif;
  font-size: 9.5pt; line-height: 1.58; color: #2C2C2A; background: white;
}

/* ── 封面 ── */
.cover {
  border-radius: 10px; padding: 26pt 26pt 20pt;
  margin-bottom: 20pt; page-break-after: always;
}
.cover h1 { font-size: 22pt; font-weight: 700; color: white; line-height: 1.3; margin-bottom: 8pt; }
.cover h2 { font-size: 12pt; color: rgba(255,255,255,0.75); margin-bottom: 6pt; }
.cover .sub { font-size: 9pt; color: rgba(255,255,255,0.55); margin-bottom: 5pt; }
.cover .date { font-size: 8pt; color: rgba(255,255,255,0.4); margin-top: 12pt; }
.badges { display: flex; gap: 7pt; margin-top: 14pt; flex-wrap: wrap; }
.badge { display: inline-block; padding: 3pt 9pt; border-radius: 20pt;
         font-size: 7.5pt; font-weight: 700; color: white;
         background: rgba(255,255,255,0.18); }

/* ── 標題 ── */
h1.sec { font-size: 13pt; font-weight: 700; color: #2C2C2A;
         margin: 16pt 0 4pt; padding-bottom: 3pt;
         border-bottom: 0.5pt solid #D3D1C7; }
h2.ssec { font-size: 11pt; font-weight: 700; color: #2C2C2A; margin: 10pt 0 4pt; }
h3.sssec { font-size: 10pt; font-weight: 700; color: #5F5E5A; margin: 8pt 0 3pt; }
p { margin-bottom: 5pt; font-size: 9.5pt; }

/* ── 指標卡片 ── */
.mc-row { display: flex; gap: 7pt; margin: 6pt 0 12pt; }
.mc { flex: 1; border-radius: 6pt; padding: 9pt 10pt; border-top: 3pt solid; }
.mc .lbl { font-size: 7.5pt; margin-bottom: 2pt; }
.mc .val { font-size: 18pt; font-weight: 700; line-height: 1.1; margin-bottom: 2pt; }
.mc .sub { font-size: 7.5pt; }
/* 顏色主題 */
.mc-blue   { background:#E6F1FB; border-color:#185FA5; }
.mc-blue   .lbl, .mc-blue   .sub { color:#0C447C; }
.mc-blue   .val { color:#185FA5; }
.mc-amber  { background:#FAEEDA; border-color:#BA7517; }
.mc-amber  .lbl, .mc-amber  .sub { color:#633806; }
.mc-amber  .val { color:#854F0B; }
.mc-purple { background:#EEEDFE; border-color:#533AB7; }
.mc-purple .lbl, .mc-purple .sub { color:#3C3489; }
.mc-purple .val { color:#533AB7; }
.mc-green  { background:#E1F5EE; border-color:#1D9E75; }
.mc-green  .lbl, .mc-green  .sub { color:#085041; }
.mc-green  .val { color:#1D9E75; }
.mc-red    { background:#FCEBEB; border-color:#A32D2D; }
.mc-red    .lbl, .mc-red    .sub { color:#791F1F; }
.mc-red    .val { color:#A32D2D; }
.mc-gray   { background:#F1EFE8; border-color:#888780; }
.mc-gray   .lbl, .mc-gray   .sub { color:#5F5E5A; }
.mc-gray   .val { color:#2C2C2A; }

/* ── 表格 ── */
table { width:100%; border-collapse:collapse; font-size:8.5pt; margin:6pt 0 10pt; }
thead tr { background:#2C2C2A; color:white; }
thead th { padding:5pt 7pt; font-weight:700; text-align:center; }
thead th:first-child { text-align:left; }
tbody tr:nth-child(odd)  { background:#FAFAF8; }
tbody tr:nth-child(even) { background:#F1EFE8; }
tbody td { padding:5pt 7pt; text-align:center; border-bottom:0.4pt solid #D3D1C7; }
tbody td:first-child { text-align:left; font-weight:500; color:#5F5E5A; }
.tbl-blue   { color:#185FA5; font-weight:700; }
.tbl-amber  { color:#854F0B; font-weight:700; }
.tbl-red    { color:#A32D2D; font-weight:700; }
.tbl-grn    { color:#3B6D11; font-weight:700; }
.tbl-purple { color:#533AB7; font-weight:700; }
.tbl-hl     { background:#EEEDFE !important; }

/* ── 瀑布圖列 ── */
.wf-wrap { display:flex; gap:18pt; margin:10pt 0 12pt; }
.wf-col  { flex:1; }
.wf-header { font-size:10pt; font-weight:700; padding:5pt 8pt;
             border-radius:4pt; margin-bottom:8pt; text-align:center; }
.wf-row  { display:flex; align-items:center; gap:6pt; margin-bottom:5pt; }
.wf-lbl  { width:85pt; font-size:8pt; color:#5F5E5A; text-align:right; flex-shrink:0; }
.wf-bar-wrap { flex:1; height:16pt; background:#F1EFE8; border-radius:3pt; overflow:hidden; }
.wf-fill { height:100%; border-radius:3pt; display:flex; align-items:center;
           padding-left:5pt; font-size:8pt; font-weight:700; }
.wf-pct  { width:35pt; font-size:8pt; font-weight:700; text-align:right; flex-shrink:0; }
.wf-divider { font-size:7.5pt; color:#888780; padding:3pt 0 2pt;
              border-bottom:0.5pt solid #D3D1C7; margin-bottom:4pt; }

/* ── 說明框（Callout） ── */
.callout { display:flex; border-radius:5pt; margin:5pt 0 8pt; overflow:hidden; }
.callout .cl { padding:8pt 10pt; font-size:8.5pt; font-weight:700;
               min-width:75pt; max-width:75pt; line-height:1.35; flex-shrink:0; }
.callout .cr { padding:8pt 10pt; font-size:8.5pt; line-height:1.55; flex:1; }

/* ── 強調框 ── */
.key-box { border-radius:8pt; padding:14pt 16pt; margin:10pt 0 14pt; }
.key-box .kh { font-size:11pt; font-weight:700; margin-bottom:6pt; }
.key-box p  { font-size:9pt; margin-bottom:4pt; line-height:1.6; }

/* ── 情境卡 ── */
.fc-wrap { display:flex; gap:7pt; margin:8pt 0 10pt; }
.fc { flex:1; border-radius:6pt; padding:9pt 10pt; border-top:3pt solid; text-align:center; }
.fc h4  { font-size:9pt; font-weight:700; margin-bottom:5pt; }
.fc .big{ font-size:20pt; font-weight:700; margin:3pt 0; }
.fc p   { font-size:8pt; color:#5F5E5A; margin:2pt 0; }

/* ── 原因列表 ── */
.reason-grid { display:flex; flex-direction:column; gap:6pt; margin:8pt 0; }
.reason { display:flex; gap:10pt; padding:9pt 10pt; border-radius:5pt;
          border-left:4pt solid; font-size:8.5pt; page-break-inside:avoid; }
.reason .num   { font-size:16pt; font-weight:700; flex-shrink:0; line-height:1; margin-top:2pt; }
.reason .rtitle{ font-weight:700; margin-bottom:3pt; font-size:9pt; }
.reason .rdesc { color:#5F5E5A; line-height:1.55; margin:0; font-size:8.5pt; }

/* ── 時間軸 ── */
.timeline { margin:8pt 0 10pt; }
.tl-item  { display:flex; gap:10pt; margin-bottom:6pt; align-items:flex-start; }
.tl-dot   { width:8pt; height:8pt; border-radius:50%; flex-shrink:0; margin-top:3pt; }
.tl-content { flex:1; font-size:8.5pt; }
.tl-date  { font-size:7.5pt; color:#888; margin-bottom:1pt; }

/* ── 產品佔比條 ── */
.mix-bar { margin:8pt 0; }
.mix-row { display:flex; align-items:center; gap:8pt; margin-bottom:5pt; font-size:8.5pt; }
.mix-label { width:80pt; color:#5F5E5A; text-align:right; }
.mix-track { flex:1; background:#F1EFE8; height:14pt; border-radius:3pt; overflow:hidden; }
.mix-fill  { height:100%; border-radius:3pt; display:flex; align-items:center;
             padding-left:6pt; font-size:7.5pt; font-weight:700; color:white; }
.mix-val   { width:30pt; color:#2C2C2A; font-weight:700; }

/* ── 杜邦拆解 ── */
.dupont { display:flex; gap:5pt; align-items:center; margin:6pt 0 10pt; }
.db { flex:1; background:#F1EFE8; border-radius:6pt; padding:7pt 6pt; text-align:center; }
.db.roe { background:#EEEDFE; border:1.5pt solid #533AB7; }
.db .dl { font-size:7.5pt; color:#5F5E5A; margin-bottom:2pt; }
.db .dv { font-size:14pt; font-weight:700; color:#2C2C2A; }
.db.roe .dl { color:#7F77DD; }
.db.roe .dv { color:#533AB7; }
.dupont-op { font-size:17pt; color:#B4B2A9; flex:0 0 auto; }

/* ── 估值框 ── */
.val-box { border:1.5pt solid #BA7517; border-radius:7pt;
           padding:11pt 14pt; margin:8pt 0;
           background:#FFF8EE; }
.val-row { display:flex; justify-content:space-between; align-items:center;
           padding:5pt 0; border-bottom:0.4pt solid #FAC775; font-size:8.5pt; }
.val-row:last-child { border-bottom:none; }
.vl { color:#5F5E5A; }
.vv { font-weight:700; color:#854F0B; }

/* ── 免責聲明 ── */
.disclaimer { margin-top:14pt; padding-top:6pt; border-top:0.5pt solid #D3D1C7;
              font-size:7.5pt; color:#888780; line-height:1.5; }

/* ── 兩欄 ── */
.two-col { display:flex; gap:10pt; margin:6pt 0; }
.two-col > div { flex:1; }
"""


# ─────────────────────────────────────────────
# 低階 HTML 元件 helpers
# ─────────────────────────────────────────────

def metric_cards(items):
    """
    items: list of (label, value, sub, theme)
    theme: 'blue' | 'amber' | 'purple' | 'green' | 'red' | 'gray'
    """
    cards = ""
    for label, value, sub, theme in items:
        cards += f"""
        <div class="mc mc-{theme}">
          <p class="lbl">{label}</p>
          <p class="val">{value}</p>
          <p class="sub">{sub}</p>
        </div>"""
    return f'<div class="mc-row">{cards}</div>'


def data_table(headers, rows, highlight_col=None, col_colors=None):
    """
    headers: list of str
    rows: list of list (each inner list = one row)
    highlight_col: index of column to highlight (0-based)
    col_colors: dict { col_idx: 'tbl-blue'|'tbl-amber'|'tbl-red'|'tbl-grn'|'tbl-purple' }
    """
    th_html = "".join(f"<th>{h}</th>" for h in headers)
    rows_html = ""
    for row in rows:
        tds = ""
        for i, cell in enumerate(row):
            cls = ""
            if col_colors and i in col_colors:
                cls = f' class="{col_colors[i]}"'
            elif highlight_col is not None and i == highlight_col:
                cls = ' class="tbl-hl"'
            tds += f"<td{cls}>{cell}</td>"
        rows_html += f"<tr>{tds}</tr>"
    return f"""
<table>
  <thead><tr>{th_html}</tr></thead>
  <tbody>{rows_html}</tbody>
</table>"""


def callout(title, body, accent_bg, accent_color, body_bg, border_color):
    """Single callout / insight box."""
    return f"""
<div class="callout">
  <div class="cl" style="background:{accent_bg};color:{accent_color};border-left:3pt solid {border_color};">{title}</div>
  <div class="cr" style="background:{body_bg};">{body}</div>
</div>"""


def key_box(heading, paragraphs, bg="#2C2C2A", heading_color="#FAC775", text_color="#D3D1C7"):
    """Dark key-finding box."""
    paras = "".join(f'<p style="color:{text_color};">{p}</p>' for p in paragraphs)
    return f"""
<div class="key-box" style="background:{bg};">
  <p class="kh" style="color:{heading_color};">{heading}</p>
  {paras}
</div>"""


def scenario_cards(scenarios):
    """
    scenarios: list of (title, subtitle, big_value, detail_lines, bg, border_color, text_color)
    """
    cards = ""
    for title, subtitle, big_val, details, bg, border, color in scenarios:
        detail_html = "".join(f"<p>{d}</p>" for d in details)
        cards += f"""
        <div class="fc" style="background:{bg};border-color:{border};">
          <h4 style="color:{color};">{title}</h4>
          <p>{subtitle}</p>
          <div class="big" style="color:{color};">{big_val}</div>
          {detail_html}
        </div>"""
    return f'<div class="fc-wrap">{cards}</div>'


def dupont_strip(factors, result_label, result_value):
    """
    factors: list of (label, value)
    result_label, result_value: the final ROE box
    """
    boxes = ""
    for i, (lbl, val) in enumerate(factors):
        if i > 0:
            boxes += '<div class="dupont-op">×</div>'
        boxes += f'<div class="db"><div class="dl">{lbl}</div><div class="dv">{val}</div></div>'
    boxes += f'<div class="dupont-op">=</div>'
    boxes += f'<div class="db roe"><div class="dl">{result_label}</div><div class="dv">{result_value}</div></div>'
    return f'<div class="dupont">{boxes}</div>'


def timeline_items(items):
    """
    items: list of (date_str, body_html, dot_color)
    """
    html = ""
    for date, body, color in items:
        html += f"""
        <div class="tl-item">
          <div class="tl-dot" style="background:{color};"></div>
          <div class="tl-content">
            <div class="tl-date">{date}</div>
            {body}
          </div>
        </div>"""
    return f'<div class="timeline">{html}</div>'


def mix_bars(items, title=""):
    """
    items: list of (label, pct_int, bar_color, value_label)
    """
    rows = ""
    for label, pct, color, val_label in items:
        rows += f"""
        <div class="mix-row">
          <div class="mix-label">{label}</div>
          <div class="mix-track">
            <div class="mix-fill" style="width:{min(pct,100)}%;background:{color};">{pct}%</div>
          </div>
          <div class="mix-val">{val_label}</div>
        </div>"""
    header = f'<div style="font-size:7.5pt;color:#5F5E5A;margin-bottom:6pt;font-weight:700;">{title}</div>' if title else ""
    return f'<div class="mix-bar">{header}{rows}</div>'


def reason_list(items):
    """
    items: list of (num_label, title, desc, bg, border_color, num_color)
    """
    html = ""
    for num, title, desc, bg, border, color in items:
        html += f"""
        <div class="reason" style="background:{bg};border-color:{border};">
          <div class="num" style="color:{color};">{num}</div>
          <div class="body">
            <p class="rtitle">{title}</p>
            <p class="rdesc">{desc}</p>
          </div>
        </div>"""
    return f'<div class="reason-grid">{html}</div>'


def cover(
    title, subtitle, description, date_str,
    badges=None,
    bg_gradient="linear-gradient(140deg,#533AB7 0%,#3C3489 100%)",
    border_color="#1D9E75"
):
    badge_html = ""
    if badges:
        spans = "".join(f'<span class="badge">{b}</span>' for b in badges)
        badge_html = f'<div class="badges">{spans}</div>'
    return f"""
<div class="cover" style="background:{bg_gradient};border-bottom:4px solid {border_color};">
  <h1>{title}</h1>
  <h2>{subtitle}</h2>
  <p class="sub">{description}</p>
  {badge_html}
  <p class="date">製作日期：{date_str}</p>
</div>"""


def section_heading(text, level=1):
    tag = "h1" if level == 1 else ("h2" if level == 2 else "h3")
    cls = "sec" if level == 1 else ("ssec" if level == 2 else "sssec")
    return f'<{tag} class="{cls}">{text}</{tag}>'


def disclaimer(text=None):
    default = ("本報告所有數據均為公開資訊整理及模型估算，僅供研究參考，不構成任何投資建議。"
               "預估數字涉及假設與不確定性，實際結果可能與預估有重大差異。"
               "投資人應審慎評估風險，自行負責投資決策。")
    body = text or default
    return f'<div class="disclaimer"><strong>免責聲明：</strong>{body}</div>'


def default_output_dir():
    """Return a writable default output directory for generated PDFs."""
    return os.path.join(os.getcwd(), "outputs")


# ─────────────────────────────────────────────
# HTML 組裝與 PDF 輸出
# ─────────────────────────────────────────────

def build_html(*sections):
    """Wrap sections in full HTML document."""
    body = "\n".join(sections)
    return f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
<meta charset="UTF-8">
<style>
{BASE_CSS}
</style>
</head>
<body>
{body}
</body>
</html>"""


def html_to_pdf(html_str, output_path):
    """Render HTML string to PDF using WeasyPrint."""
    if weasyprint is not None:
        weasyprint.HTML(string=html_str).write_pdf(output_path)
    else:
        # Fallback for macOS environments where Python bindings cannot locate
        # system libraries but the Homebrew weasyprint CLI is available.
        with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False, encoding="utf-8") as f:
            f.write(html_str)
            temp_html = f.name
        try:
            subprocess.run(
                ["weasyprint", temp_html, output_path],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        finally:
            if os.path.exists(temp_html):
                os.remove(temp_html)
    size_kb = os.path.getsize(output_path) / 1024
    if PdfReader is not None:
        pages = len(PdfReader(output_path).pages)
        print(f"  產生：{output_path}  ({pages} 頁, {size_kb:.0f} KB)")
    else:
        print(f"  產生：{output_path}  ({size_kb:.0f} KB)")
    return output_path


def merge_pdfs(pdf_paths, output_path, title="合併報告"):
    """Merge multiple PDFs into one."""
    if PdfWriter is None or PdfReader is None:
        raise RuntimeError("merge_pdfs 需要安裝 pypdf。")
    writer = PdfWriter()
    for path in pdf_paths:
        reader = PdfReader(path)
        for page in reader.pages:
            writer.add_page(page)
    writer.add_metadata({
        '/Title': title,
        '/Creator': 'PDF Report Generator',
    })
    with open(output_path, 'wb') as f:
        writer.write(f)
    size_kb = os.path.getsize(output_path) / 1024
    pages = len(PdfReader(output_path).pages)
    print(f"  合併：{output_path}  ({pages} 頁, {size_kb:.0f} KB)")
    return output_path


# ─────────────────────────────────────────────
# ReportBuilder — 高階 Builder 介面
# ─────────────────────────────────────────────

class ReportBuilder:
    """
    高階報告建構器，支援鏈式呼叫（method chaining）。

    範例：
        report = (ReportBuilder("output.pdf")
            .add_cover("雙鴻分析", "副標題", "說明文字",
                       badges=["水冷", "AI"], bg_gradient="linear-gradient(...)")
            .add_section("一、公司概況")
            .add_paragraph("公司成立於 1999 年...")
            .add_metric_cards([
                ("EPS", "28.26元", "年增33%", "amber"),
                ("毛利率", "27.4%", "快速提升", "green"),
            ])
            .add_table(["指標","奇鋐","雙鴻"], [["毛利率","26%","27%"]])
            .add_callout("核心洞察", "差距在費用層", "#EEEDFE","#533AB7","#F5F4FE","#7F77DD")
            .add_disclaimer()
            .build())
    """

    def __init__(self, output_path):
        self.output_path = output_path
        self._sections = []

    def _add(self, html):
        self._sections.append(html)
        return self

    def add_cover(self, title, subtitle, description, badges=None,
                  bg_gradient="linear-gradient(140deg,#533AB7 0%,#3C3489 100%)",
                  border_color="#1D9E75"):
        today = datetime.date.today().strftime("%Y年%m月%d日")
        return self._add(cover(title, subtitle, description, today,
                               badges=badges, bg_gradient=bg_gradient,
                               border_color=border_color))

    def add_section(self, text, level=1):
        return self._add(section_heading(text, level))

    def add_paragraph(self, text):
        return self._add(f"<p>{text}</p>")

    def add_html(self, raw_html):
        """直接插入原始 HTML（彈性擴充）。"""
        return self._add(raw_html)

    def add_metric_cards(self, items):
        """items: [(label, value, sub, theme), ...]"""
        return self._add(metric_cards(items))

    def add_table(self, headers, rows, highlight_col=None, col_colors=None):
        return self._add(data_table(headers, rows, highlight_col, col_colors))

    def add_callout(self, title, body, accent_bg, accent_color, body_bg, border_color):
        return self._add(callout(title, body, accent_bg, accent_color, body_bg, border_color))

    def add_key_box(self, heading, paragraphs,
                    bg="#2C2C2A", heading_color="#FAC775", text_color="#D3D1C7"):
        return self._add(key_box(heading, paragraphs, bg, heading_color, text_color))

    def add_scenarios(self, scenarios):
        """scenarios: [(title, subtitle, big_val, [details], bg, border, color), ...]"""
        return self._add(scenario_cards(scenarios))

    def add_dupont(self, factors, result_label="ROE", result_value=""):
        """factors: [(label, value), ...]"""
        return self._add(dupont_strip(factors, result_label, result_value))

    def add_timeline(self, items):
        """items: [(date_str, body_html, dot_color), ...]"""
        return self._add(timeline_items(items))

    def add_mix_bars(self, items, title=""):
        """items: [(label, pct_int, color, val_label), ...]"""
        return self._add(mix_bars(items, title))

    def add_reasons(self, items):
        """items: [(num, title, desc, bg, border_color, num_color), ...]"""
        return self._add(reason_list(items))

    def add_disclaimer(self, text=None):
        return self._add(disclaimer(text))

    def build(self):
        """Render all sections to PDF and return output path."""
        html = build_html(*self._sections)
        return html_to_pdf(html, self.output_path)


# ─────────────────────────────────────────────
# 範例：快速產生一份示範報告
# ─────────────────────────────────────────────

def build_sample_report(output_dir=None):
    """產生一份示範報告，展示所有元件的使用方式。"""

    output_dir = output_dir or default_output_dir()
    os.makedirs(output_dir, exist_ok=True)
    out = os.path.join(output_dir, "示範報告_雙鴻分析.pdf")

    report = (
        ReportBuilder(out)

        # ── 封面 ──
        .add_cover(
            title="雙鴻科技（3324）示範報告",
            subtitle="AI 水冷散熱轉型分析",
            description="本文件為 PDF 報告產生器的示範輸出，展示所有可用元件。",
            badges=["GB300 認證", "AWS Trainium", "泰國廠量產", "ROE 改善最陡"],
            bg_gradient="linear-gradient(140deg,#854F0B 0%,#BA7517 55%,#EF9F27 100%)",
            border_color="#533AB7",
        )

        # ── 核心結論框 ──
        .add_key_box(
            heading="核心結論",
            paragraphs=[
                "雙鴻 2025 年 EPS 28.26 元創歷史新高，毛利率提升至 27.4%。",
                "2026 年費用槓桿是 EPS 翻倍的最大驅動引擎，勝過毛利率改善。",
                "淨利率與奇鋐的差距完全來自規模效應與轉型期投資，非競爭力劣勢。",
            ],
        )

        # ── 指標卡片 ──
        .add_section("一、2025 年度財務摘要")
        .add_metric_cards([
            ("2025A EPS", "28.26元", "年增 33%｜歷史新高", "amber"),
            ("全年營收", "232.76億", "年增 47.5%", "gray"),
            ("毛利率", "27.4%", "水冷佔比提升帶動", "green"),
            ("ROE 2025E", "~38%", "改善斜率四廠最陡", "purple"),
        ])

        # ── 表格 ──
        .add_section("二、費用結構對比", level=2)
        .add_table(
            headers=["損益項目", "奇鋐 3017", "雙鴻 3324", "差距", "根本原因"],
            rows=[
                ["毛利率", "~26%", "27.4%", "+1pp（雙鴻略優）", "產品端競爭力相當"],
                ["總費用率", "~8%", "~16%", "-8pp（關鍵差異）", "規模效應+泰國折舊"],
                ["營業利益率", "~18%", "~11%", "-7pp", "費用差距直接反映"],
                ["稅後淨利率", "~16%", "~11%", "-5pp", "費用為主因"],
            ],
            col_colors={1: "tbl-blue", 2: "tbl-amber", 3: "tbl-red"},
        )

        # ── 杜邦拆解 ──
        .add_section("三、ROE 杜邦拆解", level=2)
        .add_dupont(
            factors=[("淨利率", "~11%"), ("資產週轉率", "~2.0x"), ("財務槓桿", "~1.7x")],
            result_label="ROE 2025E",
            result_value="~38%",
        )

        # ── 產品佔比條 ──
        .add_section("四、業務結構轉型", level=2)
        .add_mix_bars([
            ("伺服器", 72, "#533AB7", "72% ↑"),
            ("PC", 18, "#888780", "18% ↓"),
            ("顯示卡", 9, "#D3D1C7", "9% ↓"),
        ], title="2026E 公司預估")

        # ── 情境卡 ──
        .add_section("五、2026 年情境分析")
        .add_scenarios([
            ("樂觀情境（30%）", "Rubin H1 + Trainium 3 超預期",
             "EPS ~65元", ["ROE：~58%", "目標價：~1,600元"],
             "#EAF3DE", "#3B6D11", "#3B6D11"),
            ("基本情境（50%）", "GB300 持續 + Rubin H2 開始",
             "EPS ~58元", ["ROE：~50%", "目標價：~1,280元"],
             "#FAEEDA", "#BA7517", "#854F0B"),
            ("保守情境（20%）", "Rubin 延誤 + 泰國爬坡慢",
             "EPS ~40元", ["ROE：~38%", "目標價：~760元"],
             "#FCEBEB", "#A32D2D", "#A32D2D"),
        ])

        # ── 原因列表 ──
        .add_section("六、費用差距根本原因")
        .add_reasons([
            ("①", "規模效應（最核心）",
             "奇鋐營收是雙鴻 6 倍，相同固定費用攤在大 6 倍的分母上，費用率自然壓低 4–5pp。",
             "#E6F1FB", "#185FA5", "#185FA5"),
            ("②", "泰國建廠折舊（暫時性）",
             "泰國廠一二期折舊密集進入 2025–2026 年損益，壓低營業利益率約 1–2pp。",
             "#FAEEDA", "#BA7517", "#BA7517"),
            ("③", "多元業務分散研發成本",
             "五條產品線同時推進，NRE 費用無法集中；2026 年伺服器佔比拉到 72% 後改善。",
             "#FAEEDA", "#BA7517", "#BA7517"),
            ("④", "轉型期一次性前期費用",
             "泰國廠設立、客戶認證等費用集中在 2024–2025 年，後續不再持續累積。",
             "#EAF3DE", "#3B6D11", "#3B6D11"),
        ])

        # ── 時間軸 ──
        .add_section("七、2026 年關鍵催化劑")
        .add_timeline([
            ("2026 Q1（進行中）",
             "<strong>泰國二期量產 + GB300 主力出貨</strong> — Q1 累計營收 85.5 億，年增 94%。",
             "#854F0B"),
            ("2026 H1",
             "<strong>AWS Trainium 3 量產</strong> — ASIC 散熱訂單增幅預計超過 200%。",
             "#533AB7"),
            ("2026 H2",
             "<strong>NVIDIA Rubin VR200 全水冷放量</strong> — 單機櫃水冷組件產值翻倍。",
             "#1D9E75"),
        ])

        # ── Callout 說明框 ──
        .add_callout(
            "費用槓桿公式",
            "費用率從 16% 降至 10%，6pp 下降 × 450 億（2026E 營收）≈ 27 億額外淨利，對應 EPS 約 +30 元。"
            "這正是 EPS 從 28 元跳升至 58 元的最大單一驅動因子。",
            "#EEEDFE", "#533AB7", "#F5F4FE", "#7F77DD",
        )

        # ── 免責聲明 ──
        .add_disclaimer()

        # ── 輸出 ──
        .build()
    )

    return out


def build_coherent_vs_lumentum_report(output_dir=None):
    """
    產生 Coherent vs Lumentum 比較報告。

    資料基礎：
    - Coherent：2026-02-04 公布之 FY2026 Q2（截至 2025-12-31）
    - Lumentum：2026-02-03 公布之 FY2026 Q2（截至 2025-12-27）
    - 年度比較：兩家公司各自 FY2025 全年公告
    """

    output_dir = output_dir or default_output_dir()
    os.makedirs(output_dir, exist_ok=True)
    out = os.path.join(output_dir, "Coherent_vs_Lumentum_比較報告.pdf")

    report = (
        ReportBuilder(out)

        .add_cover(
            title="Coherent vs Lumentum 比較報告",
            subtitle="光通訊 / Photonics 平台競爭力對照",
            description=("以 2026 年 2 月公告之最新官方季報為主，輔以 FY2025 全年數據，"
                         "聚焦規模、毛利率、產品組合與獲利彈性。"),
            badges=["資料基準：FY2026 Q2", "官方 IR / 財報", "Cloud AI 光模組需求", "比較版 PDF"],
            bg_gradient="linear-gradient(140deg,#0C447C 0%,#185FA5 45%,#1D9E75 100%)",
            border_color="#BA7517",
        )

        .add_key_box(
            heading="核心結論",
            paragraphs=[
                "截至 2026 年 2 月最新公告，Coherent 的季度營收規模約為 Lumentum 的 2.5 倍，毛利率亦維持較高且更穩定。",
                "Lumentum 的復甦斜率更陡。FY2026 Q2 營收年增 65.5%、Non-GAAP 營業利益率達 25.2%，代表 Cloud/AI 需求正快速放大。",
                "如果看平台屬性，Coherent 更像大而全的光子平台；Lumentum 則更集中受惠於雲端與網通景氣循環，彈性更高但波動也更大。",
            ],
            bg="#1B2430",
            heading_color="#FAC775",
            text_color="#E7E4DA",
        )

        .add_section("一、最新季度摘要（FY2026 Q2）")
        .add_metric_cards([
            ("Coherent 營收", "US$1.69B", "FY2026 Q2｜2026-02-04 公告", "blue"),
            ("Lumentum 營收", "US$665.5M", "FY2026 Q2｜2026-02-03 公告", "green"),
            ("Coherent GAAP 毛利率", "36.9%", "Non-GAAP 39.0%", "purple"),
            ("Lumentum GAAP 毛利率", "36.1%", "Non-GAAP 42.5%", "amber"),
        ])

        .add_section("二、季度數據正面比較", level=2)
        .add_table(
            headers=["指標", "Coherent", "Lumentum", "觀察"],
            rows=[
                ["FY2026 Q2 營收", "US$1.69B", "US$665.5M", "Coherent 規模約 2.5 倍，平台覆蓋更廣"],
                ["營收年增率", "+17%", "+65.5%", "Lumentum 復甦與 AI/Cloud 拉貨斜率更陡"],
                ["GAAP 毛利率", "36.9%", "36.1%", "GAAP 層面已接近"],
                ["Non-GAAP 毛利率", "39.0%", "42.5%", "Lumentum 產品組合上行更明顯"],
                ["GAAP EPS", "US$0.76", "US$0.89", "兩者皆轉強，但口徑不可只看單點"],
                ["Non-GAAP EPS", "US$1.29", "US$1.67", "Lumentum 獲利彈性高於營收增幅"],
            ],
            col_colors={1: "tbl-blue", 2: "tbl-grn"},
        )

        .add_section("三、FY2025 全年基礎盤", level=2)
        .add_table(
            headers=["FY2025 全年", "Coherent", "Lumentum", "含意"],
            rows=[
                ["全年營收", "US$5.81B", "US$1.645B", "Coherent 基礎盤與客戶覆蓋面明顯更大"],
                ["GAAP 毛利率", "35.2%", "28.0%", "Lumentum 仍處復甦過程，基期較低"],
                ["Non-GAAP 毛利率", "37.9%", "34.7%", "Coherent 仍有平台型穩定優勢"],
                ["GAAP / Non-GAAP EPS", "-0.52 / 3.53", "0.37 / 2.06", "Coherent 受 GAAP 調整項影響更大"],
            ],
            col_colors={1: "tbl-blue", 2: "tbl-grn"},
        )

        .add_section("四、商業結構與組合", level=2)
        .add_mix_bars([
            ("Coherent：資料中心/通訊", 55, "#185FA5", "核心引擎"),
            ("Coherent：工業 / 材料 / 其他", 45, "#7F77DD", "分散風險"),
            ("Lumentum：Components", 67, "#1D9E75", "FY26 Q2"),
            ("Lumentum：Systems", 33, "#BA7517", "FY26 Q2"),
        ], title="以公開揭露之主要營收組合近似呈現")

        .add_callout(
            "解讀方式",
            ("Coherent 官方揭露偏向 Datacenter and Communications / Industrial 等平台敘述；"
             "Lumentum FY2026 Q2 則明確揭露 Components 66.7%、Systems 33.3%。"
             "因此本頁重點在看『集中度與循環敏感度』，不是把兩家公司完全同口徑切分。"),
            "#E6F1FB", "#185FA5", "#F4F8FC", "#185FA5",
        )

        .add_section("五、獲利模型差異", level=2)
        .add_dupont(
            factors=[("規模平台", "Coherent 較強"), ("產品組合彈性", "Lumentum 較強"), ("營運槓桿", "Lumentum 較陡")],
            result_label="投資辨識",
            result_value="穩定 vs 彈性",
        )

        .add_reasons([
            ("①", "Coherent 贏在平台廣度",
             "FY2025 全年營收 58.1 億美元，明顯高於 Lumentum 的 16.45 億美元。更大的製造與客戶覆蓋，通常意味著較佳的抗波動能力。",
             "#E6F1FB", "#185FA5", "#185FA5"),
            ("②", "Lumentum 贏在景氣上行彈性",
             "FY2026 Q2 營收年增 65.5%，Non-GAAP 營業利益率 25.2%，顯示當 Cloud/AI 需求回來時，獲利放大速度很快。",
             "#EAF3DE", "#3B6D11", "#3B6D11"),
            ("③", "毛利率差距已非核心",
             "最新季度 GAAP 毛利率 36.9% vs 36.1%，已經非常接近；真正差異在產品組合、營收基礎盤與波動承受度。",
             "#FAEEDA", "#BA7517", "#BA7517"),
            ("④", "估值敘事要分清楚",
             "若市場交易的是『平台型光子龍頭』，Coherent 論述更完整；若市場交易的是『AI 雲端復甦斜率』，Lumentum 更敏感。",
             "#EEEDFE", "#533AB7", "#533AB7"),
        ])

        .add_section("六、近期催化與觀察點")
        .add_timeline([
            ("2025-08-12 / 2025-08-13",
             "<strong>FY2025 全年公告</strong> — Coherent 全年營收 US$5.81B；Lumentum 全年營收 US$1.645B，作為規模基準。",
             "#888780"),
            ("2026-02-03",
             "<strong>Lumentum FY2026 Q2 公告</strong> — 營收 US$665.5M、GAAP 毛利率 36.1%、Non-GAAP 營業利益率 25.2%。",
             "#1D9E75"),
            ("2026-02-04",
             "<strong>Coherent FY2026 Q2 公告</strong> — 營收 US$1.69B、GAAP 毛利率 36.9%、Non-GAAP EPS US$1.29。",
             "#185FA5"),
            ("下一步觀察",
             "<strong>AI 網路建置是否持續外溢</strong> — 若 hyperscaler 資本支出延續，Lumentum 的斜率彈性通常更大；若景氣進入分化，Coherent 的平台防禦性較佳。",
             "#854F0B"),
        ])

        .add_section("七、情境判讀")
        .add_scenarios([
            ("偏防禦情境", "企業支出放緩但資料中心仍投資",
             "Coherent 相對占優", ["平台廣度高", "全年基礎盤較穩", "客戶分散"], "#E6F1FB", "#185FA5", "#185FA5"),
            ("景氣擴張情境", "Cloud / AI 光連接需求再加速",
             "Lumentum 彈性更大", ["營收斜率高", "毛利率上行快", "營運槓桿明顯"], "#EAF3DE", "#3B6D11", "#3B6D11"),
            ("均衡持有情境", "兩者都受惠於 AI 光通訊升級",
             "平台 + 斜率搭配", ["Coherent 打底", "Lumentum 拉彈性", "看風格配置"], "#EEEDFE", "#533AB7", "#533AB7"),
        ])

        .add_disclaimer(
            "本報告使用 Coherent 與 Lumentum 官方 Investor Relations / earnings release 公開資訊整理。"
            "由於兩家公司產品分類與會計口徑並非完全一致，文中比較以趨勢與結構判讀為主，不構成投資建議。"
        )

        .build()
    )

    return out


def build_marvell_vs_broadcom_report(output_dir=None):
    """
    產生 Marvell vs Broadcom 比較報告。

    資料基礎：
    - Marvell：2025-12-02 公布之 FY2026 Q3
    - Broadcom：2026-03-04 公布之 FY2026 Q1
    - 年度比較：Marvell FY2025、Broadcom FY2025 全年公告
    """

    output_dir = output_dir or default_output_dir()
    os.makedirs(output_dir, exist_ok=True)
    out = os.path.join(output_dir, "Marvell_vs_Broadcom_比較報告.pdf")

    report = (
        ReportBuilder(out)

        .add_cover(
            title="Marvell vs Broadcom 比較報告",
            subtitle="AI 基礎設施半導體平台對照",
            description=("聚焦 AI ASIC、Networking、Data Center 與平台規模差距。"
                         "以兩家公司最新官方季報與 FY2025 全年資料比較。"),
            badges=["AI ASIC", "Networking", "平台型 vs 純斜率", "官方 IR / 財報"],
            bg_gradient="linear-gradient(140deg,#2C2C2A 0%,#185FA5 45%,#533AB7 100%)",
            border_color="#FAC775",
        )

        .add_key_box(
            heading="核心結論",
            paragraphs=[
                "Broadcom 是 AI 基礎設施中的超大平台股，FY2026 Q1 單季營收 193.11 億美元，遠高於 Marvell FY2026 Q3 的 20.75 億美元。",
                "Marvell 的投資亮點不在絕對規模，而在 AI 資料中心業務滲透率提升後的營收與獲利斜率。",
                "Broadcom 兼具 AI 半導體與基礎軟體雙引擎；Marvell 則更集中在資料中心互連、客製化 ASIC 與光電互連升級週期。",
            ],
        )

        .add_section("一、最新季度摘要")
        .add_metric_cards([
            ("Marvell 營收", "US$2.075B", "FY2026 Q3｜2025-12-02 公告", "blue"),
            ("Broadcom 營收", "US$19.311B", "FY2026 Q1｜2026-03-04 公告", "purple"),
            ("Marvell GAAP 毛利率", "51.6%", "Non-GAAP 59.7%", "green"),
            ("Broadcom 推算 GAAP 毛利率", "~68.1%", "由 gross margin/revenue 推算", "amber"),
        ])

        .add_section("二、季度數據正面比較", level=2)
        .add_table(
            headers=["指標", "Marvell", "Broadcom", "觀察"],
            rows=[
                ["最新季度營收", "US$2.075B", "US$19.311B", "Broadcom 規模約 9 倍以上"],
                ["年增率", "+37%", "+29%", "Marvell 斜率較快，但 Broadcom 基數極大"],
                ["GAAP 毛利率", "51.6%", "~68.1%", "Broadcom 組合與軟體業務拉高整體毛利"],
                ["Non-GAAP / 調整後指標", "59.7% 毛利率", "68% Adjusted EBITDA", "Broadcom 獲利結構更厚"],
                ["GAAP EPS", "US$2.20", "US$1.50", "Marvell 含出售 automotive ethernet 業務收益"],
                ["業務引擎", "資料中心 / AI 互連", "AI 半導體 + 基礎軟體", "Broadcom 平台更完整"],
            ],
            col_colors={1: "tbl-blue", 2: "tbl-purple"},
        )

        .add_callout(
            "口徑提醒",
            "Marvell FY2026 Q3 的 GAAP EPS 包含出售 automotive ethernet 業務帶來的收益；因此在獲利比較上，更適合搭配 Non-GAAP EPS 或毛利率一起看。",
            "#FAEEDA", "#BA7517", "#FFF8EE", "#BA7517",
        )

        .add_section("三、FY2025 全年基礎盤", level=2)
        .add_table(
            headers=["FY2025 全年", "Marvell", "Broadcom", "含意"],
            rows=[
                ["全年營收", "US$5.767B", "US$63.887B", "Broadcom 為真正超大型平台"],
                ["GAAP EPS / 淨利", "-1.02 / 淨損", "4.77 / 淨利 231.26 億", "Broadcom 盈利成熟度高很多"],
                ["Non-GAAP EPS", "1.57", "6.82", "Broadcom 現金流與股東回饋能力更強"],
                ["收入結構", "偏 Data Infrastructure", "58% 半導體 / 42% 軟體", "Broadcom 抗循環能力更強"],
            ],
            col_colors={1: "tbl-blue", 2: "tbl-purple"},
        )

        .add_section("四、商業結構對比", level=2)
        .add_mix_bars([
            ("Marvell：Data Center / AI", 70, "#185FA5", "核心主軸"),
            ("Marvell：其他多元市場", 30, "#888780", "收斂中"),
            ("Broadcom：半導體", 65, "#533AB7", "FY26 Q1"),
            ("Broadcom：基礎軟體", 35, "#1D9E75", "FY26 Q1"),
        ], title="以最新公告口徑或業務描述近似呈現")

        .add_reasons([
            ("①", "Broadcom 贏在平台與現金流",
             "FY2026 Q1 單季營收 193.11 億美元，Adjusted EBITDA 131.28 億美元，占營收 68%。這種量級讓它能同時投資 AI、回購與配息。",
             "#EEEDFE", "#533AB7", "#533AB7"),
            ("②", "Marvell 贏在 AI 斜率",
             "FY2026 Q3 營收年增 37%，管理層明確指出成長由 data center 產品驅動，且下一季仍預期營收續升至約 22 億美元。",
             "#E6F1FB", "#185FA5", "#185FA5"),
            ("③", "Broadcom 的護城河較寬",
             "除了 AI networking 與 custom accelerator，Broadcom 還有大型基礎軟體收入，讓公司不完全押注單一硬體景氣循環。",
             "#EAF3DE", "#3B6D11", "#3B6D11"),
            ("④", "Marvell 更像純 AI infra beta",
             "若市場追逐 AI 交換器、DSP、光互連與客製化 ASIC 週期，Marvell 往往提供更高彈性，但波動也更大。",
             "#FAEEDA", "#BA7517", "#BA7517"),
        ])

        .add_section("五、近期催化與指引")
        .add_timeline([
            ("2025-12-02",
             "<strong>Marvell FY2026 Q3</strong> — 營收 US$2.075B、GAAP 毛利率 51.6%、Q4 營收指引約 US$2.2B。",
             "#185FA5"),
            ("2026-03-04",
             "<strong>Broadcom FY2026 Q1</strong> — 營收 US$19.311B，AI revenue US$8.4B，Q2 營收指引約 US$22.0B。",
             "#533AB7"),
            ("下一步觀察",
             "<strong>AI 自研晶片與光互連資本開支是否續強</strong> — 若 hyperscaler 持續投入，兩者都受惠，但 Broadcom 受惠面更廣，Marvell 斜率更高。",
             "#854F0B"),
        ])

        .add_section("六、情境判讀")
        .add_scenarios([
            ("偏防禦配置", "重視現金流、平台與股東回饋",
             "Broadcom 優先", ["平台大", "軟體支撐", "現金流厚"], "#EEEDFE", "#533AB7", "#533AB7"),
            ("偏攻擊配置", "重視 AI 基建加速週期",
             "Marvell 彈性較高", ["基期較小", "AI 曝險集中", "營收斜率快"], "#E6F1FB", "#185FA5", "#185FA5"),
            ("均衡配置", "平台 + 斜率並重",
             "Broadcom 打底 / Marvell 拉 beta", ["降低單一風格風險", "兼顧穩定與成長"], "#FAEEDA", "#BA7517", "#854F0B"),
        ])

        .add_disclaimer(
            "本報告使用 Marvell 與 Broadcom 官方 Investor Relations / earnings release 公開資訊整理。"
            "其中 Broadcom GAAP 毛利率係由公告中的 gross margin 與 revenue 試算，屬合理推算值。"
        )

        .build()
    )

    return out


def build_aaoi_vs_lumentum_report(output_dir=None):
    """
    產生 AAOI vs Lumentum 比較報告。

    資料基礎：
    - AAOI：2026-02-26 公布之 2025Q4 / FY2025
    - Lumentum：2026-02-03 公布之 FY2026 Q2，另參考 2025-08-12 FY2025
    """

    output_dir = output_dir or default_output_dir()
    os.makedirs(output_dir, exist_ok=True)
    out = os.path.join(output_dir, "AAOI_vs_Lumentum_比較報告.pdf")

    report = (
        ReportBuilder(out)

        .add_cover(
            title="AAOI vs Lumentum 比較報告",
            subtitle="光模組 / 光元件復甦斜率對照",
            description=("比較 AAOI 與 Lumentum 在雲端、資料中心與光通訊週期中的位置，"
                         "重點放在規模、毛利率、產品結構與 2026 年動能。"),
            badges=["Datacenter optics", "Components vs Systems", "復甦斜率", "官方 IR / 財報"],
            bg_gradient="linear-gradient(140deg,#1D9E75 0%,#185FA5 50%,#2C2C2A 100%)",
            border_color="#FAC775",
        )

        .add_key_box(
            heading="核心結論",
            paragraphs=[
                "Lumentum 目前仍是規模明顯較大的光通訊平台，FY2026 Q2 單季營收 6.655 億美元，高於 AAOI 2025Q4 的 1.343 億美元。",
                "AAOI 的特點是基期小、成長斜率快，2025 全年營收 4.557 億美元，較 2024 年大增約 83%。",
                "若看『平台完整性與獲利成熟度』，Lumentum 較強；若看『小型高速成長光模組供應商彈性』，AAOI 更像高 beta 標的。",
            ],
            bg="#1B2430",
            heading_color="#FAC775",
            text_color="#E7E4DA",
        )

        .add_section("一、最新數字摘要")
        .add_metric_cards([
            ("AAOI 營收", "US$134.3M", "2025Q4｜2026-02-26 公告", "green"),
            ("Lumentum 營收", "US$665.5M", "FY2026 Q2｜2026-02-03 公告", "blue"),
            ("AAOI GAAP 毛利率", "31.2%", "Non-GAAP 31.4%", "amber"),
            ("Lumentum GAAP 毛利率", "36.1%", "Non-GAAP 42.5%", "purple"),
        ])

        .add_section("二、季度數據正面比較", level=2)
        .add_table(
            headers=["指標", "AAOI", "Lumentum", "觀察"],
            rows=[
                ["最新季度營收", "US$134.3M", "US$665.5M", "Lumentum 規模約 5 倍"],
                ["年增率", "+33.9%", "+65.5%", "兩者都強，但 Lumentum 斜率更高"],
                ["GAAP 毛利率", "31.2%", "36.1%", "Lumentum 獲利結構較成熟"],
                ["Non-GAAP 毛利率", "31.4%", "42.5%", "高階產品組合差異明顯"],
                ["GAAP EPS / 每股", "-0.03", "0.89", "AAOI 仍接近損平，Lumentum 已顯著轉強"],
                ["下一季指引", "Q1'26 營收 US$150M-165M", "FY26 Q3 延續成長指引", "AAOI 仍處放量初期"],
            ],
            col_colors={1: "tbl-grn", 2: "tbl-blue"},
        )

        .add_section("三、FY2025 基礎盤", level=2)
        .add_table(
            headers=["FY2025 / 年度基準", "AAOI", "Lumentum", "含意"],
            rows=[
                ["全年營收", "US$455.7M", "US$1.645B", "Lumentum 規模仍為 AAOI 約 3.6 倍"],
                ["GAAP 毛利率", "30.0%", "28.0%", "全年層面 AAOI 已回升到不差水準"],
                ["Non-GAAP 毛利率", "30.9%", "34.7%", "Lumentum 高階組合仍占優"],
                ["全年獲利", "GAAP 淨損 US$38.2M", "GAAP 淨利 US$25.9M", "Lumentum 復甦已先跨過獲利門檻"],
            ],
            col_colors={1: "tbl-grn", 2: "tbl-blue"},
        )

        .add_section("四、產品與商業模型", level=2)
        .add_mix_bars([
            ("AAOI：Datacenter / CATV", 75, "#1D9E75", "需求放量"),
            ("AAOI：其他", 25, "#888780", "相對小"),
            ("Lumentum：Components", 67, "#185FA5", "FY26 Q2"),
            ("Lumentum：Systems", 33, "#BA7517", "FY26 Q2"),
        ], title="依公司揭露與業務描述近似呈現")

        .add_reasons([
            ("①", "Lumentum 贏在平台完整性",
             "Lumentum 不只做光元件，也有 systems 與更廣的客戶基礎。這讓它在景氣回升時，營收與毛利率一起放大。",
             "#E6F1FB", "#185FA5", "#185FA5"),
            ("②", "AAOI 贏在小基期彈性",
             "AAOI 2025Q4 營收年增 33.9%，全年營收從 2.494 億美元升至 4.557 億美元，成長速度很快。",
             "#EAF3DE", "#3B6D11", "#3B6D11"),
            ("③", "Lumentum 的獲利成熟度更高",
             "FY2026 Q2 Non-GAAP 毛利率 42.5%、Non-GAAP 營業利益率 25.2%，代表產品組合與規模效應都更成熟。",
             "#EEEDFE", "#533AB7", "#533AB7"),
            ("④", "AAOI 還在從成長走向穩定獲利",
             "AAOI 最新季度已接近損平，且 Q1 2026 指引營收再往上，但離穩定高獲利平台仍有距離。",
             "#FAEEDA", "#BA7517", "#BA7517"),
        ])

        .add_section("五、近期催化與指引")
        .add_timeline([
            ("2026-02-03",
             "<strong>Lumentum FY2026 Q2</strong> — 營收 US$665.5M、GAAP 毛利率 36.1%、Non-GAAP 毛利率 42.5%。",
             "#185FA5"),
            ("2026-02-26",
             "<strong>AAOI 2025Q4 / FY2025</strong> — Q4 營收 US$134.3M、GAAP 毛利率 31.2%，Q1 2026 營收指引 US$150M-165M。",
             "#1D9E75"),
            ("下一步觀察",
             "<strong>800G/1.6T 與雲端資本開支</strong> — 若 hyperscaler 持續拉貨，AAOI 與 Lumentum 都受惠，但 Lumentum 受惠面更廣，AAOI 彈性更高。",
             "#854F0B"),
        ])

        .add_section("六、情境判讀")
        .add_scenarios([
            ("平台型配置", "重視規模、產品廣度與已驗證獲利",
             "Lumentum 較優", ["規模大", "毛利高", "已跨過獲利門檻"], "#E6F1FB", "#185FA5", "#185FA5"),
            ("高彈性配置", "重視小公司放量斜率",
             "AAOI 較優", ["小基期", "拉貨加速時 beta 高", "營收彈性大"], "#EAF3DE", "#3B6D11", "#3B6D11"),
            ("均衡配置", "平台 + 小型成長股搭配",
             "Lumentum 打底 / AAOI 拉彈性", ["風格互補", "降低單點風險"], "#FAEEDA", "#BA7517", "#854F0B"),
        ])

        .add_disclaimer(
            "本報告使用 Applied Optoelectronics 與 Lumentum 官方 Investor Relations / earnings release 公開資訊整理。"
            "AAOI 與 Lumentum 的產品分類與會計口徑不完全相同，文中比較重點在趨勢與結構。"
        )

        .build()
    )

    return out


def build_broadcom_vs_nvidia_networking_report(output_dir=None):
    """
    產生 Broadcom vs NVIDIA networking 比較報告。

    資料基礎：
    - Broadcom：2026-03-04 公布 FY2026 Q1，搭配 FY2025 全年
    - NVIDIA：FY2026 年報與 Q4/FY2026 公告
    """

    output_dir = output_dir or default_output_dir()
    os.makedirs(output_dir, exist_ok=True)
    out = os.path.join(output_dir, "Broadcom_vs_NVIDIA_networking_比較報告.pdf")

    report = (
        ReportBuilder(out)

        .add_cover(
            title="Broadcom vs NVIDIA Networking 比較報告",
            subtitle="AI 網路骨幹平台對照",
            description=("聚焦 AI cluster 中 Ethernet、InfiniBand、NVLink fabric、"
                         "switch / NIC / interconnect 的競爭位置與商業模式差異。"),
            badges=["Ethernet", "InfiniBand", "NVLink", "AI networking"],
            bg_gradient="linear-gradient(140deg,#533AB7 0%,#185FA5 45%,#1D9E75 100%)",
            border_color="#FAC775",
        )

        .add_key_box(
            heading="核心結論",
            paragraphs=[
                "Broadcom 與 NVIDIA 都是 AI networking 核心受惠者，但切入點不同。Broadcom 更偏交換晶片、客製化 ASIC 生態與平台配套；NVIDIA 則把 networking 當成 AI 系統架構的一部分，與 GPU / NVLink / InfiniBand 綁在一起賣。",
                "若市場押注開放式 Ethernet AI fabric 與 hyperscaler 自研 ASIC 擴張，Broadcom 論述更強；若市場押注全棧式 AI 系統、NVLink + InfiniBand 緊密整合，NVIDIA 的控制力更強。",
                "可比性限制在於 Broadcom 並未單獨揭露 networking revenue，因此與 NVIDIA networking 的比較要以策略位置與 segment 推論為主，不是純財務同口徑對比。",
            ],
        )

        .add_section("一、最新官方數字摘要")
        .add_metric_cards([
            ("Broadcom Q1 FY2026 營收", "US$19.311B", "其中 Semiconductor US$12.515B", "purple"),
            ("Broadcom AI revenue", "US$8.4B", "Q1 FY2026｜年增 106%", "amber"),
            ("NVIDIA FY2026 Compute & Networking", "US$193.479B", "年增 67%", "green"),
            ("NVIDIA Data Center networking", "+142%", "FY2026 年增率｜官方 10-K", "blue"),
        ])

        .add_section("二、核心對照", level=2)
        .add_table(
            headers=["維度", "Broadcom", "NVIDIA networking", "解讀"],
            rows=[
                ["最新可引用財務口徑", "AI revenue US$8.4B；半導體 US$12.5B", "Compute & Networking FY2026 US$193.5B", "NVIDIA 揭露更完整，Broadcom networking 需推論"],
                ["主要產品路線", "Tomahawk / Jericho / custom interconnect", "InfiniBand / Spectrum-X Ethernet / NVLink fabric", "兩者都吃 AI cluster 網路升級"],
                ["商業模式", "元件/晶片供應 + hyperscaler 設計夥伴", "全棧系統平台一體銷售", "NVIDIA 綁定度更高"],
                ["客戶依賴", "大型 CSP / ASIC 客戶", "CSP + AI model builders + OEM", "兩者都高度集中於 hyperscaler capex"],
                ["護城河", "乙太網交換與客製 ASIC 生態", "GPU + networking + software 整合", "Broadcom 偏開放生態，NVIDIA 偏封閉整合"],
            ],
            col_colors={1: "tbl-purple", 2: "tbl-blue"},
        )

        .add_callout(
            "口徑提醒",
            "Broadcom 官方揭露的是 AI semiconductor revenue 與 semiconductor segment revenue，未單獨拆出 networking revenue；NVIDIA 則在 FY2026 年報中明確說明 data center networking 年增 142%。本報告因此用『平台位置』而非『完全同口徑營收』比較。",
            "#FAEEDA", "#BA7517", "#FFF8EE", "#BA7517",
        )

        .add_section("三、平台結構差異", level=2)
        .add_mix_bars([
            ("Broadcom：半導體", 65, "#533AB7", "FY26 Q1"),
            ("Broadcom：基礎軟體", 35, "#7F77DD", "FY26 Q1"),
            ("NVIDIA：Compute & Networking", 90, "#185FA5", "FY26 年報口徑"),
            ("NVIDIA：Graphics / 其他", 10, "#888780", "FY26 年報口徑"),
        ], title="以官方 segment 揭露近似呈現")

        .add_reasons([
            ("①", "Broadcom 的優勢在開放式 AI fabric",
             "Broadcom 深耕交換晶片、SerDes、switch silicon 與客製化 AI ASIC 生態，若大型 CSP 持續推動自研加速器與 Ethernet fabric，Broadcom 往往是核心基礎設施供應商。",
             "#EEEDFE", "#533AB7", "#533AB7"),
            ("②", "NVIDIA 的優勢在系統整合",
             "NVIDIA 將 networking 視為 AI 系統的一部分，而非單一零件。官方年報指出 FY2026 data center networking 年增 142%，動能來自 NVLink fabric、InfiniBand 與 Ethernet 平台。",
             "#E6F1FB", "#185FA5", "#185FA5"),
            ("③", "Broadcom 較像底層基建賣鏟人",
             "就算最終 AI cluster 不是 NVIDIA GPU，Broadcom 仍可能從交換器、ASIC 與互連層受益。這讓 Broadcom 更具架構中立性。",
             "#EAF3DE", "#3B6D11", "#3B6D11"),
            ("④", "NVIDIA 較像整體 AI 工廠營運商",
             "NVIDIA 的 networking 價值在於把算力、互連、軟體與系統設計打包賣出，因此毛利與客戶黏著度通常更高，但也更依賴整體平台優勢持續領先。",
             "#FAEEDA", "#BA7517", "#BA7517"),
        ])

        .add_section("四、近期催化")
        .add_timeline([
            ("2025-12-11",
             "<strong>Broadcom FY2025 全年</strong> — 全年營收 US$63.887B；Q4 半導體營收 US$11.072B，基礎軟體 US$6.943B。",
             "#533AB7"),
            ("2026-03-04",
             "<strong>Broadcom FY2026 Q1</strong> — 營收 US$19.311B；AI revenue US$8.4B；Q2 營收指引約 US$22.0B。",
             "#7F77DD"),
            ("2026-02-25",
             "<strong>NVIDIA FY2026 年報 / Q4</strong> — Compute & Networking FY2026 revenue US$193.479B；data center networking 年增 142%。",
             "#185FA5"),
            ("下一步觀察",
             "<strong>Ethernet AI fabric 是否持續滲透</strong> — 若大型客戶更偏向開放網路架構，Broadcom 受惠更直接；若整機櫃式 tightly-coupled AI systems 持續主導，NVIDIA networking 敘事更強。",
             "#854F0B"),
        ])

        .add_section("五、情境判讀")
        .add_scenarios([
            ("開放生態勝出", "CSP 強化自研 ASIC + Ethernet fabric",
             "Broadcom 占優", ["架構中立", "switch / ASIC 生態深", "客戶面廣"], "#EEEDFE", "#533AB7", "#533AB7"),
            ("全棧平台勝出", "AI factory 更偏向整合式設計",
             "NVIDIA 占優", ["GPU + network 綁定", "NVLink / InfiniBand 完整", "系統控制力高"], "#E6F1FB", "#185FA5", "#185FA5"),
            ("雙贏情境", "AI 資本開支持續擴大",
             "兩者都受惠", ["Broadcom 吃基建", "NVIDIA 吃整機與平台"], "#EAF3DE", "#3B6D11", "#3B6D11"),
        ])

        .add_disclaimer(
            "本報告使用 Broadcom 與 NVIDIA 官方 Investor Relations / SEC 公開資訊整理。"
            "由於 Broadcom 未單獨揭露 networking revenue，與 NVIDIA networking 的財務比較含有推論成分。"
        )

        .build()
    )

    return out


def build_coherent_vs_aaoi_report(output_dir=None):
    """
    產生 Coherent vs AAOI 比較報告。

    資料基礎：
    - Coherent：2026-02-04 FY2026 Q2 與 FY2025 全年
    - AAOI：2026-02-26 2025Q4 / FY2025
    """

    output_dir = output_dir or default_output_dir()
    os.makedirs(output_dir, exist_ok=True)
    out = os.path.join(output_dir, "Coherent_vs_AAOI_比較報告.pdf")

    report = (
        ReportBuilder(out)

        .add_cover(
            title="Coherent vs AAOI 比較報告",
            subtitle="光子平台 vs 小型高速成長光模組供應商",
            description="比較 Coherent 與 AAOI 在規模、毛利率、產品廣度與 AI 光通訊週期中的定位差異。",
            badges=["Photonics platform", "Datacenter optics", "平台型 vs 高 beta", "官方 IR / 財報"],
            bg_gradient="linear-gradient(140deg,#185FA5 0%,#1D9E75 50%,#2C2C2A 100%)",
            border_color="#FAC775",
        )

        .add_key_box(
            heading="核心結論",
            paragraphs=[
                "Coherent 是明顯更大型、更多元的 photonics 平台股。FY2026 Q2 營收 16.9 億美元，遠高於 AAOI 2025Q4 的 1.343 億美元。",
                "AAOI 的強項在小基期放量與資料中心光模組週期彈性，而不是平台完整度。",
                "若市場要的是『大型光子平台 + 較穩毛利』，Coherent 更合適；若市場要的是『小型高彈性 datacenter optics beta』，AAOI 更敏感。",
            ],
        )

        .add_section("一、最新數字摘要")
        .add_metric_cards([
            ("Coherent 營收", "US$1.69B", "FY2026 Q2｜2026-02-04 公告", "blue"),
            ("AAOI 營收", "US$134.3M", "2025Q4｜2026-02-26 公告", "green"),
            ("Coherent GAAP 毛利率", "36.9%", "Non-GAAP 39.0%", "purple"),
            ("AAOI GAAP 毛利率", "31.2%", "Non-GAAP 31.4%", "amber"),
        ])

        .add_section("二、季度數據正面比較", level=2)
        .add_table(
            headers=["指標", "Coherent", "AAOI", "觀察"],
            rows=[
                ["最新季度營收", "US$1.69B", "US$134.3M", "Coherent 規模約 12.6 倍"],
                ["年增率", "+17%", "+33.9%", "AAOI 斜率較快，但基數小很多"],
                ["GAAP 毛利率", "36.9%", "31.2%", "Coherent 毛利結構較成熟"],
                ["Non-GAAP 毛利率", "39.0%", "31.4%", "產品組合與規模效應差異明顯"],
                ["GAAP EPS", "US$0.76", "-US$0.03", "Coherent 已穩定獲利，AAOI 接近損平"],
                ["產品廣度", "多元 photonics / industrial / comms", "以 datacenter / CATV 為主", "Coherent 分散度更高"],
            ],
            col_colors={1: "tbl-blue", 2: "tbl-grn"},
        )

        .add_section("三、FY2025 基礎盤", level=2)
        .add_table(
            headers=["FY2025 全年", "Coherent", "AAOI", "含意"],
            rows=[
                ["全年營收", "US$5.81B", "US$455.7M", "Coherent 約為 AAOI 的 12.7 倍"],
                ["GAAP 毛利率", "35.2%", "30.0%", "Coherent 維持較高毛利"],
                ["Non-GAAP 毛利率", "37.9%", "30.9%", "平台型優勢仍明顯"],
                ["全年獲利", "GAAP 淨損 / Non-GAAP EPS 3.53", "GAAP 淨損 US$38.2M", "AAOI 還在改善途中"],
            ],
            col_colors={1: "tbl-blue", 2: "tbl-grn"},
        )

        .add_section("四、商業模型差異", level=2)
        .add_mix_bars([
            ("Coherent：資料中心/通訊", 55, "#185FA5", "主要引擎"),
            ("Coherent：工業/材料/其他", 45, "#7F77DD", "分散風險"),
            ("AAOI：Datacenter / CATV", 75, "#1D9E75", "高度集中"),
            ("AAOI：其他", 25, "#888780", "較小"),
        ], title="依公司揭露與業務描述近似呈現")

        .add_reasons([
            ("①", "Coherent 贏在平台廣度",
             "Coherent 不只是 datacenter optics，而是更廣義的 photonics 平台。這讓它在單一產品週期波動時有更強緩衝。",
             "#E6F1FB", "#185FA5", "#185FA5"),
            ("②", "AAOI 贏在小基期彈性",
             "AAOI 2025 全年營收從 2.494 億美元升至 4.557 億美元，顯示當 datacenter optics 拉貨回來時，營收斜率很大。",
             "#EAF3DE", "#3B6D11", "#3B6D11"),
            ("③", "獲利成熟度差距很大",
             "Coherent 已在 30% 中後段毛利率運作，AAOI 則仍在接近損平的過程中，因此 valuation 敘事不能混用。",
             "#EEEDFE", "#533AB7", "#533AB7"),
            ("④", "風格差異比產業差異更重要",
             "這兩家公司都受惠 AI 光連接升級，但 Coherent 更像大型平台股，AAOI 更像高波動成長股，持有邏輯不同。",
             "#FAEEDA", "#BA7517", "#BA7517"),
        ])

        .add_section("五、近期催化")
        .add_timeline([
            ("2026-02-04",
             "<strong>Coherent FY2026 Q2</strong> — 營收 US$1.69B、GAAP 毛利率 36.9%、GAAP EPS US$0.76。",
             "#185FA5"),
            ("2026-02-26",
             "<strong>AAOI 2025Q4 / FY2025</strong> — Q4 營收 US$134.3M、GAAP 毛利率 31.2%、Q1 2026 指引營收 US$150M-165M。",
             "#1D9E75"),
            ("下一步觀察",
             "<strong>800G / 1.6T 光連接放量</strong> — 若 hyperscaler 光模組升級延續，AAOI 彈性較大；若市場更重視平台穩定性，Coherent 較占優。",
             "#854F0B"),
        ])

        .add_section("六、情境判讀")
        .add_scenarios([
            ("平台型配置", "重視規模、毛利與分散度",
             "Coherent 較優", ["平台完整", "毛利較高", "風險較分散"], "#E6F1FB", "#185FA5", "#185FA5"),
            ("高 beta 配置", "重視小公司放量彈性",
             "AAOI 較優", ["基期小", "營收彈性大", "更敏感"], "#EAF3DE", "#3B6D11", "#3B6D11"),
            ("均衡配置", "平台 + 小型成長搭配",
             "Coherent 打底 / AAOI 拉彈性", ["風格互補", "降低單一押注"], "#FAEEDA", "#BA7517", "#854F0B"),
        ])

        .add_disclaimer(
            "本報告使用 Coherent 與 Applied Optoelectronics 官方 Investor Relations / earnings release 公開資訊整理。"
            "由於兩家公司產品結構與營運範圍差異大，文中比較以結構與風格判讀為主。"
        )

        .build()
    )

    return out


def build_marvell_vs_credo_report(output_dir=None):
    """
    產生 Marvell vs Credo 比較報告。

    資料基礎：
    - Marvell：2025-12-02 FY2026 Q3；FY2025 全年
    - Credo：2026-03-02 FY2026 Q3；FY2025 全年
    """

    output_dir = output_dir or default_output_dir()
    os.makedirs(output_dir, exist_ok=True)
    out = os.path.join(output_dir, "Marvell_vs_Credo_比較報告.pdf")

    report = (
        ReportBuilder(out)

        .add_cover(
            title="Marvell vs Credo 比較報告",
            subtitle="AI 互連 / SerDes / Switch / Optical connectivity 對照",
            description="比較 Marvell 與 Credo 在 AI 資料中心互連升級週期中的位置，聚焦規模、毛利率、產品純度與成長斜率。",
            badges=["SerDes", "AEC / optical", "AI connectivity", "官方 IR / 財報"],
            bg_gradient="linear-gradient(140deg,#185FA5 0%,#533AB7 50%,#2C2C2A 100%)",
            border_color="#FAC775",
        )

        .add_key_box(
            heading="核心結論",
            paragraphs=[
                "Marvell 是規模更大的 data infrastructure 公司；Credo 則是更純粹的高速連接 / SerDes / AEC / optical connectivity 標的。",
                "若市場主軸是 AI cluster 內部互連爆發，Credo 通常提供更高純度與更高 beta；若市場看重平台多元度與大客戶滲透，Marvell 論述更完整。",
                "最新季度看，Credo 的增速與毛利率都更漂亮；Marvell 的絕對規模與產品廣度則明顯更大。",
            ],
        )

        .add_section("一、最新季度摘要")
        .add_metric_cards([
            ("Marvell 營收", "US$2.075B", "FY2026 Q3｜2025-12-02 公告", "blue"),
            ("Credo 營收", "US$407.0M", "FY2026 Q3｜2026-03-02 公告", "purple"),
            ("Marvell GAAP 毛利率", "51.6%", "Non-GAAP 59.7%", "amber"),
            ("Credo GAAP 毛利率", "68.5%", "Non-GAAP 68.6%", "green"),
        ])

        .add_section("二、季度數據正面比較", level=2)
        .add_table(
            headers=["指標", "Marvell", "Credo", "觀察"],
            rows=[
                ["最新季度營收", "US$2.075B", "US$407.0M", "Marvell 規模約 5.1 倍"],
                ["年增率", "+37%", "+201.5%", "Credo 斜率極高，基期更小"],
                ["GAAP 毛利率", "51.6%", "68.5%", "Credo 產品純度與輕資產特性明顯"],
                ["Non-GAAP 毛利率", "59.7%", "68.6%", "Credo 毛利結構更佳"],
                ["GAAP / Non-GAAP EPS", "2.20 / 0.76", "0.82 / 1.07", "Marvell GAAP 含業務出售收益；比較要看調整後"],
                ["Q4 指引", "約 US$2.2B", "US$425M-435M", "兩者都延續成長"],
            ],
            col_colors={1: "tbl-blue", 2: "tbl-purple"},
        )

        .add_callout(
            "口徑提醒",
            "Marvell FY2026 Q3 的 GAAP net income 受 automotive ethernet 業務出售收益影響，因此若要比較核心獲利能力，應優先看 Non-GAAP EPS、毛利率與營收成長。",
            "#FAEEDA", "#BA7517", "#FFF8EE", "#BA7517",
        )

        .add_section("三、FY2025 基礎盤", level=2)
        .add_table(
            headers=["FY2025 全年", "Marvell", "Credo", "含意"],
            rows=[
                ["全年營收", "US$5.767B", "US$436.8M", "Marvell 規模大很多"],
                ["Q4 / 年底毛利率", "Q4 GAAP 50.5%", "Q4 GAAP 67.2%", "Credo 結構性高毛利更突出"],
                ["全年成長描述", "AI 資料中心恢復成長", "全年營收年增 126%", "Credo 純度更高、斜率更快"],
                ["風格", "大平台 data infra", "高純度 connectivity", "本質是風格股比較"],
            ],
            col_colors={1: "tbl-blue", 2: "tbl-purple"},
        )

        .add_section("四、商業模型差異", level=2)
        .add_mix_bars([
            ("Marvell：Data Center / AI", 70, "#185FA5", "核心引擎"),
            ("Marvell：其他", 30, "#888780", "多元市場"),
            ("Credo：連接解決方案", 85, "#533AB7", "高度純化"),
            ("Credo：其他", 15, "#7F77DD", "相對小"),
        ], title="依公司揭露與業務描述近似呈現")

        .add_reasons([
            ("①", "Credo 贏在純度與毛利",
             "Credo FY2026 Q3 營收 4.07 億美元、GAAP 毛利率 68.5%，非常適合被市場視為 AI interconnect 高純度標的。",
             "#EEEDFE", "#533AB7", "#533AB7"),
            ("②", "Marvell 贏在規模與產品面",
             "Marvell 不只做互連，也涵蓋更廣的 data infrastructure 產品，因此客戶覆蓋與平台敘事更完整。",
             "#E6F1FB", "#185FA5", "#185FA5"),
            ("③", "Credo 的風險在集中度與波動",
             "純度高意味著一旦 AI cluster 互連需求進一步加速，股價彈性可能很大；但若拉貨節奏變化，波動也通常更高。",
             "#FAEEDA", "#BA7517", "#BA7517"),
            ("④", "Marvell 更像大型 AI infra beta",
             "相較 Credo，Marvell 的成長沒有那麼純，但也不會完全依賴單一互連敘事，因此更像較平衡的大型受惠股。",
             "#EAF3DE", "#3B6D11", "#3B6D11"),
        ])

        .add_section("五、近期催化與指引")
        .add_timeline([
            ("2025-12-02",
             "<strong>Marvell FY2026 Q3</strong> — 營收 US$2.075B、GAAP 毛利率 51.6%、Q4 指引約 US$2.2B。",
             "#185FA5"),
            ("2026-03-02",
             "<strong>Credo FY2026 Q3</strong> — 營收 US$407.0M、GAAP 毛利率 68.5%、Q4 指引 US$425M-435M。",
             "#533AB7"),
            ("下一步觀察",
             "<strong>AEC、光互連與 rack-scale network 滲透率</strong> — 若 AI cluster 互連密度持續上升，Credo 的純度優勢更容易被放大；若市場回到平台化與客戶多元度，Marvell 更有韌性。",
             "#854F0B"),
        ])

        .add_section("六、情境判讀")
        .add_scenarios([
            ("高純度成長", "市場追逐 AI 互連最純標的",
             "Credo 較優", ["高毛利", "高成長", "高 beta"], "#EEEDFE", "#533AB7", "#533AB7"),
            ("平台平衡型", "市場偏好大公司與產品多元度",
             "Marvell 較優", ["規模大", "產品面廣", "客戶基礎更厚"], "#E6F1FB", "#185FA5", "#185FA5"),
            ("雙贏情境", "AI cluster 持續擴張",
             "兩者都受惠", ["Marvell 吃平台面", "Credo 吃純互連"], "#EAF3DE", "#3B6D11", "#3B6D11"),
        ])

        .add_disclaimer(
            "本報告使用 Marvell 與 Credo 官方 Investor Relations / earnings release 公開資訊整理。"
            "兩家公司產品純度與經營範圍差異大，文中比較重點在風格與結構，而非完全同口徑財務對照。"
        )

        .build()
    )

    return out


def build_credo_vs_astera_labs_report(output_dir=None):
    """
    產生 Credo vs Astera Labs 比較報告。

    資料基礎：
    - Credo：2026-03-02 FY2026 Q3；FY2025 全年
    - Astera Labs：2026-02-10 2025Q4 / FY2025
    """

    output_dir = output_dir or default_output_dir()
    os.makedirs(output_dir, exist_ok=True)
    out = os.path.join(output_dir, "Credo_vs_Astera_Labs_比較報告.pdf")

    report = (
        ReportBuilder(out)

        .add_cover(
            title="Credo vs Astera Labs 比較報告",
            subtitle="AI Connectivity 高純度標的對照",
            description="比較 Credo 與 Astera Labs 在 AI 資料中心互連、scale-up fabric、AEC / optical / PCIe / CXL 生態中的定位。",
            badges=["AI connectivity", "AEC / optics", "PCIe / CXL", "官方 IR / 財報"],
            bg_gradient="linear-gradient(140deg,#533AB7 0%,#185FA5 50%,#1D9E75 100%)",
            border_color="#FAC775",
        )

        .add_key_box(
            heading="核心結論",
            paragraphs=[
                "Credo 與 Astera Labs 都是 AI 基礎設施中的高純度 connectivity 標的，但切點不同。Credo 更偏高速連接、SerDes、AEC 與光互連；Astera Labs 更偏 rack-scale connectivity 平台、PCIe / CXL / fabric switch。",
                "最新季度看，Credo 的營收斜率更陡，FY2026 Q3 營收 4.07 億美元、年增 201.5%；Astera Labs 2025Q4 營收 2.706 億美元、年增 92%。",
                "若市場偏好最純 AI interconnect beta，Credo 更直接；若市場偏好具 platform roadmap 與 scale-up fabric 敘事的 AI connectivity 平台，Astera Labs 更完整。",
            ],
        )

        .add_section("一、最新數字摘要")
        .add_metric_cards([
            ("Credo 營收", "US$407.0M", "FY2026 Q3｜2026-03-02 公告", "purple"),
            ("Astera Labs 營收", "US$270.6M", "2025Q4｜2026-02-10 公告", "blue"),
            ("Credo GAAP 毛利率", "68.5%", "Non-GAAP 68.6%", "green"),
            ("Astera GAAP 毛利率", "75.6%", "Non-GAAP 75.7%", "amber"),
        ])

        .add_section("二、季度數據正面比較", level=2)
        .add_table(
            headers=["指標", "Credo", "Astera Labs", "觀察"],
            rows=[
                ["最新季度營收", "US$407.0M", "US$270.6M", "Credo 當前規模略大"],
                ["年增率", "+201.5%", "+92%", "Credo 斜率更陡"],
                ["GAAP 毛利率", "68.5%", "75.6%", "Astera 平台毛利更高"],
                ["Non-GAAP 毛利率", "68.6%", "75.7%", "Astera 結構性毛利優勢明顯"],
                ["GAAP EPS", "US$0.82", "US$0.25", "兩者皆獲利，但口徑與股本不同"],
                ["下一季指引", "US$425M-435M", "US$286M-297M", "兩者都維持成長動能"],
            ],
            col_colors={1: "tbl-purple", 2: "tbl-blue"},
        )

        .add_section("三、FY2025 基礎盤", level=2)
        .add_table(
            headers=["FY2025 全年", "Credo", "Astera Labs", "含意"],
            rows=[
                ["全年營收", "US$436.8M", "US$852.5M", "Astera 平台規模約為 Credo 1.95 倍"],
                ["GAAP 毛利率", "約 64.8%*", "75.7%", "Astera 毛利結構更厚"],
                ["全年獲利", "全年轉盈", "GAAP 淨利 US$219.1M", "Astera 獲利成熟度更高"],
                ["產品路線", "AEC / IC / optical connectivity", "PCIe / CXL / fabric switch", "切入點不同但都吃 AI cluster 升級"],
            ],
            col_colors={1: "tbl-purple", 2: "tbl-blue"},
        )

        .add_callout(
            "註記",
            "Credo FY2025 全年 GAAP 毛利率為依年報/財報 gross profit 與 revenue 近似推算；Astera Labs 則直接揭露全年 GAAP gross margin 75.7%。",
            "#FAEEDA", "#BA7517", "#FFF8EE", "#BA7517",
        )

        .add_section("四、產品與商業模型", level=2)
        .add_mix_bars([
            ("Credo：高速連接 / AEC / optics", 85, "#533AB7", "高純度"),
            ("Credo：其他", 15, "#7F77DD", "相對小"),
            ("Astera：connectivity platform", 70, "#185FA5", "PCIe / CXL / fabric"),
            ("Astera：新 switch / scale-up", 30, "#1D9E75", "Scorpio X-Series"),
        ], title="依公司揭露與業務描述近似呈現")

        .add_reasons([
            ("①", "Credo 贏在 AI interconnect 純度",
             "Credo 最新季度營收年增 201.5%，管理層明確提到 AECs、ICs 與新 TAM 擴張。若市場追逐最純互連 beta，Credo 更直接。",
             "#EEEDFE", "#533AB7", "#533AB7"),
            ("②", "Astera 贏在平台與毛利",
             "Astera 2025Q4 GAAP gross margin 75.6%、全年 75.7%，且 roadmap 已延伸到 Scorpio X-Series smart fabric switch，平台敘事更完整。",
             "#E6F1FB", "#185FA5", "#185FA5"),
            ("③", "Credo 成長更快但波動可能更高",
             "小基期、高純度、高客戶集中度意味著只要 AI cluster 互連加速，Credo 會被放大定價；反過來也代表波動較大。",
             "#FAEEDA", "#BA7517", "#BA7517"),
            ("④", "Astera 更像 AI rack-scale 連接平台",
             "Astera 不只賣單一連接零件，而是把 PCIe、CXL、fabric switch 與系統互連組成平台。這讓它更接近結構性平台股，而非單點零組件股。",
             "#EAF3DE", "#3B6D11", "#3B6D11"),
        ])

        .add_section("五、近期催化")
        .add_timeline([
            ("2026-02-10",
             "<strong>Astera Labs 2025Q4 / FY2025</strong> — Q4 營收 US$270.6M、GAAP 毛利率 75.6%、Q1 指引 US$286M-297M。",
             "#185FA5"),
            ("2026-03-02",
             "<strong>Credo FY2026 Q3</strong> — 營收 US$407.0M、GAAP 毛利率 68.5%、Q4 指引 US$425M-435M。",
             "#533AB7"),
            ("下一步觀察",
             "<strong>Rack-scale AI 系統互連密度是否再升級</strong> — 若重點落在 AEC / optical rollout，Credo 更受惠；若重點落在 scale-up fabric 與平台化互連，Astera 更受惠。",
             "#854F0B"),
        ])

        .add_section("六、情境判讀")
        .add_scenarios([
            ("高 beta 互連行情", "市場追逐最純 AI 互連受惠股",
             "Credo 較優", ["高斜率", "高純度", "高彈性"], "#EEEDFE", "#533AB7", "#533AB7"),
            ("平台型 connectivity 行情", "市場偏好高毛利平台敘事",
             "Astera 較優", ["毛利厚", "平台完整", "switch 路線延伸"], "#E6F1FB", "#185FA5", "#185FA5"),
            ("雙贏情境", "AI rack-scale 資本開支持續擴大",
             "兩者都受惠", ["Credo 吃互連", "Astera 吃平台"], "#EAF3DE", "#3B6D11", "#3B6D11"),
        ])

        .add_disclaimer(
            "本報告使用 Credo 與 Astera Labs 官方 Investor Relations / earnings release 公開資訊整理。"
            "部分年度比較因揭露方式不同含近似推算，已於文中標註。"
        )

        .build()
    )

    return out


def build_coherent_lumentum_aaoi_report(output_dir=None):
    """
    產生 Coherent vs Lumentum vs AAOI 三方比較報告。

    資料基礎：
    - Coherent：2026-02-04 FY2026 Q2；FY2025 全年
    - Lumentum：2026-02-03 FY2026 Q2；FY2025 全年
    - AAOI：2026-02-26 2025Q4 / FY2025
    """

    output_dir = output_dir or default_output_dir()
    os.makedirs(output_dir, exist_ok=True)
    out = os.path.join(output_dir, "Coherent_vs_Lumentum_vs_AAOI_比較報告.pdf")

    report = (
        ReportBuilder(out)

        .add_cover(
            title="Coherent vs Lumentum vs AAOI 比較報告",
            subtitle="光通訊三方相對位置圖",
            description="把三家公司放在同一張圖裡看：平台規模、毛利率、產品廣度與 AI optics 週期彈性各自落在哪裡。",
            badges=["Photonics", "Cloud optics", "平台 vs 斜率", "三方比較"],
            bg_gradient="linear-gradient(140deg,#185FA5 0%,#1D9E75 40%,#533AB7 100%)",
            border_color="#FAC775",
        )

        .add_key_box(
            heading="核心結論",
            paragraphs=[
                "如果把三家公司放在同一條光通訊座標軸上：Coherent 是『大型 photonics 平台』，Lumentum 是『中型但復甦斜率最陡的平台』，AAOI 是『小型高彈性 optics beta』。",
                "規模與穩定度排序大致是 Coherent > Lumentum > AAOI；成長彈性與波動性則通常相反，AAOI 與 Lumentum 更敏感，Coherent 較穩。",
                "投資上不應把三者當成完全同一類股票。這更像平台股、復甦股與高 beta 小型股的風格選擇。",
            ],
        )

        .add_section("一、最新數字一覽")
        .add_metric_cards([
            ("Coherent 營收", "US$1.69B", "FY2026 Q2", "blue"),
            ("Lumentum 營收", "US$665.5M", "FY2026 Q2", "purple"),
            ("AAOI 營收", "US$134.3M", "2025Q4", "green"),
            ("毛利率帶", "36.9% / 36.1% / 31.2%", "Coherent / Lumentum / AAOI", "amber"),
        ])

        .add_section("二、季度數據三方比較", level=2)
        .add_table(
            headers=["指標", "Coherent", "Lumentum", "AAOI"],
            rows=[
                ["最新季度營收", "US$1.69B", "US$665.5M", "US$134.3M"],
                ["年增率", "+17%", "+65.5%", "+33.9%"],
                ["GAAP 毛利率", "36.9%", "36.1%", "31.2%"],
                ["Non-GAAP 毛利率", "39.0%", "42.5%", "31.4%"],
                ["GAAP EPS / 每股", "US$0.76", "US$0.89", "-US$0.03"],
                ["投資風格", "大型平台", "復甦斜率股", "小型高 beta"],
            ],
            col_colors={1: "tbl-blue", 2: "tbl-purple", 3: "tbl-grn"},
        )

        .add_section("三、FY2025 年度基礎盤", level=2)
        .add_table(
            headers=["FY2025 全年", "Coherent", "Lumentum", "AAOI"],
            rows=[
                ["全年營收", "US$5.81B", "US$1.645B", "US$455.7M"],
                ["GAAP 毛利率", "35.2%", "28.0%", "30.0%"],
                ["Non-GAAP 毛利率", "37.9%", "34.7%", "30.9%"],
                ["全年獲利狀態", "Non-GAAP 已成熟", "復甦中已回正", "仍在損平邊緣改善"],
                ["整體定位", "大型 photonics 平台", "Cloud/Networking 平台", "Optics 小型成長股"],
            ],
            col_colors={1: "tbl-blue", 2: "tbl-purple", 3: "tbl-grn"},
        )

        .add_section("四、三方定位圖", level=2)
        .add_scenarios([
            ("Coherent", "大而全 photonics 平台",
             "穩定度最高", ["規模最大", "毛利穩", "業務分散"], "#E6F1FB", "#185FA5", "#185FA5"),
            ("Lumentum", "Cloud optics / systems 復甦",
             "斜率最漂亮", ["營收年增快", "Non-GAAP 毛利強", "平台中型"], "#EEEDFE", "#533AB7", "#533AB7"),
            ("AAOI", "小型 datacenter optics beta",
             "彈性最高", ["基期小", "放量時 beta 高", "波動也最大"], "#EAF3DE", "#3B6D11", "#3B6D11"),
        ])

        .add_mix_bars([
            ("規模穩定度：Coherent", 90, "#185FA5", "最高"),
            ("規模穩定度：Lumentum", 65, "#533AB7", "中等"),
            ("規模穩定度：AAOI", 35, "#1D9E75", "較低"),
            ("彈性 / beta：AAOI", 90, "#1D9E75", "最高"),
            ("彈性 / beta：Lumentum", 75, "#533AB7", "高"),
            ("彈性 / beta：Coherent", 45, "#185FA5", "較低"),
        ], title="以相對風格定位近似呈現")

        .add_reasons([
            ("①", "Coherent 是平台股",
             "規模最大、產品線最廣，適合用『大型光子平台』框架看待，而不是只看單一光模組週期。",
             "#E6F1FB", "#185FA5", "#185FA5"),
            ("②", "Lumentum 是復甦斜率股",
             "FY2026 Q2 營收年增 65.5%、Non-GAAP 毛利率 42.5%，代表產品組合改善與規模效應同步放大。",
             "#EEEDFE", "#533AB7", "#533AB7"),
            ("③", "AAOI 是小型高彈性股",
             "營收規模最小、產品集中度最高，因此一旦雲端 optics 拉貨加速，股價彈性通常最大，但同時波動也最大。",
             "#EAF3DE", "#3B6D11", "#3B6D11"),
            ("④", "三者不能用同一套估值敘事",
             "Coherent 比較像平台與穩定現金流敘事；Lumentum 比較像毛利修復與景氣上行敘事；AAOI 比較像成長 option 敘事。",
             "#FAEEDA", "#BA7517", "#BA7517"),
        ])

        .add_section("五、近期催化")
        .add_timeline([
            ("2026-02-03",
             "<strong>Lumentum FY2026 Q2</strong> — 營收 US$665.5M、GAAP 毛利率 36.1%、Non-GAAP 毛利率 42.5%。",
             "#533AB7"),
            ("2026-02-04",
             "<strong>Coherent FY2026 Q2</strong> — 營收 US$1.69B、GAAP 毛利率 36.9%、GAAP EPS US$0.76。",
             "#185FA5"),
            ("2026-02-26",
             "<strong>AAOI 2025Q4 / FY2025</strong> — Q4 營收 US$134.3M、GAAP 毛利率 31.2%、Q1 指引 US$150M-165M。",
             "#1D9E75"),
            ("下一步觀察",
             "<strong>800G / 1.6T / scale-up optics</strong> — 若 optics 升級持續，三者都受惠，但風格反應會不同：Coherent 較穩、Lumentum 斜率大、AAOI beta 最高。",
             "#854F0B"),
        ])

        .add_section("六、配置思路")
        .add_dupont(
            factors=[("平台穩定度", "Coherent"), ("復甦斜率", "Lumentum"), ("高 beta 彈性", "AAOI")],
            result_label="三方角色",
            result_value="分工明確",
        )

        .add_disclaimer(
            "本報告使用 Coherent、Lumentum 與 Applied Optoelectronics 官方 Investor Relations / earnings release 公開資訊整理。"
            "由於三家公司產品範圍與會計口徑差異大，三方比較重點在相對定位與投資風格。"
        )

        .build()
    )

    return out


def build_silicon_photonics_testing_stocks_report(output_dir=None):
    """
    產生矽光子測試族群個股整理報告。

    名單定位：
    - 直接卡位矽光子/CPO測試設備或介面
    - 測試量測延伸受惠
    - 封測驗證/量產導入受惠
    """

    output_dir = output_dir or default_output_dir()
    os.makedirs(output_dir, exist_ok=True)
    out = os.path.join(output_dir, "矽光子測試族群個股整理.pdf")

    report = (
        ReportBuilder(out)

        .add_cover(
            title="矽光子測試族群個股整理",
            subtitle="台股測試 / 量測 / 封測受惠名單",
            description="聚焦 CPO、矽光子、光電整合量產過程中最可能先受惠的測試介面、設備、量測與封測驗證公司。",
            badges=["SiPh", "CPO", "測試介面", "量測 / 封測"],
            bg_gradient="linear-gradient(140deg,#185FA5 0%,#533AB7 45%,#BA7517 100%)",
            border_color="#1D9E75",
        )

        .add_key_box(
            heading="核心結論",
            paragraphs=[
                "矽光子真正難的不是『能不能做出來』，而是『怎麼大量測、快速測、準確測』。因此先受惠族群通常不是單一光元件商，而是測試介面、量測設備、封測驗證與代工分選業者。",
                "若以台股觀察名單來看，最直接的測試題材大致可分為三層：直接卡位 CPO/矽光子測試設備者、測試介面/量測延伸受惠者，以及封測驗證/量產導入受惠者。",
                "這份名單不是把所有矽光子概念股混在一起，而是只抓『測試』這一段最有機會轉成營收的公司。",
            ],
        )

        .add_section("一、核心名單速覽")
        .add_metric_cards([
            ("直接卡位", "穎崴 6515", "CPO / 晶圓級光學測試介面", "purple"),
            ("設備新秀", "漢測 7856", "矽光子測試設備研發 / 驗證", "blue"),
            ("設備+代工", "惠特 6706", "矽光子設備 / 測試分選", "green"),
            ("封測導入", "矽格 6257", "矽光子晶片測試布局", "amber"),
        ])

        .add_section("二、分層觀察名單", level=2)
        .add_table(
            headers=["層級", "個股", "定位", "目前觀察重點"],
            rows=[
                ["最直接", "穎崴（6515）", "矽光子/CPO 測試介面", "晶圓級光學 CPO 測試方案已獲客戶驗證"],
                ["最直接", "漢測（7856）", "矽光子測試設備", "成立專責團隊，設備研發與驗證推進中"],
                ["直接", "惠特（6706）", "設備 + 系統整合 + 代工測試分選", "DFB/EEL、光纖陣列、光纖貼合量測"],
                ["延伸受惠", "旺矽（6223）", "探針卡 / CPO 測試解決方案", "CPO 測試設備客戶驗證進度"],
                ["延伸受惠", "致茂（2360）", "半導體光子測試 / SLT / 量測", "Photonics 測試解決方案與 AI 測試需求"],
                ["封測受惠", "矽格（6257）", "先進測試 / 矽光子晶片測試", "AI / ASIC / 矽光子測試產能擴充"],
            ],
            col_colors={1: "tbl-purple", 2: "tbl-blue", 3: "tbl-grn"},
        )

        .add_section("三、最值得盯的四檔", level=2)
        .add_reasons([
            ("①", "穎崴（6515）",
             "最像『矽光子測試正宗軍火商』。公司已推出晶圓級矽光子 CPO 測試介面解決方案，重點不只是題材，而是已進入客戶驗證階段，這比單純喊概念更有營收轉換價值。",
             "#EEEDFE", "#533AB7", "#533AB7"),
            ("②", "漢測（7856）",
             "新進但值得追蹤。公司法說明確提到矽光子測試設備將成為未來重要成長動能，且已啟動研發、驗證與專責團隊布局，屬於從 0 到 1 的早期卡位型標的。",
             "#E6F1FB", "#185FA5", "#185FA5"),
            ("③", "惠特（6706）",
             "特色在於不是只做設備，而是走『設備研發製造 + 系統整合 + 代工測試分選』的多元商模。若矽光子導入量產，惠特受惠點比純設備商更多。",
             "#EAF3DE", "#3B6D11", "#3B6D11"),
            ("④", "矽格（6257）",
             "如果矽光子進入穩定量產，最終還是要回到封測與良率。矽格已在法說提到矽光子晶片測試布局，因此它更像中後段量產驗證受惠者。",
             "#FAEEDA", "#BA7517", "#BA7517"),
        ])

        .add_section("四、第二梯隊與延伸名單", level=2)
        .add_callout(
            "旺矽（6223）",
            "市場關注點在高階探針卡與 CPO 測試解決方案。若客戶驗證順利、2026 下半年開始轉營收，題材就可能從『想像』進入『數字』。",
            "#EEEDFE", "#533AB7", "#F5F4FE", "#7F77DD",
        )
        .add_callout(
            "致茂（2360）",
            "比較不像純矽光子股，而是大型量測/測試平台股。優勢在半導體光子測試、SLT 與量測自動化能力，適合當成『測試平台延伸受惠』來看。",
            "#E6F1FB", "#185FA5", "#F4F8FC", "#185FA5",
        )

        .add_section("五、如何區分真受惠與假題材")
        .add_table(
            headers=["判斷題", "要看什麼", "較有價值的答案"],
            rows=[
                ["是否提到『驗證』", "客戶是否已驗證或送樣", "有驗證進度比單講技術更重要"],
                ["是否有『設備/產能』", "新產能、資本支出、交期", "有 CAPEX 與設備到位通常更接近營收"],
                ["是否碰到『量產』", "何時從研發轉量產", "真正業績通常在量產導入後才放大"],
                ["是否有『多元商模』", "設備、介面、代工、封測", "受惠點越多，波動越小"],
            ],
            col_colors={1: "tbl-blue", 2: "tbl-amber"},
        )

        .add_section("六、觀察路徑")
        .add_timeline([
            ("現在到 2026 下半年",
             "<strong>驗證期</strong> — 重點看穎崴、漢測、旺矽、惠特是否出現客戶驗證通過、送樣放量、設備交機等訊號。",
             "#533AB7"),
            ("量產導入期",
             "<strong>設備轉營收</strong> — 真正的差異會出現在單季營收與毛利率是否開始反映矽光子/CPO 訂單。",
             "#185FA5"),
            ("量產擴散期",
             "<strong>封測與分選受惠</strong> — 當矽光子從少量導入走向大規模量產，矽格這類封測與測試產能提供者的重要性才會被放大。",
             "#1D9E75"),
        ])

        .add_section("七、配置思路")
        .add_scenarios([
            ("高純度題材", "最直接卡位矽光子測試",
             "穎崴 / 漢測", ["題材純", "驗證重要", "波動也大"], "#EEEDFE", "#533AB7", "#533AB7"),
            ("商模較完整", "設備 + 代工 + 分選",
             "惠特", ["受惠點多", "轉單季營收機會高"], "#EAF3DE", "#3B6D11", "#3B6D11"),
            ("量產後段受惠", "封測與驗證能量",
             "矽格 / 致茂 / 旺矽", ["較偏平台或後段", "適合中線觀察"], "#FAEEDA", "#BA7517", "#854F0B"),
        ])

        .add_disclaimer(
            "本報告以近期公開新聞與產業資訊整理矽光子『測試』受惠名單，重點在觀察清單與產業位置，不構成投資建議。"
            "部分公司仍處於研發、驗證或早期導入階段，題材與實際營收貢獻未必同步。"
        )

        .build()
    )

    return out


# ─────────────────────────────────────────────
# 主程式
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("AI 水冷散熱供應鏈 — PDF 報告產生器")
    print("=" * 55)

    print("\n[1/10] 產生示範報告...")
    sample = build_sample_report()

    print("\n[2/10] 產生 Coherent vs Lumentum 比較報告...")
    comparison = build_coherent_vs_lumentum_report()

    print("\n[3/10] 產生 Marvell vs Broadcom 比較報告...")
    marvell_broadcom = build_marvell_vs_broadcom_report()

    print("\n[4/10] 產生 AAOI vs Lumentum 比較報告...")
    aaoi_lumentum = build_aaoi_vs_lumentum_report()

    print("\n[5/10] 產生 Broadcom vs NVIDIA networking 比較報告...")
    broadcom_nvidia_networking = build_broadcom_vs_nvidia_networking_report()

    print("\n[6/10] 產生 Coherent vs AAOI 比較報告...")
    coherent_aaoi = build_coherent_vs_aaoi_report()

    print("\n[7/10] 產生 Marvell vs Credo 比較報告...")
    marvell_credo = build_marvell_vs_credo_report()

    print("\n[8/10] 產生 Credo vs Astera Labs 比較報告...")
    credo_astera = build_credo_vs_astera_labs_report()

    print("\n[9/10] 產生 Coherent vs Lumentum vs AAOI 三方比較報告...")
    coherent_lumentum_aaoi = build_coherent_lumentum_aaoi_report()

    print("\n[10/10] 產生矽光子測試族群個股整理...")
    siphone_testing = build_silicon_photonics_testing_stocks_report()

    print("\n完成！輸出檔案：")
    print(f"  {sample}")
    print(f"  {comparison}")
    print(f"  {marvell_broadcom}")
    print(f"  {aaoi_lumentum}")
    print(f"  {broadcom_nvidia_networking}")
    print(f"  {coherent_aaoi}")
    print(f"  {marvell_credo}")
    print(f"  {credo_astera}")
    print(f"  {coherent_lumentum_aaoi}")
    print(f"  {siphone_testing}")

    print("""
─────────────────────────────────────────────────
自訂報告使用方式（ReportBuilder）：

    from pdf_report_generator import ReportBuilder, merge_pdfs

    report = (
        ReportBuilder("my_report.pdf")
        .add_cover("報告標題", "副標題", "說明")
        .add_section("一、章節名稱")
        .add_paragraph("段落內文...")
        .add_metric_cards([
            ("EPS", "47元", "年增119%", "blue"),
            ("毛利率", "18%", "承壓中", "amber"),
        ])
        .add_table(["項目","數值"], [["營收","2483億"]])
        .add_disclaimer()
        .build()
    )

    # 合併多份 PDF
    merge_pdfs(
        ["report1.pdf", "report2.pdf"],
        "combined.pdf",
        title="完整研究報告"
    )
─────────────────────────────────────────────────
""")

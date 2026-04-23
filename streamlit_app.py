#!/usr/bin/env python3
"""Streamlit dashboard for browsing and generating PDF research reports."""

from __future__ import annotations

import base64
import io
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import streamlit as st

import pdf_report_generator as prg


OUTPUT_DIR = Path(prg.default_output_dir())


@dataclass(frozen=True)
class ReportDefinition:
    key: str
    title: str
    category: str
    description: str
    filename: str
    builder: Callable[[str | None], str]


REPORTS = [
    ReportDefinition(
        key="sample",
        title="示範報告｜雙鴻分析",
        category="示範",
        description="展示版 PDF，包含封面、表格、情境卡與時間軸。",
        filename="示範報告_雙鴻分析.pdf",
        builder=prg.build_sample_report,
    ),
    ReportDefinition(
        key="cohr_lite",
        title="Coherent vs Lumentum",
        category="美股兩兩比較",
        description="大型 photonics 平台對中型 cloud optics 平台。",
        filename="Coherent_vs_Lumentum_比較報告.pdf",
        builder=prg.build_coherent_vs_lumentum_report,
    ),
    ReportDefinition(
        key="mrvl_avgo",
        title="Marvell vs Broadcom",
        category="美股兩兩比較",
        description="AI data infrastructure 平台與超大型半導體/軟體平台對照。",
        filename="Marvell_vs_Broadcom_比較報告.pdf",
        builder=prg.build_marvell_vs_broadcom_report,
    ),
    ReportDefinition(
        key="aaoi_lite",
        title="AAOI vs Lumentum",
        category="美股兩兩比較",
        description="小型 optics beta 與中型復甦平台對照。",
        filename="AAOI_vs_Lumentum_比較報告.pdf",
        builder=prg.build_aaoi_vs_lumentum_report,
    ),
    ReportDefinition(
        key="avgo_nvda_net",
        title="Broadcom vs NVIDIA networking",
        category="美股主題比較",
        description="AI networking 平台比較，偏結構與策略位置分析。",
        filename="Broadcom_vs_NVIDIA_networking_比較報告.pdf",
        builder=prg.build_broadcom_vs_nvidia_networking_report,
    ),
    ReportDefinition(
        key="cohr_aaoi",
        title="Coherent vs AAOI",
        category="美股兩兩比較",
        description="大型 photonics 平台與小型高 beta optics 股對照。",
        filename="Coherent_vs_AAOI_比較報告.pdf",
        builder=prg.build_coherent_vs_aaoi_report,
    ),
    ReportDefinition(
        key="mrvl_crdo",
        title="Marvell vs Credo",
        category="美股兩兩比較",
        description="資料中心互連平台與高純度 connectivity 標的對照。",
        filename="Marvell_vs_Credo_比較報告.pdf",
        builder=prg.build_marvell_vs_credo_report,
    ),
    ReportDefinition(
        key="crdo_alab",
        title="Credo vs Astera Labs",
        category="美股兩兩比較",
        description="AI connectivity 高純度標的對照。",
        filename="Credo_vs_Astera_Labs_比較報告.pdf",
        builder=prg.build_credo_vs_astera_labs_report,
    ),
    ReportDefinition(
        key="cohr_lite_aaoi",
        title="Coherent vs Lumentum vs AAOI",
        category="美股三方比較",
        description="光通訊三方相對位置圖，重點是風格與定位。",
        filename="Coherent_vs_Lumentum_vs_AAOI_比較報告.pdf",
        builder=prg.build_coherent_lumentum_aaoi_report,
    ),
    ReportDefinition(
        key="siph_test_tw",
        title="矽光子測試族群個股整理",
        category="台股主題整理",
        description="聚焦矽光子測試、量測、封測與介面受惠名單。",
        filename="矽光子測試族群個股整理.pdf",
        builder=prg.build_silicon_photonics_testing_stocks_report,
    ),
]


def ensure_output_dir() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def report_path(report: ReportDefinition) -> Path:
    return OUTPUT_DIR / report.filename


def file_size_label(path: Path) -> str:
    size_kb = path.stat().st_size / 1024
    if size_kb < 1024:
        return f"{size_kb:.0f} KB"
    return f"{size_kb / 1024:.2f} MB"


def modified_label(path: Path) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(path.stat().st_mtime))


def generate_report(report: ReportDefinition) -> Path:
    ensure_output_dir()
    output = Path(report.builder(str(OUTPUT_DIR)))
    return output


def generate_all_reports() -> list[Path]:
    outputs = []
    for report in REPORTS:
        outputs.append(generate_report(report))
    return outputs


def render_sidebar() -> tuple[str, str]:
    st.sidebar.title("報告中心")
    category = st.sidebar.selectbox(
        "分類",
        ["全部"] + sorted({report.category for report in REPORTS}),
    )
    keyword = st.sidebar.text_input("搜尋", placeholder="例如：Coherent、矽光子、Marvell")
    st.sidebar.markdown("---")
    st.sidebar.caption("輸出目錄")
    st.sidebar.code(str(OUTPUT_DIR))
    return category, keyword.strip().lower()


def render_header() -> None:
    st.set_page_config(
        page_title="PDF 報告中心",
        page_icon="📄",
        layout="wide",
    )
    st.title("PDF 研究報告中心")
    st.caption("整合既有 PDF 報告、支援一鍵重新生成與瀏覽下載。")


def render_actions() -> None:
    left, right = st.columns([1, 1])
    with left:
        if st.button("重新生成全部報告", type="primary", use_container_width=True):
            with st.spinner("正在生成全部 PDF..."):
                outputs = generate_all_reports()
            st.success(f"已完成 {len(outputs)} 份報告生成。")
    with right:
        if st.button("重新掃描輸出目錄", use_container_width=True):
            st.rerun()


def filter_reports(category: str, keyword: str) -> list[ReportDefinition]:
    results = REPORTS
    if category != "全部":
        results = [report for report in results if report.category == category]
    if keyword:
        results = [
            report
            for report in results
            if keyword in report.title.lower()
            or keyword in report.description.lower()
            or keyword in report.category.lower()
            or keyword in report.filename.lower()
        ]
    return results


def render_summary(reports: list[ReportDefinition]) -> None:
    existing = sum(report_path(report).exists() for report in reports)
    c1, c2, c3 = st.columns(3)
    c1.metric("報告數量", len(reports))
    c2.metric("已生成", existing)
    c3.metric("未生成", len(reports) - existing)


def render_pdf_card(report: ReportDefinition) -> None:
    path = report_path(report)
    with st.container(border=True):
        top_left, top_right = st.columns([4, 1])
        with top_left:
            st.subheader(report.title)
            st.caption(f"{report.category}｜{report.filename}")
            st.write(report.description)
        with top_right:
            if st.button("生成", key=f"build-{report.key}", use_container_width=True):
                with st.spinner(f"生成 {report.title}..."):
                    path = generate_report(report)
                st.success(f"已生成：{path.name}")
                st.rerun()

        if path.exists():
            meta1, meta2 = st.columns(2)
            meta1.caption(f"大小：{file_size_label(path)}")
            meta2.caption(f"更新：{modified_label(path)}")

            data = path.read_bytes()
            btn1, btn2 = st.columns([1, 1])
            with btn1:
                st.download_button(
                    "下載 PDF",
                    data=data,
                    file_name=path.name,
                    mime="application/pdf",
                    key=f"download-{report.key}",
                    use_container_width=True,
                )
            with btn2:
                b64 = base64.b64encode(io.BytesIO(data).getvalue()).decode("ascii")
                with st.popover("放大預覽", use_container_width=True):
                    st.markdown(
                        f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="480"></iframe>',
                        unsafe_allow_html=True,
                    )
        else:
            st.warning("尚未生成這份報告。")


def render_report_grid(reports: list[ReportDefinition]) -> None:
    if not reports:
        st.info("沒有符合篩選條件的報告。")
        return

    for idx in range(0, len(reports), 2):
        cols = st.columns(2)
        for col, report in zip(cols, reports[idx:idx + 2]):
            with col:
                render_pdf_card(report)


def main() -> None:
    render_header()
    ensure_output_dir()
    category, keyword = render_sidebar()
    render_actions()
    reports = filter_reports(category, keyword)
    render_summary(reports)
    st.markdown("---")
    render_report_grid(reports)


if __name__ == "__main__":
    main()

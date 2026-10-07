"""
Optional Streamlit dashboard. Run:
    streamlit run analytics/dashboard/app.py
"""
from __future__ import annotations

import asyncio

try:
    import streamlit as st  # type: ignore
except ImportError:  # pragma: no cover
    st = None  # type: ignore

from analytics.reports import full_report


async def _load() -> dict:
    return await full_report()


def main() -> None:
    if st is None:
        print("Streamlit not installed. `pip install streamlit` to use dashboard.")
        return
    st.set_page_config(page_title="techgeo", layout="wide")
    st.title("techgeo — dashboard")
    report = asyncio.run(_load())
    st.subheader("Actions (7d)")
    st.json(report.get("actions_7d", {}))
    st.subheader("Posts by platform")
    st.json(report.get("posts_by_platform", {}))
    st.caption(f"Generated at {report.get('generated_at')}")


if __name__ == "__main__":
    main()

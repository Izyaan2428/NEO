"""Main application entrypoint for NASA Asteroid Tracker (NEO Sentinel)."""

from datetime import datetime, date
from pathlib import Path
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from core.nasa_client import fetch_neo_data, get_scale_comparison
from visualizer.builder import build_visualizer_html

st.set_page_config(
    page_title="NASA Eyes on Asteroids | NEO Sentinel",
    page_icon="☄️",
    layout="wide",
    initial_sidebar_state="expanded"
)


def inject_custom_css():
    css_path = Path("frontend/assets/style.css")
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


inject_custom_css()


def main():
    if "sim_date_input" not in st.session_state:
        st.session_state["sim_date_input"] = datetime.today().date()

    def warp_to_origin():
        st.session_state["sim_date_input"] = date(2005, 11, 18)

    with st.sidebar:
        st.markdown(
            """
            <div style="margin-bottom: 20px;">
                <div style="font-size: 11px; letter-spacing: 2.5px; color: #00f0ff; text-transform: uppercase; font-weight: 700;">NEO SENTINEL</div>
                <div style="font-size: 20px; font-weight: 800; color: #ffffff; letter-spacing: -0.5px; margin-top: 2px;">TEMPORAL CONTROLS</div>
                <div style="font-size: 11px; color: rgba(255,255,255,0.45); margin-top: 4px; letter-spacing: 0.5px;">EPHEMERIS & ARCHIVAL REPLAY</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        selected_date_val = st.date_input(
            "Simulation Date",
            key="sim_date_input",
        )

        st.button(
            "Warp to Origin (Nov 18, 2005)",
            on_click=warp_to_origin,
            use_container_width=True,
        )

        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
        autopilot_toggle = st.toggle("Engage Auto-Pilot (QA Mode)", key="autopilot_toggle", value=False)

    if isinstance(selected_date_val, (list, tuple)):
        selected_date_val = selected_date_val[0]
    if isinstance(selected_date_val, (datetime, date)):
        target_date = selected_date_val.strftime("%Y-%m-%d")
    else:
        target_date = str(selected_date_val)

    df = fetch_neo_data(target_date)

    if df is None or df.empty:
        df = pd.DataFrame([
            {"Name": "SIM-ALPHA", "Diameter (m)": 250, "Velocity (km/h)": 45000, "Miss Distance (km)": 2500000, "Hazardous": True},
            {"Name": "SIM-BETA", "Diameter (m)": 120, "Velocity (km/h)": 28000, "Miss Distance (km)": 14000000, "Hazardous": False}
        ])
        df["Scale Analogy"] = df["Diameter (m)"].apply(get_scale_comparison)
        df["Lunar Distance (LD)"] = df["Miss Distance (km)"] / 384400.0

    with st.sidebar:
        haz_count = int(df["Hazardous"].sum()) if "Hazardous" in df.columns else 0
        ap_badge = '<span style="color:#00f0ff; font-weight:700;">ENGAGED (8s CYCLE)</span>' if autopilot_toggle else '<span style="color:rgba(255,255,255,0.5);">STANDBY</span>'
        st.markdown(
            f"""
            <div style="margin-top: 20px; padding: 14px 16px; background: rgba(18, 22, 36, 0.65); border: 1px solid rgba(0, 240, 255, 0.2); border-radius: 12px; backdrop-filter: blur(12px);">
                <div style="font-size: 10px; letter-spacing: 1.5px; color: #00f0ff; text-transform: uppercase; font-weight: 600; margin-bottom: 8px;">MISSION STATUS</div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 11px; color: rgba(255,255,255,0.7);">TARGET EPOCH</span>
                    <span style="font-size: 12px; font-family: monospace; color: #ffffff; font-weight: 700;">{target_date}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 11px; color: rgba(255,255,255,0.7);">NEOs TRACKED</span>
                    <span style="font-size: 12px; font-family: monospace; color: #00ff88; font-weight: 700;">{len(df)} OBJECTS</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span style="font-size: 11px; color: rgba(255,255,255,0.7);">POTENTIAL THREATS</span>
                    <span style="font-size: 12px; font-family: monospace; color: {'#ff003c' if haz_count > 0 else '#00ff88'}; font-weight: 700;">{haz_count} DETECTED</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 6px; margin-top: 6px;">
                    <span style="font-size: 11px; color: rgba(255,255,255,0.7);">AUTO-PILOT QA</span>
                    <span style="font-size: 11px; font-family: monospace;">{ap_badge}</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    html_content = build_visualizer_html(df, target_date, autopilot_enabled=autopilot_toggle)
    components.html(html_content, height=1000, scrolling=False)


if __name__ == "__main__":
    main()

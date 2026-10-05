from datetime import datetime, date
import os
from pathlib import Path
import json
import requests
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(
    page_title="NASA Eyes on Asteroids | NEO Sentinel",
    page_icon="☄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

FULLSCREEN_OVERRIDE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200');
@import url('https://fonts.googleapis.com/css2?family=Material+Icons');

#MainMenu, footer {
    visibility: hidden !important;
    display: none !important;
}

[data-testid="stToolbar"] {
    display: flex !important;
    background: transparent !important;
    visibility: visible !important;
    height: auto !important;
    pointer-events: none !important;
    position: fixed !important;
    top: 15px !important;
    left: 15px !important;
    z-index: 9999999 !important;
}

[data-testid="stToolbarActions"],
[data-testid="stStatusWidget"],
[data-testid="stToolbarActionButton"],
[data-testid="stToolbar"] [data-testid="stActionButton"],
.stDeployButton {
    display: none !important;
    visibility: hidden !important;
}

[data-testid="stHeader"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    height: 0px !important;
    min-height: 0px !important;
    overflow: visible !important;
    z-index: 99999 !important;
}

header {
    background: transparent !important;
    display: none !important;
}

header:has([data-testid="collapsedControl"]),
header:has([data-testid="stSidebarTrigger"]) {
    display: block !important;
    background: transparent !important;
    border: none !important;
    height: 0px !important;
    min-height: 0px !important;
    overflow: visible !important;
}

[data-testid="stSidebar"] {
    background: rgba(10, 15, 30, 0.85) !important;
    backdrop-filter: blur(24px) !important;
    -webkit-backdrop-filter: blur(24px) !important;
    border-right: 1px solid rgba(0, 240, 255, 0.25) !important;
    box-shadow: 10px 0 35px rgba(0, 0, 0, 0.75) !important;
    z-index: 100 !important;
}

[data-testid="stSidebar"] > div:first-child {
    background: transparent !important;
}

[data-testid="stSidebar"] h1, 
[data-testid="stSidebar"] h2, 
[data-testid="stSidebar"] h3, 
[data-testid="stSidebar"] p, 
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p span,
[data-testid="stSidebar"] label span {
    color: #ffffff !important;
    font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", "Segoe UI", Roboto, sans-serif !important;
}

[data-testid="stSidebar"] label {
    font-size: 11px !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: #00f0ff !important;
    font-weight: 600 !important;
}

[data-testid="stSidebar"] input {
    background: rgba(18, 22, 36, 0.85) !important;
    color: #00f0ff !important;
    border: 1px solid rgba(0, 240, 255, 0.35) !important;
    border-radius: 8px !important;
    font-family: monospace !important;
    font-size: 13px !important;
    padding: 8px 12px !important;
}

[data-testid="stSidebar"] input:focus {
    border-color: #00f0ff !important;
    box-shadow: 0 0 12px rgba(0, 240, 255, 0.5) !important;
}

[data-testid="stSidebar"] button {
    background: rgba(18, 22, 36, 0.7) !important;
    border: 1px solid rgba(0, 240, 255, 0.4) !important;
    color: #ffffff !important;
    border-radius: 9999px !important;
    font-size: 12px !important;
    font-weight: 700 !important;
    letter-spacing: 0.8px !important;
    text-transform: uppercase !important;
    padding: 10px 16px !important;
    transition: all 0.25s ease !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5), inset 0 0 8px rgba(0, 240, 255, 0.1) !important;
}

[data-testid="stSidebar"] button:hover {
    background: rgba(0, 240, 255, 0.2) !important;
    border-color: #00f0ff !important;
    color: #00f0ff !important;
    box-shadow: 0 0 20px rgba(0, 240, 255, 0.5) !important;
    transform: translateY(-1px) !important;
}

[data-testid="stExpandSidebarButton"],
[data-testid="collapsedControl"],
section[data-testid="collapsedControl"],
[data-testid="stSidebarTrigger"] {
    display: flex !important;
    position: fixed !important;
    top: 15px !important;
    left: 15px !important;
    z-index: 99999999 !important;
    pointer-events: auto !important;
    visibility: visible !important;
    opacity: 1 !important;
    background: rgba(10, 15, 30, 0.85) !important;
    backdrop-filter: blur(16px) !important;
    -webkit-backdrop-filter: blur(16px) !important;
    border: 1px solid rgba(0, 240, 255, 0.5) !important;
    border-radius: 8px !important;
    box-shadow: 0 0 20px rgba(0, 240, 255, 0.4), inset 0 0 8px rgba(0, 240, 255, 0.2) !important;
    width: 42px !important;
    height: 42px !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 0 !important;
    cursor: pointer !important;
    transition: all 0.25s ease !important;
}

[data-testid="stExpandSidebarButton"]:hover,
[data-testid="collapsedControl"]:hover,
[data-testid="stSidebarTrigger"]:hover {
    background: rgba(0, 240, 255, 0.25) !important;
    border-color: #00f0ff !important;
    box-shadow: 0 0 25px rgba(0, 240, 255, 0.7) !important;
    transform: scale(1.05) !important;
}

[data-testid="stExpandSidebarButton"] button,
[data-testid="collapsedControl"] button,
[data-testid="stSidebarTrigger"] button {
    background: transparent !important;
    border: none !important;
    color: #00f0ff !important;
    width: 100% !important;
    height: 100% !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    padding: 0 !important;
    pointer-events: auto !important;
}

[data-testid="stSidebarCollapseButton"] {
    display: flex !important;
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
    background: rgba(18, 22, 36, 0.7) !important;
    border: 1px solid rgba(0, 240, 255, 0.4) !important;
    border-radius: 50% !important;
    color: #00f0ff !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
    z-index: 100000 !important;
}

[data-testid="stSidebarCollapseButton"]:hover {
    background: rgba(0, 240, 255, 0.25) !important;
    box-shadow: 0 0 15px rgba(0, 240, 255, 0.6) !important;
}

[data-testid="stExpandSidebarButton"] *, 
[data-testid="collapsedControl"] *, 
section[data-testid="collapsedControl"] *,
[data-testid="stSidebarCollapseButton"] *,
[data-testid="stSidebarTrigger"] * { 
    font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important; 
    color: #00f0ff !important; 
    font-size: 24px !important; 
    font-weight: normal !important;
    font-style: normal !important;
    line-height: 1 !important;
    letter-spacing: normal !important;
    text-transform: none !important;
    display: inline-block !important;
    white-space: nowrap !important;
    word-wrap: normal !important;
    direction: ltr !important;
}

div[data-baseweb="popover"],
div[data-baseweb="calendar"] {
    z-index: 1000 !important;
}
div[data-baseweb="calendar"] {
    background: #0d121f !important;
    border: 1px solid rgba(0, 240, 255, 0.3) !important;
    border-radius: 12px !important;
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.85) !important;
    color: #ffffff !important;
}

[data-testid="stSidebar"] [data-testid="stToggle"] {
    margin-top: 10px !important;
}
[data-testid="stSidebar"] [data-testid="stToggle"] div[role="switch"] {
    background-color: rgba(255, 255, 255, 0.2) !important;
}
[data-testid="stSidebar"] [data-testid="stToggle"] div[role="switch"][aria-checked="true"] {
    background-color: #00f0ff !important;
    box-shadow: 0 0 12px rgba(0, 240, 255, 0.7) !important;
}

.main, .block-container, [data-testid="stAppViewContainer"] {
    padding: 0 !important;
    margin: 0 !important;
    max-width: 100vw !important;
    width: 100vw !important;
    height: 100vh !important;
    height: 100dvh !important;
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    overflow: hidden !important;
    background-color: #000000 !important;
}

iframe {
    position: fixed !important;
    top: 0 !important;
    left: 0 !important;
    width: 100vw !important;
    height: 100vh !important;
    height: 100dvh !important;
    border: none !important;
    display: block !important;
    z-index: 1 !important;
    overflow: hidden !important;
}

@media (max-width: 768px) {
    [data-testid="stSidebar"] {
        width: 100vw !important;
        max-width: 100vw !important;
    }
    [data-testid="stSidebar"] h1 { font-size: 18px !important; }
    [data-testid="stSidebar"] h2 { font-size: 15px !important; }
    [data-testid="stSidebar"] h3 { font-size: 13px !important; }
    [data-testid="stSidebar"] p, 
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] span { font-size: 11px !important; }
    [data-testid="stSidebar"] button { font-size: 11px !important; padding: 8px 12px !important; }

    [data-testid="stExpandSidebarButton"],
    [data-testid="collapsedControl"],
    section[data-testid="collapsedControl"],
    [data-testid="stSidebarTrigger"] {
        top: 12px !important;
        top: max(12px, env(safe-area-inset-top, 12px)) !important;
        left: 12px !important;
        width: 48px !important;
        height: 48px !important;
        min-width: 48px !important;
        min-height: 48px !important;
        z-index: 1000000 !important;
        pointer-events: auto !important;
    }

    [data-testid="stSidebarCollapseButton"] {
        top: 12px !important;
        top: max(12px, env(safe-area-inset-top, 12px)) !important;
        width: 48px !important;
        height: 48px !important;
        min-width: 48px !important;
        min-height: 48px !important;
        z-index: 1000000 !important;
        pointer-events: auto !important;
    }

    #hologram-toggle {
        pointer-events: auto !important;
        cursor: pointer !important;
    }

    #top-nav, .top-nav-container, [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 8px !important;
        justify-content: center !important;
        align-items: center !important;
        max-width: 100vw !important;
        padding: 8px 12px !important;
        font-size: 11px !important;
        top: 12px !important;
        top: max(12px, env(safe-area-inset-top, 12px)) !important;
    }
    #top-nav * {
        font-size: 11px !important;
    }

    .bottom-controls-container, .hud-controls-bar {
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 8px !important;
        align-items: center !important;
        justify-content: center !important;
    }

    #telemetry-drawer {
        width: 100vw !important;
        max-width: 100vw !important;
        bottom: 0 !important;
        right: 0 !important;
        border-radius: 16px 16px 0 0 !important;
        display: flex !important;
        flex-direction: column !important;
    }
    #telemetry-drawer h1 { font-size: 16px !important; }
    #telemetry-drawer h2 { font-size: 14px !important; }
    #telemetry-drawer h3 { font-size: 12px !important; }
    #telemetry-drawer p { font-size: 11px !important; }
    #telemetry-drawer .scale-card {
        display: flex !important;
        flex-direction: column !important;
        width: 100% !important;
    }
    #telemetry-drawer .telemetry-row {
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
        width: 100% !important;
    }
}

@media (max-width: 1024px) {
    #brand-badge, #nav-help {
        display: none !important;
    }
    #top-nav, .top-nav-container, [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 8px !important;
        justify-content: center !important;
        align-items: center !important;
        max-width: 100vw !important;
    }
    .bottom-controls-container, .hud-controls-bar {
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 8px !important;
        align-items: center !important;
        justify-content: center !important;
    }
}
</style>
"""
st.markdown(FULLSCREEN_OVERRIDE_CSS, unsafe_allow_html=True)


def get_scale_comparison(diameter_m: float) -> str:
    if diameter_m is None or pd.isna(diameter_m):
        return "Unknown scale"
    if diameter_m < 15:
        return "School Bus"
    elif diameter_m < 50:
        return "Airplane"
    elif diameter_m < 150:
        return "Football Stadium"
    elif diameter_m < 400:
        return "Skyscraper"
    else:
        return "Burj Khalifa / Mountain"


def get_nasa_api_key() -> str:
    key = os.environ.get("NASA_API_KEY")
    if not key:
        env_file = Path(__file__).parent / ".env"
        if env_file.exists():
            for line in env_file.read_text(encoding="utf-8").splitlines():
                if line.startswith("NASA_API_KEY="):
                    key = line.split("=", 1)[1].strip()
                    break
    return key or "Mw40v36Nf7OrnaUHdylPza4VeFE6iJebhYMeUj1p"


def create_guaranteed_mock_df() -> pd.DataFrame:
    """Fallback simulation dataset when external API is unreachable."""
    records = [
        {"Name": "SIM-ALPHA", "Diameter (m)": 250.0, "Velocity (km/h)": 45000.0, "Miss Distance (km)": 2500000.0, "Hazardous": True},
        {"Name": "SIM-BETA", "Diameter (m)": 120.0, "Velocity (km/h)": 28000.0, "Miss Distance (km)": 14000000.0, "Hazardous": False},
    ]
    df = pd.DataFrame(records)
    df["Scale Analogy"] = df["Diameter (m)"].apply(get_scale_comparison)
    df["Lunar Distance (LD)"] = df["Miss Distance (km)"] / 384400.0
    return df


@st.cache_data(ttl=3600)
def fetch_asteroid_data(target_date: str) -> pd.DataFrame:
    df = None
    try:
        api_key = get_nasa_api_key()
        url = f"https://api.nasa.gov/neo/rest/v1/feed?start_date={target_date}&end_date={target_date}&api_key={api_key}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            neo_by_date = data.get("near_earth_objects", {})
            records = []
            
            for date_str, asteroids in neo_by_date.items():
                for asteroid in asteroids:
                    name = asteroid.get("name")
                    diameter = (
                        asteroid.get("estimated_diameter", {})
                        .get("meters", {})
                        .get("estimated_diameter_max")
                    )
                    cad_list = asteroid.get("close_approach_data", [])
                    velocity = None
                    miss_distance = None
                    if cad_list:
                        cad = cad_list[0]
                        vel_str = cad.get("relative_velocity", {}).get("kilometers_per_hour")
                        miss_str = cad.get("miss_distance", {}).get("kilometers")
                        velocity = float(vel_str) if vel_str is not None else None
                        miss_distance = float(miss_str) if miss_str is not None else None
                        
                    hazardous = bool(asteroid.get("is_potentially_hazardous_asteroid", False))
                    records.append({
                        "Name": name,
                        "Diameter (m)": diameter,
                        "Velocity (km/h)": velocity,
                        "Miss Distance (km)": miss_distance,
                        "Hazardous": hazardous
                    })
                    
            if records:
                df = pd.DataFrame(records)
                df["Scale Analogy"] = df["Diameter (m)"].apply(get_scale_comparison)
                df["Lunar Distance (LD)"] = df["Miss Distance (km)"] / 384400.0
    except Exception:
        df = None

    # Fallback dataset if API fails or returns no records
    if df is None or df.empty:
        df = pd.DataFrame([
            {"Name": "SIM-ALPHA", "Diameter (m)": 250, "Velocity (km/h)": 45000, "Miss Distance (km)": 2500000, "Hazardous": True},
            {"Name": "SIM-BETA", "Diameter (m)": 120, "Velocity (km/h)": 28000, "Miss Distance (km)": 14000000, "Hazardous": False}
        ])
        df["Scale Analogy"] = df["Diameter (m)"].apply(get_scale_comparison)
        df["Lunar Distance (LD)"] = df["Miss Distance (km)"] / 384400.0

    return df


CINEMATIC_THREEJS_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=no">
  <title>NASA Eyes on Asteroids</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }
    html, body {
      width: 100vw !important;
      height: 100vh !important;
      height: 100dvh !important;
      position: fixed !important;
      top: 0 !important;
      left: 0 !important;
      overflow: hidden !important;
      background: #000000;
      color: #ffffff;
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", "Segoe UI", Roboto, sans-serif;
      user-select: none;
      -webkit-user-select: none;
      touch-action: none;
    }

    #canvas-container {
      width: 100vw !important;
      height: 100vh !important;
      height: 100dvh !important;
      position: fixed !important;
      top: 0 !important;
      left: 0 !important;
      overflow: hidden !important;
      z-index: 1;
      background: #000000;
      touch-action: none;
    }

    #canvas-container canvas {
      width: 100vw !important;
      height: 100vh !important;
      height: 100dvh !important;
      position: fixed !important;
      top: 0 !important;
      left: 0 !important;
      display: block !important;
    }

    .glass-pill {
      background: rgba(18, 22, 32, 0.65);
      border: 1px solid rgba(255, 255, 255, 0.16);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.65), inset 0 0 12px rgba(255, 255, 255, 0.05);
      border-radius: 9999px;
    }

    #top-nav, .top-nav-container, [data-testid="stHorizontalBlock"] {
      position: absolute;
      top: 20px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 10;
      padding: 10px 22px;
      display: flex;
      align-items: center;
      gap: 14px;
      font-size: 13px;
      letter-spacing: 0.5px;
      max-width: 90vw;
      box-sizing: border-box;
      flex-wrap: wrap !important;
      justify-content: center !important;
      pointer-events: none;
    }
    #top-nav * {
      pointer-events: none;
    }
    .status-beacon {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #00ff88;
      box-shadow: 0 0 10px #00ff88;
      animation: pulse-beacon 2s infinite;
    }
    @keyframes pulse-beacon {
      0% { opacity: 0.4; }
      50% { opacity: 1; transform: scale(1.15); }
      100% { opacity: 0.4; }
    }
    .brand-title {
      font-weight: 700;
      color: #ffffff;
      letter-spacing: 1px;
    }
    .nav-sep {
      color: rgba(255, 255, 255, 0.25);
    }
    .nav-meta {
      color: rgba(255, 255, 255, 0.85);
      font-variant-numeric: tabular-nums;
    }

    #brand-badge {
      position: absolute;
      top: 18px;
      left: 70px;
      z-index: 10;
      font-size: 11px;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: rgba(255, 255, 255, 0.6);
      cursor: pointer;
      pointer-events: auto !important;
      user-select: none;
      transition: all 0.25s ease;
    }
    #brand-badge:hover strong {
      color: #ffffff;
      text-shadow: 0 0 10px #00f0ff;
    }
    #brand-badge strong {
      color: #00f0ff;
      display: block;
      font-size: 13px;
      letter-spacing: 2.5px;
      margin-bottom: 2px;
    }

    .bottom-controls-container, .hud-controls-bar {
      position: absolute;
      bottom: 28px;
      left: 28px;
      z-index: 10;
      display: flex !important;
      flex-direction: row !important;
      flex-wrap: wrap !important;
      gap: 8px !important;
      align-items: center !important;
      justify-content: center !important;
      pointer-events: none;
    }

    #reset-control {
      position: relative;
      padding: 10px 20px;
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 12px;
      font-weight: 600;
      letter-spacing: 0.5px;
      cursor: pointer;
      color: rgba(255, 255, 255, 0.9);
      transition: all 0.25s ease;
      pointer-events: auto !important;
      white-space: nowrap !important;
    }
    #reset-control:hover {
      background: rgba(30, 36, 52, 0.85);
      border-color: rgba(0, 240, 255, 0.5);
      color: #00f0ff;
      transform: translateY(-2px);
    }

    #hud-sidebar-toggle {
      position: relative;
      padding: 10px 18px;
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.8px;
      color: #00f0ff;
      border: 1px solid rgba(0, 240, 255, 0.45);
      cursor: pointer;
      pointer-events: auto !important;
      transition: all 0.25s ease;
      user-select: none;
      white-space: nowrap !important;
    }
    #hud-sidebar-toggle:hover {
      background: rgba(0, 240, 255, 0.25);
      border-color: #00f0ff;
      box-shadow: 0 0 20px rgba(0, 240, 255, 0.6);
      transform: translateY(-2px);
    }

    #nav-help {
      position: absolute;
      bottom: 30px;
      left: 50%;
      transform: translateX(-50%);
      z-index: 10;
      font-size: 11px;
      color: rgba(255, 255, 255, 0.45);
      letter-spacing: 1px;
      pointer-events: none;
    }

    #telemetry-drawer {
      position: absolute;
      top: 0;
      right: -450px;
      width: 350px;
      max-width: 90vw;
      height: 100vh;
      transition: right 0.5s cubic-bezier(0.16, 1, 0.3, 1);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      background: rgba(10, 15, 30, 0.75);
      border-left: 1px solid rgba(0, 240, 255, 0.3);
      box-shadow: -15px 0 45px rgba(0, 0, 0, 0.75);
      z-index: 100;
      padding: 24px 20px;
      font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "Inter", "Segoe UI", Roboto, sans-serif;
      color: white;
      display: flex;
      flex-direction: column;
      box-sizing: border-box;
      overflow-y: auto;
      pointer-events: auto;
    }
    #telemetry-drawer .close-btn, #telemetry-drawer button { pointer-events: auto !important; cursor: pointer !important; z-index: 1000000 !important; position: relative; }
    .drawer-close {
      position: absolute !important;
      top: 20px !important;
      right: 20px !important;
      width: 48px !important;
      height: 48px !important;
      min-width: 48px !important;
      min-height: 48px !important;
      border-radius: 50% !important;
      display: flex !important;
      align-items: center !important;
      justify-content: center !important;
      background: rgba(255, 255, 255, 0.12) !important;
      border: 1px solid rgba(0, 240, 255, 0.4) !important;
      cursor: pointer !important;
      color: #ffffff !important;
      font-size: 24px !important;
      line-height: 1 !important;
      transition: all 0.2s ease !important;
      pointer-events: auto !important;
      z-index: 1000000 !important;
    }
    .drawer-close:hover, #telemetry-drawer .close-btn:hover {
      background: rgba(255, 0, 60, 0.3) !important;
      border-color: #ff003c !important;
      color: #ffffff !important;
    }
    .target-tag {
      font-size: 10px;
      letter-spacing: 2px;
      text-transform: uppercase;
      color: #00f0ff;
      margin-bottom: 6px;
    }
    .target-name {
      font-size: 24px;
      font-weight: 800;
      letter-spacing: -0.5px;
      margin-bottom: 12px;
      color: #ffffff;
    }
    .threat-pill {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 5px 12px;
      border-radius: 9999px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.5px;
      margin-bottom: 24px;
      align-self: flex-start;
    }
    .threat-safe {
      background: rgba(0, 240, 255, 0.12);
      border: 1px solid #00f0ff;
      color: #00f0ff;
    }
    .threat-hazard {
      background: rgba(255, 0, 60, 0.18);
      border: 1px solid #ff003c;
      color: #ff003c;
      box-shadow: 0 0 15px rgba(255, 0, 60, 0.35);
    }
    
    .scale-card {
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.08);
      border-radius: 12px;
      padding: 18px;
      margin-bottom: 24px;
    }
    .scale-card-title {
      font-size: 10px;
      letter-spacing: 1.5px;
      text-transform: uppercase;
      color: rgba(255, 255, 255, 0.5);
      margin-bottom: 8px;
    }
    .scale-analogy-text {
      font-size: 14px;
      font-weight: 600;
      color: #ffcc00;
      margin-bottom: 10px;
    }
    .silhouette-canvas {
      width: 100%;
      height: 70px;
      display: flex;
      align-items: flex-end;
      gap: 16px;
      padding-top: 10px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
    }

    #hologram-toggle {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 9px 14px;
      margin-top: 14px;
      background: rgba(0, 240, 255, 0.08);
      border: 1px solid rgba(0, 240, 255, 0.35);
      border-radius: 8px;
      font-size: 11px;
      font-weight: 700;
      letter-spacing: 0.8px;
      color: #00f3ff;
      cursor: pointer;
      pointer-events: auto !important;
      transition: all 0.25s ease;
      user-select: none;
      box-shadow: 0 0 12px rgba(0, 240, 255, 0.12);
    }
    #hologram-toggle:hover {
      background: rgba(0, 240, 255, 0.18);
      border-color: #00f3ff;
      box-shadow: 0 0 18px rgba(0, 240, 255, 0.35);
      transform: translateY(-1px);
    }
    #hologram-toggle.disabled {
      background: rgba(255, 255, 255, 0.04);
      border-color: rgba(255, 255, 255, 0.12);
      color: rgba(255, 255, 255, 0.4);
      box-shadow: none;
    }
    #hologram-toggle .toggle-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #00f3ff;
      box-shadow: 0 0 8px #00f3ff;
      transition: all 0.25s ease;
      display: inline-block;
    }
    #hologram-toggle.disabled .toggle-dot {
      background: rgba(255, 255, 255, 0.25);
      box-shadow: none;
    }

    .telemetry-row {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      padding: 10px 0;
      border-bottom: 1px solid rgba(255, 255, 255, 0.06);
    }
    .telemetry-label {
      font-size: 12px;
      color: rgba(255, 255, 255, 0.55);
      letter-spacing: 0.5px;
    }
    .telemetry-value {
      font-size: 14px;
      font-weight: 600;
      color: #ffffff;
      font-variant-numeric: tabular-nums;
    }

    #hover-tooltip {
      position: absolute;
      display: none;
      z-index: 15;
      padding: 6px 12px;
      background: rgba(10, 14, 22, 0.85);
      border: 1px solid rgba(255, 255, 255, 0.2);
      border-radius: 6px;
      font-size: 11px;
      font-weight: 600;
      letter-spacing: 0.5px;
      pointer-events: none;
      backdrop-filter: blur(10px);
      box-shadow: 0 4px 16px rgba(0, 0, 0, 0.5);
      transform: translate(12px, -12px);
    }

    #targeting-reticle {
      position: absolute;
      top: -9999px;
      left: -9999px;
      transform: translate(-50%, -50%);
      width: 220px;
      height: 220px;
      pointer-events: none;
      z-index: 12;
      opacity: 0;
      transition: opacity 0.4s ease;
      display: none;
    }
    #targeting-reticle.active {
      opacity: 0.85;
      display: block;
    }
    @media (max-width: 820px) {
      #targeting-reticle {
        width: 170px;
        height: 170px;
      }
    }
    .reticle-outer-ring {
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      border-radius: 50%;
      border: 1px dashed rgba(0, 240, 255, 0.45);
      animation: spin-reticle 24s linear infinite;
      box-sizing: border-box;
    }
    .reticle-inner-ring {
      position: absolute;
      top: 12.5%;
      left: 12.5%;
      width: 75%;
      height: 75%;
      border-radius: 50%;
      border: 1px dotted rgba(0, 240, 255, 0.35);
      animation: counter-spin-reticle 14s linear infinite;
      box-sizing: border-box;
    }
    .reticle-bracket {
      position: absolute;
      width: 20px;
      height: 20px;
      border-color: #00f0ff;
      border-style: solid;
      box-sizing: border-box;
    }
    .reticle-bracket.tl { top: 0; left: 0; border-width: 2px 0 0 2px; }
    .reticle-bracket.tr { top: 0; right: 0; border-width: 2px 2px 0 0; }
    .reticle-bracket.bl { bottom: 0; left: 0; border-width: 0 0 2px 2px; }
    .reticle-bracket.br { bottom: 0; right: 0; border-width: 0 2px 2px 0; }
    
    .reticle-tag {
      position: absolute;
      bottom: -28px;
      left: 50%;
      transform: translateX(-50%);
      font-family: monospace;
      font-size: 10px;
      letter-spacing: 2px;
      color: #00f0ff;
      white-space: nowrap;
      text-shadow: 0 0 8px rgba(0, 240, 255, 0.7);
    }

    #targeting-reticle.hazard .reticle-outer-ring {
      border-color: rgba(255, 0, 60, 0.55);
    }
    #targeting-reticle.hazard .reticle-inner-ring {
      border-color: rgba(255, 0, 60, 0.45);
    }
    #targeting-reticle.hazard .reticle-bracket {
      border-color: #ff003c;
    }
    #targeting-reticle.hazard .reticle-tag {
      color: #ff003c;
      text-shadow: 0 0 8px rgba(255, 0, 60, 0.7);
    }

    @keyframes spin-reticle {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
    @keyframes counter-spin-reticle {
      from { transform: rotate(360deg); }
      to { transform: rotate(0deg); }
    }

    @media (max-width: 1024px) {
      #brand-badge, #nav-help {
        display: none !important;
      }
      #top-nav, .top-nav-container, [data-testid="stHorizontalBlock"] {
        flex-wrap: wrap !important;
        gap: 8px !important;
        justify-content: center !important;
        align-items: center !important;
        max-width: 96vw !important;
      }
      .bottom-controls-container, .hud-controls-bar {
        bottom: 20px !important;
        left: 20px !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 8px !important;
        align-items: center !important;
        justify-content: flex-start !important;
      }
    }

    @media (max-width: 768px) {
      #brand-badge { display: none !important; }
      #nav-help { display: none !important; }

      /* Top Navigation Pill */
      #top-nav {
        flex-direction: row !important;
        flex-wrap: wrap !important;
        justify-content: center !important;
        align-items: center !important;
        padding: 8px 12px !important;
        font-size: 11px !important;
        gap: 6px !important;
        top: 12px !important;
        top: max(12px, env(safe-area-inset-top, 12px)) !important;
        width: 92vw !important;
        max-width: 92vw !important;
        box-sizing: border-box !important;
        pointer-events: none !important;
        left: 50% !important;
        transform: translateX(-50%) !important;
      }
      #top-nav span,
      #top-nav div,
      .brand-title,
      .nav-meta {
        font-size: 11px !important;
      }
      #top-nav .nav-sep {
        font-size: 9px !important;
        margin: 0 1px !important;
      }

      /* Telemetry Drawer: fluid responsive bottom sheet modal with single-column vertical stacking */
      #telemetry-drawer {
        width: 100vw !important;
        max-width: 100vw !important;
        bottom: 0 !important;
        right: 0 !important;
        left: 0 !important;
        top: auto !important;
        height: auto !important;
        max-height: 80vh !important;
        max-height: 80dvh !important;
        border-radius: 16px 16px 0 0 !important;
        border-left: none !important;
        border-top: 1px solid rgba(0, 240, 255, 0.4) !important;
        backdrop-filter: blur(28px) !important;
        -webkit-backdrop-filter: blur(28px) !important;
        background: rgba(10, 15, 30, 0.96) !important;
        padding: 24px 18px 30px 18px !important;
        box-sizing: border-box !important;
        box-shadow: 0 -12px 40px rgba(0, 0, 0, 0.85) !important;
        transform: translateY(100%);
        transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.3s ease !important;
        opacity: 0;
        pointer-events: none;
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch !important;
        z-index: 100000 !important;
        display: flex !important;
        flex-direction: column !important;
      }

      #telemetry-drawer.open,
      #telemetry-drawer[style*="right: 0px"],
      #telemetry-drawer[style*="right:0px"] {
        transform: translateY(0%) !important;
        opacity: 1 !important;
        pointer-events: auto !important;
      }

      /* Mobile typography scaling: >= 30% reduction to prevent text overflow */
      #telemetry-drawer h1 { font-size: 16px !important; }
      #telemetry-drawer h2 { font-size: 14px !important; }
      #telemetry-drawer h3 { font-size: 12px !important; }
      #telemetry-drawer p { font-size: 11px !important; }
      #telemetry-drawer .target-tag { font-size: 8px !important; letter-spacing: 1.5px !important; }
      #telemetry-drawer .target-name { font-size: 18px !important; margin-bottom: 8px !important; }
      #telemetry-drawer .threat-pill { font-size: 9.5px !important; padding: 4px 8px !important; margin-bottom: 14px !important; }
      
      /* Single-column vertical stacking across all telemetry cards */
      #telemetry-drawer .scale-card {
        padding: 12px !important;
        margin-bottom: 14px !important;
        display: flex !important;
        flex-direction: column !important;
        width: 100% !important;
        box-sizing: border-box !important;
      }
      #telemetry-drawer .scale-card-title { font-size: 8.5px !important; }
      #telemetry-drawer .scale-analogy-text { font-size: 11px !important; margin-bottom: 6px !important; }
      #telemetry-drawer .silhouette-canvas { height: 50px !important; width: 100% !important; }
      #telemetry-drawer .telemetry-label { font-size: 9.5px !important; letter-spacing: 0.3px !important; width: 100% !important; text-align: left !important; }
      #telemetry-drawer .telemetry-value { font-size: 11.5px !important; width: 100% !important; text-align: left !important; }
      #telemetry-drawer #hologram-toggle { padding: 8px 12px !important; font-size: 10px !important; margin-top: 10px !important; }

      /* Data Readouts single column flex layout */
      .telemetry-row {
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
        width: 100% !important;
        box-sizing: border-box !important;
        padding: 6px 0 !important;
        gap: 2px !important;
      }

      /* Minimum 48px x 48px interactive touch targets */
      .drawer-close,
      #telemetry-drawer .close-btn,
      #telemetry-drawer button {
        width: 48px !important;
        height: 48px !important;
        min-width: 48px !important;
        min-height: 48px !important;
        top: 14px !important;
        right: 14px !important;
        font-size: 26px !important;
        pointer-events: auto !important;
        z-index: 1000000 !important;
        cursor: pointer !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
      }

      .bottom-controls-container, .hud-controls-bar {
        bottom: 16px !important;
        bottom: max(16px, env(safe-area-inset-bottom, 16px)) !important;
        left: 14px !important;
        flex-direction: row !important;
        flex-wrap: wrap !important;
        gap: 8px !important;
      }

      #reset-control, #hud-sidebar-toggle {
        position: relative !important;
        bottom: auto !important;
        left: auto !important;
        min-width: 48px !important;
        min-height: 48px !important;
        padding: 10px 14px !important;
        font-size: 11px !important;
        pointer-events: auto !important;
        z-index: 1000000 !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
      }

      #targeting-reticle {
        width: 120px !important;
        height: 120px !important;
        pointer-events: none !important;
      }
    }
  </style>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js"></script>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/tween.js/18.6.4/tween.umd.js"></script>
</head>
<body>
  <div id="canvas-container"></div>

  <div id="top-nav" class="glass-pill top-nav-container">
    <div class="status-beacon"></div>
    <span class="brand-title">NASA EYES ON ASTEROIDS</span>
    <span class="nav-sep">•</span>
    <span class="nav-meta">DATE: <span id="display-date">__TARGET_DATE__</span></span>
    <span class="nav-sep">•</span>
    <span class="nav-meta"><span id="tracked-count">__TRACKED_COUNT__</span> TRACKED</span>
    <span id="autopilot-nav-badge" style="display: none; color: #00f0ff; font-weight: 700; font-size: 11px; letter-spacing: 1px; border: 1px solid rgba(0,240,255,0.6); padding: 2px 8px; border-radius: 9999px; background: rgba(0,240,255,0.15);">AUTO-PILOT QA</span>
  </div>

  <div id="brand-badge" onclick="toggleMissionControls()" title="Click to Toggle Mission Controls Sidebar">
    <strong>NEO SENTINEL</strong>
    DEEP SPACE TRAJECTORY VISUALIZER
  </div>

  <div class="bottom-controls-container hud-controls-bar" id="bottom-controls">
    <div id="reset-control" class="glass-pill" onclick="resetToEarthView()">
      <span>🌍</span>
      <span>RESET VIEW (ESC)</span>
    </div>

    <div id="hud-sidebar-toggle" class="glass-pill" onclick="toggleMissionControls()" title="Click to Toggle Mission Controls Sidebar">
      <span>☰</span>
      <span>CONTROLS</span>
    </div>
  </div>

  <div id="nav-help">
    DRAG TO ORBIT // SCROLL TO ZOOM // CLICK ASTEROID TO FLY IN
  </div>

  <div id="hover-tooltip"></div>

  <div id="targeting-reticle">
    <div class="reticle-outer-ring"></div>
    <div class="reticle-inner-ring"></div>
    <div class="reticle-bracket tl"></div>
    <div class="reticle-bracket tr"></div>
    <div class="reticle-bracket bl"></div>
    <div class="reticle-bracket br"></div>
    <div class="reticle-tag" id="reticle-status">TARGET LOCK: ACTIVE</div>
  </div>

  <div id="telemetry-drawer">
    <button class="drawer-close close-btn" id="drawer-close-btn" onclick="resetToEarthView()" aria-label="Close drawer">×</button>
    <div class="target-tag">TARGET TELEMETRY</div>
    <div class="target-name" id="drawer-name">---</div>
    <div id="drawer-threat" class="threat-pill">---</div>

    <div class="scale-card">
      <div class="scale-card-title">HUMAN-SCALE PHYSICAL COMPARISON</div>
      <div class="scale-analogy-text" id="drawer-scale">---</div>
      <div class="silhouette-canvas" id="drawer-silhouette"></div>
      <div id="hologram-toggle" class="hologram-toggle-btn" onclick="toggleHologram()" title="Toggle 3D Holographic Landmark Scale in Scene">
        <span class="toggle-dot"></span>
        <span class="toggle-label">3D HOLO COMPARISON: ON</span>
      </div>
    </div>

    <div class="telemetry-row">
      <span class="telemetry-label">ESTIMATED DIAMETER</span>
      <span class="telemetry-value" id="drawer-diameter">---</span>
    </div>
    <div class="telemetry-row">
      <span class="telemetry-label">RELATIVE VELOCITY</span>
      <span class="telemetry-value" id="drawer-velocity">---</span>
    </div>
    <div class="telemetry-row">
      <span class="telemetry-label">CLOSE APPROACH (MISS DISTANCE)</span>
      <span class="telemetry-value" id="drawer-distance">---</span>
    </div>
    <div class="telemetry-row">
      <span class="telemetry-label">LUNAR PROXIMITY (LD)</span>
      <span class="telemetry-value" id="drawer-ld">---</span>
    </div>
    <div class="telemetry-row">
      <span class="telemetry-label">ORBITAL INCLINATION</span>
      <span class="telemetry-value" id="drawer-inc">---</span>
    </div>
  </div>

  <script>
    const AUTO_PILOT_ENABLED = __AUTO_PILOT_ENABLED__;
    let asteroidData = [];
    try {
      asteroidData = JSON.parse(String.raw`__ASTEROID_DATA_JSON__`);
    } catch (e) {
      asteroidData = [];
    }

    if (!asteroidData || asteroidData.length === 0) {
      asteroidData = [
        {"Name": "SIM-ALPHA", "Diameter (m)": 250, "Velocity (km/h)": 45000, "Miss Distance (km)": 2500000, "Hazardous": true, "Scale Analogy": "Eiffel Tower scale", "Lunar Distance (LD)": 6.5},
        {"Name": "SIM-BETA", "Diameter (m)": 120, "Velocity (km/h)": 28000, "Miss Distance (km)": 14000000, "Hazardous": false, "Scale Analogy": "Football Stadium scale", "Lunar Distance (LD)": 36.4}
      ];
    }

    // Initialize Three.js engine
    try {
      console.log("NEO Sentinel Engine Initialized. Loaded asteroids:", asteroidData ? asteroidData.length : 0);

      const trackedCountEl = document.getElementById('tracked-count');
      if (trackedCountEl) {
        trackedCountEl.innerText = asteroidData ? asteroidData.length : 0;
      }

      const container = document.getElementById('canvas-container');
      if (!container) throw new Error("Mounting container #canvas-container does not exist.");

      const tooltip = document.getElementById('hover-tooltip');
      const drawer = document.getElementById('telemetry-drawer');

      // Scene, camera, and renderer setup
      const scene = new THREE.Scene();
      scene.background = new THREE.Color(0x000000);

      // Procedural Holographic Scale Comparison Landmark System
      const hologramGroup = new THREE.Group();
      hologramGroup.name = "hologramGroup";
      hologramGroup.visible = false;
      scene.add(hologramGroup);

      const hologramMaterial = new THREE.LineBasicMaterial({
        color: 0x00f3ff,
        transparent: true,
        opacity: 0.85,
        blending: THREE.AdditiveBlending,
        depthWrite: false
      });
      window.hologramMaterial = hologramMaterial;
      let hologramEnabled = true;

      const width = window.innerWidth || 1200;
      const height = window.innerHeight || 800;

      const camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 15000);
      const defaultCamPos = new THREE.Vector3(38, 20, 46);
      camera.position.copy(defaultCamPos);

      const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: "high-performance" });
      renderer.setSize(width, height);
      renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = 1.0;
      container.appendChild(renderer.domElement);

      const controls = new THREE.OrbitControls(camera, renderer.domElement);
      controls.enableDamping = true;
      controls.dampingFactor = 0.05;
      controls.minDistance = 14;
      controls.maxDistance = 400;

      // 1. ARCHITECTURAL HIERARCHY (The Sun Group)
      const sunPosition = new THREE.Vector3(1200, 400, -1200);
      const sunGroup = new THREE.Group();
      sunGroup.position.copy(sunPosition);
      scene.add(sunGroup);

      // 2. PART A: THE SOLID OCCLUDER CORE (Blinding white emissive core)
      const coreGeo = new THREE.SphereGeometry(120, 32, 32);
      const coreMat = new THREE.MeshBasicMaterial({
        color: 0xffffff,
        emissive: 0xffffff,
        emissiveIntensity: 2.5,
        depthWrite: true,
        depthTest: true
      });
      const sunCore = new THREE.Mesh(coreGeo, coreMat);
      sunGroup.add(sunCore);

      // 3. PART B: THE PROCEDURAL GLOW CORONA (Additive Atmosphere)
      function createSunCanvasTexture() {
        const c = document.createElement('canvas');
        c.width = 2048;
        c.height = 2048;
        const ctx = c.getContext('2d');

        const cx = 1024;
        const cy = 1024;
        const maxR = 1024;

        const grad = ctx.createRadialGradient(cx, cy, 0, cx, cy, maxR);

        // Core (0% to 15% radius): Pure blinding white (#ffffff at opacity 1.0)
        grad.addColorStop(0.0, 'rgba(255, 255, 255, 1.0)');
        grad.addColorStop(0.10, 'rgba(255, 255, 255, 1.0)');
        grad.addColorStop(0.15, 'rgba(255, 255, 255, 1.0)');

        // Photosphere (15% to 50% radius): Bright yellow-orange (#ffaa22 transitioning with exponential curve Math.pow(1 - r, 2) to simulate limb darkening)
        const photoSteps = 16;
        for (let i = 1; i <= photoSteps; i++) {
          const t = i / photoSteps;
          const r = 0.15 + t * 0.35;
          const f = Math.pow(1.0 - t, 2.0);
          const g = Math.round(170 + (255 - 170) * f);
          const b = Math.round(34 + (255 - 34) * Math.pow(f, 1.5));
          const a = 1.0 - 0.25 * (1.0 - f);
          grad.addColorStop(Number(r.toFixed(4)), `rgba(255, ${g}, ${b}, ${a.toFixed(3)})`);
        }

        // Corona (50% to 100% radius): Deep solar red-orange fading smoothly to absolute zero opacity rgba(255, 60, 0, 0)
        const coronaSteps = 20;
        for (let j = 1; j <= coronaSteps; j++) {
          const u = j / coronaSteps;
          const r = 0.50 + u * 0.50;
          const falloff = Math.pow(1.0 - u, 2.5);
          const g = Math.round(60 + (170 - 60) * (1.0 - u));
          const a = 0.75 * falloff;
          grad.addColorStop(Number(r.toFixed(4)), `rgba(255, ${g}, 0, ${a.toFixed(4)})`);
        }

        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, 2048, 2048);

        const tex = new THREE.CanvasTexture(c);
        tex.needsUpdate = true;
        return tex;
      }

      const canvasTexture = createSunCanvasTexture();
      const coronaGeo = new THREE.PlaneGeometry(1600, 1600);
      const coronaMat = new THREE.MeshBasicMaterial({
        map: canvasTexture,
        transparent: true,
        blending: THREE.AdditiveBlending,
        depthWrite: false,
        depthTest: true,
        side: THREE.DoubleSide
      });
      const sunCorona = new THREE.Mesh(coronaGeo, coronaMat);
      sunGroup.add(sunCorona);

      // Primary solar directional light anchored at the exact Sun world position
      const sunLight = new THREE.DirectionalLight(0xffffff, 4.2);
      sunLight.position.copy(sunGroup.position);
      sunLight.target.position.set(0, 0, 0);
      scene.add(sunLight);
      scene.add(sunLight.target);

      const ambientLight = new THREE.AmbientLight(0xffffff, 0.015);
      scene.add(ambientLight);

      // Skysphere and starfield
      const textureLoader = new THREE.TextureLoader();
      textureLoader.crossOrigin = 'anonymous';

      const skyGeo = new THREE.SphereGeometry(8000, 64, 64);
      const skyTex = textureLoader.load('https://unpkg.com/three-globe/example/img/night-sky.png');
      skyTex.wrapS = THREE.RepeatWrapping;
      skyTex.wrapT = THREE.RepeatWrapping;
      const skyMat = new THREE.MeshBasicMaterial({
        map: skyTex,
        side: THREE.BackSide,
        depthWrite: false
      });
      const skyDome = new THREE.Mesh(skyGeo, skyMat);
      scene.add(skyDome);

      const starCount = 2000;
      const starGeo = new THREE.BufferGeometry();
      const starPos = new Float32Array(starCount * 3);
      const starColors = new Float32Array(starCount * 3);

      for (let i = 0; i < starCount; i++) {
        const r = 2500 + Math.random() * 3500;
        const theta = Math.random() * Math.PI * 2;
        const phi = Math.acos(2 * Math.random() - 1);

        starPos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
        starPos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
        starPos[i * 3 + 2] = r * Math.cos(phi);

        const lum = 0.65 + Math.random() * 0.35;
        starColors[i * 3] = 0.75 * lum;
        starColors[i * 3 + 1] = 0.9 * lum;
        starColors[i * 3 + 2] = 1.0 * lum;
      }
      starGeo.setAttribute('position', new THREE.BufferAttribute(starPos, 3));
      starGeo.setAttribute('color', new THREE.BufferAttribute(starColors, 3));

      const starMat = new THREE.PointsMaterial({
        size: 2.0,
        vertexColors: true,
        transparent: true,
        opacity: 0.82
      });
      scene.add(new THREE.Points(starGeo, starMat));

      // Earth, clouds, and atmosphere shaders
      const earthDayTex = textureLoader.load('https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_atmos_2048.jpg');
      const earthNormalTex = textureLoader.load('https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_normal_2048.jpg');
      const earthSpecularTex = textureLoader.load('https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_specular_2048.jpg');
      const earthCloudsTex = textureLoader.load('https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_clouds_1024.png');
      const earthLightsTex = textureLoader.load('https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_lights_2048.png');

      const earthGeo = new THREE.SphereGeometry(10, 64, 64);
      const earthMat = new THREE.MeshStandardMaterial({
        color: 0x1d365d,
        map: earthDayTex,
        normalMap: earthNormalTex,
        normalScale: new THREE.Vector2(0.85, 0.85),
        roughnessMap: earthSpecularTex,
        roughness: 0.85,
        metalness: 0.05,
        emissiveMap: earthLightsTex,
        emissive: new THREE.Color(0xffffff),
        emissiveIntensity: 1.0
      });

      // City lights night terminator shader
      let earthShaderUniforms = null;
      try {
        earthMat.onBeforeCompile = (shader) => {
          earthShaderUniforms = shader.uniforms;
          shader.uniforms.uSunDir = { value: sunPosition.clone().normalize() };
          shader.vertexShader = `varying vec3 vWorldNormal;\n` + shader.vertexShader;
          shader.vertexShader = shader.vertexShader.replace(
            `#include <worldpos_vertex>`,
            `#include <worldpos_vertex>\nvWorldNormal = normalize((modelMatrix * vec4(normal, 0.0)).xyz);`
          );
          shader.fragmentShader = `uniform vec3 uSunDir;\nvarying vec3 vWorldNormal;\n` + shader.fragmentShader;
          shader.fragmentShader = shader.fragmentShader.replace(
            `#include <emissivemap_fragment>`,
            `#include <emissivemap_fragment>
             float sunDot = dot(normalize(vWorldNormal), normalize(uSunDir));
             float sunMask = smoothstep(-0.15, 0.1, sunDot);
             float nightMask = clamp(1.0 - sunMask, 0.0, 1.0);
             totalEmissiveRadiance *= (nightMask * 0.35);
            `
          );
        };
      } catch (err) {
        console.warn("Shader onBeforeCompile fallback:", err);
      }

      const earthMesh = new THREE.Mesh(earthGeo, earthMat);
      scene.add(earthMesh);

      const cloudGeo = new THREE.SphereGeometry(10.18, 64, 64);
      const cloudMat = new THREE.MeshLambertMaterial({
        map: earthCloudsTex,
        transparent: true,
        opacity: 0.45,
        blending: THREE.NormalBlending
      });
      const cloudMesh = new THREE.Mesh(cloudGeo, cloudMat);
      scene.add(cloudMesh);

      const atmosphereGeo = new THREE.SphereGeometry(10.42, 64, 64);
      const atmosphereMat = new THREE.ShaderMaterial({
        vertexShader: `
          varying vec3 vNormal;
          varying vec3 vPosition;
          void main() {
            vNormal = normalize(normalMatrix * normal);
            vPosition = (modelViewMatrix * vec4(position, 1.0)).xyz;
            gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
          }
        `,
        fragmentShader: `
          varying vec3 vNormal;
          varying vec3 vPosition;
          uniform vec3 uSunPos;
          void main() {
            vec3 viewDir = normalize(-vPosition);
            float rim = 1.0 - max(dot(viewDir, vNormal), 0.0);
            float halo = pow(rim, 3.2);

            vec3 eyeSun = normalize((viewMatrix * vec4(uSunPos, 0.0)).xyz);
            float sunFacing = dot(vNormal, eyeSun);
            float daylight = smoothstep(-0.25, 0.5, sunFacing);

            vec3 rayleighColor = vec3(0.18, 0.58, 1.0);
            gl_FragColor = vec4(rayleighColor, halo * (0.2 + 0.8 * daylight) * 0.95);
          }
        `,
        uniforms: {
          uSunPos: { value: sunPosition }
        },
        blending: THREE.AdditiveBlending,
        side: THREE.BackSide,
        transparent: true,
        depthWrite: false
      });
      const atmosphereMesh = new THREE.Mesh(atmosphereGeo, atmosphereMat);
      scene.add(atmosphereMesh);

      // Ground station telemetry marker
      function latLonToCartesian(lat, lon, radius) {
        const phi = (90 - lat) * (Math.PI / 180);
        const theta = (lon + 180) * (Math.PI / 180);
        const x = -radius * Math.sin(phi) * Math.cos(theta);
        const y = radius * Math.cos(phi);
        const z = radius * Math.sin(phi) * Math.sin(theta);
        return new THREE.Vector3(x, y, z);
      }

      // Malé station coordinates (4.1755° N, 73.5093° E)
      const maleLat = 4.1755;
      const maleLon = 73.5093;
      const malePos = latLonToCartesian(maleLat, maleLon, 10.05);

      const maleStationGroup = new THREE.Group();
      maleStationGroup.position.copy(malePos);

      const surfaceNormal = malePos.clone().normalize();
      maleStationGroup.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), surfaceNormal);

      const beaconGeo = new THREE.CylinderGeometry(0.08, 0.16, 0.45, 16);
      const beaconMat = new THREE.MeshStandardMaterial({
        color: 0x00f0ff,
        emissive: 0x00f0ff,
        emissiveIntensity: 2.2,
        roughness: 0.25,
        metalness: 0.85
      });
      const beaconMesh = new THREE.Mesh(beaconGeo, beaconMat);
      beaconMesh.position.y = 0.22;
      maleStationGroup.add(beaconMesh);

      const maleLight = new THREE.PointLight(0x00f0ff, 2.5, 6.0);
      maleLight.position.y = 0.5;
      maleStationGroup.add(maleLight);

      const ringGeo = new THREE.RingGeometry(0.12, 0.35, 32);
      const ringMat = new THREE.MeshBasicMaterial({
        color: 0x00f0ff,
        transparent: true,
        opacity: 0.9,
        side: THREE.DoubleSide
      });
      const pingRing = new THREE.Mesh(ringGeo, ringMat);
      pingRing.rotation.x = Math.PI / 2;
      pingRing.position.y = 0.02;
      maleStationGroup.add(pingRing);

      earthMesh.add(maleStationGroup);

      beaconMesh.userData = {
        name: "MALÉ GROUND COMMAND",
        isStation: true,
        coords: "4.1755° N, 73.5093° E",
        desc: "PRIMARY SENSOR & TELEMETRY UPLINK [MALDIVES]",
        group: maleStationGroup
      };

      // Asteroid trajectory curves and geometry
      const TIME_SCALE = 0.15;
      const asteroidGroups = [];
      const asteroidGroup = new THREE.Group();
      scene.add(asteroidGroup);
      asteroidGroup.add(beaconMesh);
      const interactiveObjects = [beaconMesh];

      const asteroidBumpMap = textureLoader.load('https://unpkg.com/three-globe/example/img/earth-topology.png');
      asteroidBumpMap.wrapS = THREE.RepeatWrapping;
      asteroidBumpMap.wrapT = THREE.RepeatWrapping;
      asteroidBumpMap.repeat.set(4, 4);

      const asteroidNormalTex = textureLoader.load('https://unpkg.com/three-globe/example/img/earth-topology.png');
      asteroidNormalTex.wrapS = THREE.RepeatWrapping;
      asteroidNormalTex.wrapT = THREE.RepeatWrapping;
      asteroidNormalTex.repeat.set(4, 4);

      if (!asteroidData || asteroidData.length === 0) {
        console.warn("No asteroids found.");
      } else {
        const minMiss = Math.min(...asteroidData.map(a => Number(a["Miss Distance (km)"]) || 1e6));
        const maxMiss = Math.max(...asteroidData.map(a => Number(a["Miss Distance (km)"]) || 7e7));
        const maxDiam = Math.max(...asteroidData.map(a => Number(a["Diameter (m)"]) || 100));
        const minDiam = Math.min(...asteroidData.map(a => Number(a["Diameter (m)"]) || 10));

        asteroidData.forEach((ast, idx) => {
          const isHazard = Boolean(ast["Hazardous"]);
          const missKm = Number(ast["Miss Distance (km)"]) || 5e6;
          const diamM = Number(ast["Diameter (m)"]) || 50;
          const velKmh = Number(ast["Velocity (km/h)"]) || 30000;
          const missLd = Number(ast["Lunar Distance (LD)"]) || (missKm / 384400.0);
          const scaleAnalogy = ast["Scale Analogy"] || "Scale unknown";

          const normDist = (maxMiss > minMiss) ? (missKm - minMiss) / (maxMiss - minMiss) : 0.5;
          const periRadius = 18 + normDist * 64;

          const inclination = (((idx * 43) % 75) - 37.5) * (Math.PI / 180);
          const theta = (idx / Math.max(1, asteroidData.length)) * Math.PI * 2;

          // Periapsis coordinates
          const pMiddle = new THREE.Vector3(
            periRadius * Math.cos(theta),
            periRadius * Math.sin(theta) * Math.sin(inclination),
            periRadius * Math.sin(theta) * Math.cos(inclination)
          );

          const normal = pMiddle.clone().normalize();
          const tangent = new THREE.Vector3(
            -Math.sin(theta),
            Math.cos(theta) * Math.sin(inclination),
            Math.cos(theta) * Math.cos(inclination)
          ).normalize();

          // Hyperbolic trajectory asymptotes
          const dDeep = 450 + normDist * 180;
          const pStart = pMiddle.clone()
            .sub(tangent.clone().multiplyScalar(dDeep))
            .add(normal.clone().multiplyScalar(dDeep * 0.08));
          const pEnd = pMiddle.clone()
            .add(tangent.clone().multiplyScalar(dDeep))
            .add(normal.clone().multiplyScalar(dDeep * 0.08));

          // Trajectory spline
          const curve = new THREE.CatmullRomCurve3([pStart, pMiddle, pEnd], false, 'catmullrom', 0.1);

          // Trajectory line geometry and vertex colors
          const curvePts = curve.getPoints(120);
          const colors = [];
          const peakCol = isHazard ? new THREE.Color(0xff003c) : new THREE.Color(0x00f0ff);
          const voidCol = new THREE.Color(0x000000);

          for (let s = 0; s < curvePts.length; s++) {
            const normS = s / (curvePts.length - 1);
            const intensity = Math.pow(Math.sin(normS * Math.PI), 1.6);
            const col = voidCol.clone().lerp(peakCol, intensity);
            colors.push(col.r, col.g, col.b);
          }

          const pathGeo = new THREE.BufferGeometry().setFromPoints(curvePts);
          pathGeo.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));

          const pathMat = new THREE.LineBasicMaterial({
            vertexColors: true,
            transparent: true,
            opacity: 0.85,
            blending: THREE.AdditiveBlending,
            depthWrite: false
          });
          const flybyLine = new THREE.Line(pathGeo, pathMat);
          scene.add(flybyLine);

          // High-density geometry and procedural displacement
          const normDiam = (maxDiam > minDiam) ? (diamM - minDiam) / (maxDiam - minDiam) : 0.5;
          const geoSize = 0.55 + normDiam * 1.5;
          const astGeo = new THREE.IcosahedronGeometry(geoSize, 6);

          const posAttr = astGeo.attributes.position;
          const v = new THREE.Vector3();
          const craterCenter = new THREE.Vector3(
            Math.sin(idx * 2.13),
            Math.cos(idx * 3.41),
            Math.sin(idx * 1.77)
          ).normalize();
          
          for (let p = 0; p < posAttr.count; p++) {
            v.fromBufferAttribute(posAttr, p);
            const dir = v.clone().normalize();
            
            const ridge1 = (1.0 - Math.abs(Math.sin(dir.x * 2.4 + idx * 0.7))) * 0.16;
            const ridge2 = Math.pow(Math.abs(Math.cos(dir.z * 3.6 + dir.y * 2.2)), 2.0) * 0.10;
            const gouge1 = -Math.pow(Math.abs(Math.sin(dir.y * 4.5 + dir.x * 3.2)), 2.5) * 0.12;
            const gouge2 = -Math.pow(Math.abs(Math.cos(dir.z * 6.0 + dir.x * 1.5)), 3.0) * 0.08;
            const microGrain = Math.sin(dir.x * 18.0) * Math.cos(dir.y * 18.0) * Math.sin(dir.z * 18.0) * 0.02;
            
            const angleToCrater = dir.angleTo(craterCenter);
            let craterDisp = 0.0;
            if (angleToCrater < 0.50) {
              const u = angleToCrater / 0.50;
              const bowl = -Math.pow(Math.cos(Math.min(1.0, u * 1.25) * Math.PI * 0.5), 2.0) * 0.22;
              const rim = Math.pow(Math.sin(Math.max(0.0, (u - 0.55) / 0.45) * Math.PI), 2.0) * 0.09;
              craterDisp = bowl + rim;
            }
            
            const totalDisp = 1.0 + ridge1 + ridge2 + gouge1 + gouge2 + microGrain + craterDisp;
            v.multiplyScalar(totalDisp);
            posAttr.setXYZ(p, v.x, v.y, v.z);
          }

          astGeo.computeVertexNormals();

          const rotAxis = new THREE.Vector3(
            (Math.random() - 0.5) * 2,
            (Math.random() - 0.5) * 2,
            (Math.random() - 0.5) * 2
          ).normalize();
          const rotSpeed = 0.005 + Math.random() * 0.015;

          const astMat = new THREE.MeshStandardMaterial({
            color: 0x222426,
            roughness: 0.95,
            metalness: 0.05,
            flatShading: false,
            bumpMap: asteroidBumpMap,
            bumpScale: 0.02,
            normalMap: asteroidNormalTex,
            normalScale: new THREE.Vector2(2.5, 2.5),
            emissive: isHazard ? new THREE.Color(0xff003c) : new THREE.Color(0x000000),
            emissiveIntensity: isHazard ? 0.35 : 0.0
          });
          const rockMesh = new THREE.Mesh(astGeo, astMat);

          if (isHazard) {
            const markerGeo = new THREE.RingGeometry(geoSize * 1.4, geoSize * 1.55, 32);
            const markerMat = new THREE.MeshBasicMaterial({
              color: 0xff003c,
              side: THREE.DoubleSide,
              transparent: true,
              opacity: 0.95
            });
            const marker = new THREE.Mesh(markerGeo, markerMat);
            marker.rotation.x = Math.PI / 2;
            rockMesh.add(marker);
          }

          const hitboxRadius = geoSize * 8.0;
          const hitboxGeo = new THREE.SphereGeometry(hitboxRadius, 16, 16);
          const hitboxMat = new THREE.MeshBasicMaterial({ visible: false });
          const hitboxMesh = new THREE.Mesh(hitboxGeo, hitboxMat);

          const astGroup = new THREE.Group();
          astGroup.add(rockMesh);
          astGroup.add(hitboxMesh);

          const startT = (idx * 0.28 + 0.15) % 1.0;
          const flybySpeed = (velKmh / 60000.0) * 0.0006 + 0.0003;

          const telemetryData = {
            name: ast["Name"],
            isHazard: isHazard,
            diameter: diamM,
            velocity: velKmh,
            missKm: missKm,
            missLd: missLd,
            scaleAnalogy: scaleAnalogy,
            curve: curve,
            t: startT,
            speed: flybySpeed,
            rotAxis: rotAxis,
            rotSpeed: rotSpeed,
            periapsis: pMiddle,
            inclination: inclination,
            group: astGroup,
            rock: rockMesh,
            hitbox: hitboxMesh,
            geoSize: geoSize
          };

          astGroup.userData = telemetryData;
          rockMesh.userData = telemetryData;
          hitboxMesh.userData = telemetryData;

          const initialPos = curve.getPoint(startT);
          astGroup.position.copy(initialPos);

          asteroidGroup.add(astGroup);
          asteroidGroups.push(telemetryData);
          interactiveObjects.push(hitboxMesh);
        });
      }

      // Procedural Landmark Hologram Generator
      function clearHologramGroup() {
        while (hologramGroup.children.length > 0) {
          const child = hologramGroup.children[0];
          hologramGroup.remove(child);
          if (child.isGroup) {
            while (child.children.length > 0) {
              const subChild = child.children[0];
              child.remove(subChild);
              if (subChild.geometry) subChild.geometry.dispose();
              if (subChild.material) {
                if (subChild.material.map) subChild.material.map.dispose();
                if (subChild.material !== hologramMaterial) subChild.material.dispose();
              }
            }
          } else {
            if (child.geometry) child.geometry.dispose();
            if (child.material) {
              if (child.material.map) child.material.map.dispose();
              if (child.material !== hologramMaterial) child.material.dispose();
            }
          }
        }
      }

      function createLandmarkHologram(asteroidDiameterMeters, geoSize) {
        clearHologramGroup();
        if (!hologramEnabled || !asteroidDiameterMeters) return;

        const diam = Number(asteroidDiameterMeters) || 100;
        let landmarkName = "";
        let landmarkHeight = 0;
        let landmarkWidth = 0;
        let landmarkDim = "";
        const pts = [];

        function addSeg(x1, y1, z1, x2, y2, z2) {
          pts.push(new THREE.Vector3(x1, y1, z1), new THREE.Vector3(x2, y2, z2));
        }

        if (diam < 100) {
          // Passenger jet silhouette (length ~70m, wingspan ~65m)
          landmarkName = "Passenger Jet (747)";
          landmarkHeight = 70;
          landmarkWidth = 65;
          landmarkDim = "70m Length";

          // Nose cone & Cockpit
          addSeg(0, 70, 0, -3.2, 62, 0);
          addSeg(0, 70, 0, 3.2, 62, 0);
          addSeg(-3.2, 62, 0, 3.2, 62, 0);
          addSeg(0, 70, 0, 0, 62, 3);
          addSeg(-3.2, 62, 0, 0, 62, 3);
          addSeg(3.2, 62, 0, 0, 62, 3);
          addSeg(-2.8, 64, 1.5, 2.8, 64, 1.5);

          // Fuselage tube
          addSeg(-3.2, 62, 0, -3.2, 10, 0);
          addSeg(3.2, 62, 0, 3.2, 10, 0);
          addSeg(0, 62, 3, 0, 10, 3);
          addSeg(-3.2, 45, 0, 3.2, 45, 0);
          addSeg(-3.2, 28, 0, 3.2, 28, 0);

          // Left Wing
          addSeg(-3.2, 42, 0, -32.5, 22, 0);
          addSeg(-32.5, 22, 0, -32.5, 27, 0);
          addSeg(-32.5, 27, 0, -3.2, 50, 0);
          addSeg(-32.5, 27, 0, -32.5, 32, 2.5); // Winglet
          addSeg(-12, 30, -2, -12, 38, -2);     // Engine
          addSeg(-10, 34, -2, -14, 34, -2);

          // Right Wing
          addSeg(3.2, 42, 0, 32.5, 22, 0);
          addSeg(32.5, 22, 0, 32.5, 27, 0);
          addSeg(32.5, 27, 0, 3.2, 50, 0);
          addSeg(32.5, 27, 0, 32.5, 32, 2.5);  // Winglet
          addSeg(12, 30, -2, 12, 38, -2);      // Engine
          addSeg(10, 34, -2, 14, 34, -2);

          // Horizontal Tail Stabilizers
          addSeg(-3.2, 6, 0, -12.5, 2, 0);
          addSeg(-12.5, 2, 0, -12.5, 5, 0);
          addSeg(-12.5, 5, 0, -3.2, 10, 0);
          addSeg(3.2, 6, 0, 12.5, 2, 0);
          addSeg(12.5, 2, 0, 12.5, 5, 0);
          addSeg(12.5, 5, 0, 3.2, 10, 0);

          // Vertical Tail Fin & Closure
          addSeg(0, 12, 0, 0, 2, 16);
          addSeg(0, 2, 16, 0, 0, 14);
          addSeg(0, 0, 14, 0, 0, 0);
          addSeg(-3.2, 10, 0, 0, 0, 0);
          addSeg(3.2, 10, 0, 0, 0, 0);

        } else if (diam <= 450) {
          // Eiffel Tower silhouette (height 330m, stepped tapered wireframe lines)
          landmarkName = "Eiffel Tower";
          landmarkHeight = 330;
          landmarkWidth = 125;
          landmarkDim = "330m Height";

          // Base Pillars & Ground Ties
          addSeg(-62.5, 0, 0, -38, 57, 0);
          addSeg(62.5, 0, 0, 38, 57, 0);
          addSeg(-38, 0, 0, -25, 57, 0);
          addSeg(38, 0, 0, 25, 57, 0);
          addSeg(-62.5, 0, 0, -38, 0, 0);
          addSeg(38, 0, 0, 62.5, 0, 0);

          // Base Arch
          addSeg(-25, 0, 0, -18, 30, 0);
          addSeg(-18, 30, 0, 0, 40, 0);
          addSeg(0, 40, 0, 18, 30, 0);
          addSeg(18, 30, 0, 25, 0, 0);

          // Base Trusses
          addSeg(-62.5, 0, 0, -25, 57, 0);
          addSeg(-38, 0, 0, -38, 57, 0);
          addSeg(62.5, 0, 0, 25, 57, 0);
          addSeg(38, 0, 0, 38, 57, 0);

          // Level 1 Platform (Y = 57 to 62)
          addSeg(-42, 57, 0, 42, 57, 0);
          addSeg(-40, 62, 0, 40, 62, 0);
          addSeg(-42, 57, 0, -40, 62, 0);
          addSeg(42, 57, 0, 40, 62, 0);

          // Tier 2 (Y = 62 to 115)
          addSeg(-35, 62, 0, -20, 115, 0);
          addSeg(35, 62, 0, 20, 115, 0);
          addSeg(-20, 62, 0, -12, 115, 0);
          addSeg(20, 62, 0, 12, 115, 0);
          addSeg(-35, 62, 0, -12, 115, 0);
          addSeg(-20, 62, 0, -20, 115, 0);
          addSeg(35, 62, 0, 12, 115, 0);
          addSeg(20, 62, 0, 20, 115, 0);

          // Level 2 Platform (Y = 115 to 120)
          addSeg(-24, 115, 0, 24, 115, 0);
          addSeg(-22, 120, 0, 22, 120, 0);
          addSeg(-24, 115, 0, -22, 120, 0);
          addSeg(24, 115, 0, 22, 120, 0);

          // Tapered Shaft (Y = 120 to 276)
          addSeg(-18, 120, 0, -4, 276, 0);
          addSeg(18, 120, 0, 4, 276, 0);
          addSeg(0, 120, 0, 0, 276, 0);

          let prevY = 120, prevW = 18;
          [160, 200, 240, 276].forEach(y => {
            const w = 18 - (18 - 4) * ((y - 120) / (276 - 120));
            addSeg(-w, y, 0, w, y, 0);
            addSeg(-prevW, prevY, 0, w, y, 0);
            addSeg(prevW, prevY, 0, -w, y, 0);
            prevY = y;
            prevW = w;
          });

          // Level 3 Platform & Dome (Y = 276 to 295)
          addSeg(-7, 276, 0, 7, 276, 0);
          addSeg(-4, 276, 0, -3, 295, 0);
          addSeg(4, 276, 0, 3, 295, 0);
          addSeg(-3, 295, 0, 3, 295, 0);

          // Lantern & Spire (Y = 295 to 330)
          addSeg(-2, 295, 0, -1.5, 305, 0);
          addSeg(2, 295, 0, 1.5, 305, 0);
          addSeg(-1.5, 305, 0, 1.5, 305, 0);
          addSeg(0, 305, 0, 0, 330, 0);
          addSeg(-3, 318, 0, 3, 318, 0);

        } else {
          // Skyscraper (Burj Khalifa silhouette, height 828m, stepped vertical setbacks)
          landmarkName = "Burj Khalifa";
          landmarkHeight = 828;
          landmarkWidth = 140;
          landmarkDim = "828m Height";

          // Base Podium
          addSeg(-70, 0, 0, 70, 0, 0);
          addSeg(-70, 0, 0, -70, 80, 0);
          addSeg(70, 0, 0, 70, 80, 0);
          addSeg(-70, 40, 0, 70, 40, 0);

          // Central Spine Line
          addSeg(0, 0, 0, 0, 750, 0);

          // Stepped Setbacks
          const setbacks = [
            { y0: 80, y1: 160, xL: -58, xR: 70, shelfL: -70, shelfR: 70 },
            { y0: 160, y1: 240, xL: -58, xR: 50, shelfL: -58, shelfR: 70 },
            { y0: 240, y1: 320, xL: -46, xR: 50, shelfL: -58, shelfR: 50 },
            { y0: 320, y1: 400, xL: -46, xR: 38, shelfL: -46, shelfR: 50 },
            { y0: 400, y1: 480, xL: -34, xR: 38, shelfL: -46, shelfR: 38 },
            { y0: 480, y1: 560, xL: -34, xR: 26, shelfL: -34, shelfR: 38 },
            { y0: 560, y1: 630, xL: -22, xR: 26, shelfL: -34, shelfR: 26 },
            { y0: 630, y1: 700, xL: -12, xR: 12, shelfL: -22, shelfR: 26 },
            { y0: 700, y1: 750, xL: -6, xR: 6, shelfL: -12, shelfR: 12 }
          ];

          setbacks.forEach(tier => {
            if (tier.shelfL !== tier.xL) addSeg(tier.shelfL, tier.y0, 0, tier.xL, tier.y0, 0);
            if (tier.shelfR !== tier.xR) addSeg(tier.xR, tier.y0, 0, tier.shelfR, tier.y0, 0);
            addSeg(tier.xL, tier.y0, 0, tier.xL, tier.y1, 0);
            addSeg(tier.xR, tier.y0, 0, tier.xR, tier.y1, 0);
            const midY = (tier.y0 + tier.y1) * 0.5;
            addSeg(tier.xL, midY, 0, tier.xR, midY, 0);
            addSeg(tier.xL, tier.y1, 0, tier.xR, tier.y1, 0);
          });

          // Pinnacle Needle Spire (Y = 750 to 828)
          addSeg(-6, 750, 0, 0, 828, 0);
          addSeg(6, 750, 0, 0, 828, 0);
          addSeg(0, 750, 0, 0, 828, 0);
          addSeg(-4, 790, 0, 4, 790, 0);
          addSeg(-2, 815, 0, 2, 815, 0);
        }

        // Measurement bracket line alongside the landmark
        const xBrk = -(landmarkWidth * 0.5 + 18);
        addSeg(xBrk, 0, 0, xBrk, landmarkHeight, 0);
        addSeg(xBrk, landmarkHeight, 0, xBrk + 12, landmarkHeight, 0);
        addSeg(xBrk, 0, 0, xBrk + 12, 0, 0);
        addSeg(xBrk - 6, landmarkHeight * 0.5, 0, xBrk + 6, landmarkHeight * 0.5, 0);
        // Ground baseline
        addSeg(-(landmarkWidth * 0.5 + 24), 0, 0, (landmarkWidth * 0.5 + 16), 0, 0);

        // Build THREE.LineSegments
        const landmarkGeo = new THREE.BufferGeometry().setFromPoints(pts);
        const landmarkLines = new THREE.LineSegments(landmarkGeo, hologramMaterial);

        // Interactive scale comparison label sprite
        const canvas = document.createElement('canvas');
        canvas.width = 1024;
        canvas.height = 320;
        const ctx = canvas.getContext('2d');

        // Cyber container background
        ctx.fillStyle = 'rgba(6, 12, 24, 0.92)';
        ctx.strokeStyle = '#00f3ff';
        ctx.lineWidth = 4;
        if (ctx.roundRect) {
          ctx.beginPath();
          ctx.roundRect(4, 4, 1016, 312, 16);
          ctx.fill();
          ctx.stroke();
        } else {
          ctx.fillRect(4, 4, 1016, 312);
          ctx.strokeRect(4, 4, 1016, 312);
        }

        // Cyber corner accents
        ctx.fillStyle = '#00f3ff';
        ctx.fillRect(4, 4, 24, 6);
        ctx.fillRect(4, 4, 6, 24);
        ctx.fillRect(996, 4, 24, 6);
        ctx.fillRect(1014, 4, 6, 24);
        ctx.fillRect(4, 310, 24, 6);
        ctx.fillRect(4, 292, 6, 24);
        ctx.fillRect(996, 310, 24, 6);
        ctx.fillRect(1014, 292, 6, 24);

        // Header tag
        ctx.font = 'bold 24px monospace';
        ctx.fillStyle = '#00f3ff';
        ctx.fillText("HOLOGRAPHIC SCALE COMPARISON", 36, 48);

        // Landmark name
        ctx.font = 'bold 44px -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif';
        ctx.fillStyle = '#ffffff';
        ctx.fillText(`${landmarkName} (${landmarkDim})`, 36, 114);

        // Comparison line
        ctx.font = 'bold 36px monospace';
        ctx.fillStyle = '#ffaa00';
        ctx.fillText(`vs Asteroid (${Math.round(diam)}m)`, 36, 175);

        // Ratio readout
        const ratio = (diam / landmarkHeight).toFixed(2);
        ctx.font = '28px monospace';
        ctx.fillStyle = '#00f3ff';
        ctx.fillText(`Asteroid is ${ratio}x Landmark size`, 36, 235);

        const tex = new THREE.CanvasTexture(canvas);
        tex.minFilter = THREE.LinearFilter;
        const spriteMat = new THREE.SpriteMaterial({
          map: tex,
          transparent: true,
          opacity: 0.95,
          blending: THREE.AdditiveBlending,
          depthWrite: false
        });
        const labelSprite = new THREE.Sprite(spriteMat);

        const labelH = Math.max(35, landmarkHeight * 0.22);
        const labelW = labelH * (1024 / 320);
        labelSprite.scale.set(labelW, labelH, 1.0);
        labelSprite.position.set(xBrk - (labelW * 0.5) - 14, 0, 0);

        // Assemble subGroup centered at origin
        const subGroup = new THREE.Group();
        landmarkLines.position.y = -landmarkHeight * 0.5;
        labelSprite.position.y = 0;
        subGroup.add(landmarkLines);
        subGroup.add(labelSprite);

        // Scale relative to asteroid visual radius:
        // Visual diameter of asteroid is (geoSize * 2)
        // Physical diameter of asteroid is diam meters
        const gSize = geoSize || 1.2;
        const scaleFactor = (gSize * 2.0) / Math.max(1, diam);
        subGroup.scale.set(scaleFactor, scaleFactor, scaleFactor);

        hologramGroup.add(subGroup);
        return hologramGroup;
      }
      window.createLandmarkHologram = createLandmarkHologram;

      window.toggleHologram = function() {
        hologramEnabled = !hologramEnabled;
        const btn = document.getElementById('hologram-toggle');
        const label = btn ? btn.querySelector('.toggle-label') : null;
        if (hologramEnabled) {
          if (btn) btn.classList.remove('disabled');
          if (label) label.innerText = "3D HOLO COMPARISON: ON";
          if (selectedMesh && isTracking && selectedMesh.userData && selectedMesh.userData.diameter) {
            createLandmarkHologram(selectedMesh.userData.diameter, selectedMesh.userData.geoSize);
            hologramGroup.visible = true;
          }
        } else {
          if (btn) btn.classList.add('disabled');
          if (label) label.innerText = "3D HOLO COMPARISON: OFF";
          hologramGroup.visible = false;
        }
      };

      // Interaction and camera transitions
      const raycaster = new THREE.Raycaster();
      const mouse = new THREE.Vector2(-999, -999);
      let hoveredMesh = null;
      let selectedMesh = null;
      let isTracking = false;

      function triggerTargetLock(target) {
        stopAutoPilot();
        if (target.userData && target.userData.isStation) {
          flyToStation(target);
        } else {
          flyToAsteroid(target);
        }
      }

      window.addEventListener('mousemove', (e) => {
        const rect = renderer.domElement.getBoundingClientRect();
        mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

        if (hoveredMesh) {
          tooltip.style.left = e.clientX + 'px';
          tooltip.style.top = e.clientY + 'px';
        }
      });

      renderer.domElement.addEventListener('touchend', function(e) {
        if (!e.changedTouches || e.changedTouches.length === 0) return;
        const touch = e.changedTouches[0];
        const rect = renderer.domElement.getBoundingClientRect();

        // Calculate precise normalized device coordinates for mobile touch
        mouse.x = ((touch.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((touch.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(asteroidGroup.children, true);
        if (intersects.length > 0) {
          e.preventDefault();
          triggerTargetLock(intersects[0].object);
        }
      }, { passive: false });

      renderer.domElement.addEventListener('click', (e) => {
        const rect = renderer.domElement.getBoundingClientRect();
        mouse.x = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        mouse.y = -((e.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(asteroidGroup.children, true);
        if (intersects.length > 0) {
          triggerTargetLock(intersects[0].object);
        }
      });

      window.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          stopAutoPilot();
          resetToEarthView();
        }
      });

      function flyToAsteroid(obj) {
        const group = obj.isGroup ? obj : (obj.userData.group || obj.parent || obj);
        const data = obj.userData;
        selectedMesh = group;
        isTracking = true;

        tooltip.style.display = 'none';

        const astPos = group.position.clone();
        const viewOffset = astPos.clone().normalize().multiplyScalar(4.5).add(new THREE.Vector3(0, 1.8, 0));
        const targetCamPos = astPos.clone().add(viewOffset);

        new TWEEN.Tween(camera.position)
          .to({ x: targetCamPos.x, y: targetCamPos.y, z: targetCamPos.z }, 1600)
          .easing(TWEEN.Easing.Cubic.InOut)
          .start();

        new TWEEN.Tween(controls.target)
          .to({ x: astPos.x, y: astPos.y, z: astPos.z }, 1600)
          .easing(TWEEN.Easing.Cubic.InOut)
          .start();

        document.getElementById('drawer-name').innerText = data.name;
        
        const threatEl = document.getElementById('drawer-threat');
        if (data.isHazard) {
          threatEl.className = 'threat-pill threat-hazard';
          threatEl.innerText = '⚠️ POTENTIALLY HAZARDOUS';
        } else {
          threatEl.className = 'threat-pill threat-safe';
          threatEl.innerText = '🛡️ NOMINAL TRAJECTORY';
        }

        const scaleEl = document.getElementById('drawer-scale');
        if (scaleEl) {
          scaleEl.innerText = `Scale: ${data.scaleAnalogy}`;
        }
        document.getElementById('drawer-diameter').innerText = `${data.diameter.toLocaleString('en-US', {maximumFractionDigits: 1})} m`;
        document.getElementById('drawer-velocity').innerText = `${data.velocity.toLocaleString('en-US', {maximumFractionDigits: 0})} km/h`;
        document.getElementById('drawer-distance').innerText = `${data.missKm.toLocaleString('en-US', {maximumFractionDigits: 0})} km`;
        document.getElementById('drawer-ld').innerText = `${data.missLd.toFixed(2)} LD`;
        const incEl = document.getElementById('drawer-inc');
        if (incEl) incEl.innerText = `${(data.inclination * (180/Math.PI)).toFixed(1)}°`;

        renderSilhouette(data.diameter, data.scaleAnalogy);
        if (hologramEnabled && data && data.diameter) {
          createLandmarkHologram(data.diameter, data.geoSize);
          hologramGroup.visible = true;
        } else {
          hologramGroup.visible = false;
        }

        drawer.classList.add('open');
        drawer.style.right = '0px';

        const reticle = document.getElementById('targeting-reticle');
        const reticleTag = document.getElementById('reticle-status');
        if (reticle) {
          reticle.classList.add('active');
          if (data.isHazard) {
            reticle.classList.add('hazard');
            if (reticleTag) reticleTag.innerText = `⚠️ LOCK: ${data.name} [HAZARD]`;
          } else {
            reticle.classList.remove('hazard');
            if (reticleTag) reticleTag.innerText = `⌖ LOCK: ${data.name} [NOMINAL]`;
          }
          const vector = group.position.clone();
          vector.project(camera);
          const x = (vector.x * 0.5 + 0.5) * window.innerWidth;
          const y = (vector.y * -0.5 + 0.5) * window.innerHeight;
          reticle.style.left = x + 'px';
          reticle.style.top = y + 'px';
          reticle.style.display = 'block';
        }
      }

      function flyToStation(mesh) {
        selectedMesh = null;
        isTracking = false;
        hologramGroup.visible = false;
        tooltip.style.display = 'none';

        const worldPos = new THREE.Vector3();
        mesh.getWorldPosition(worldPos);

        const camTarget = worldPos.clone().normalize().multiplyScalar(15.5);

        new TWEEN.Tween(camera.position)
          .to({ x: camTarget.x, y: camTarget.y, z: camTarget.z }, 1600)
          .easing(TWEEN.Easing.Cubic.InOut)
          .start();

        new TWEEN.Tween(controls.target)
          .to({ x: worldPos.x, y: worldPos.y, z: worldPos.z }, 1600)
          .easing(TWEEN.Easing.Cubic.InOut)
          .start();

        document.getElementById('drawer-name').innerText = "MALÉ COMMAND";
        const threatEl = document.getElementById('drawer-threat');
        threatEl.className = 'threat-pill threat-safe';
        threatEl.innerText = '📡 ACTIVE SENSOR UPLINK';

        document.getElementById('drawer-scale').innerText = "Scale: Ground Sensor Station (4.18° N, 73.51° E)";
        document.getElementById('drawer-diameter').innerText = "Surface Sensor Array";
        document.getElementById('drawer-velocity').innerText = "1,670 km/h (Earth Rotation)";
        document.getElementById('drawer-distance').innerText = "0.0 km (Earth Surface)";
        document.getElementById('drawer-ld').innerText = "0.00 LD";
        const incEl = document.getElementById('drawer-inc');
        if (incEl) incEl.innerText = "4.2° N Equat.";

        const silContainer = document.getElementById('drawer-silhouette');
        silContainer.innerHTML = `
          <div style="font-size:12px; color:#00f0ff; font-family:monospace; padding-bottom:10px;">
            ● RADAR BEACON: ONLINE<br>
            ● OPTICAL SENSORS: CALIBRATED<br>
            ● LAT: 4.1755° N | LON: 73.5093° E
          </div>
        `;

        drawer.classList.add('open');
        drawer.style.right = '0px';

        const reticle = document.getElementById('targeting-reticle');
        if (reticle) {
          reticle.classList.remove('active');
          reticle.classList.remove('hazard');
          reticle.style.display = 'none';
        }
      }

      window.resetToEarthView = function() {
        stopAutoPilot();
        isTracking = false;
        selectedMesh = null;
        hologramGroup.visible = false;
        drawer.classList.remove('open');
        drawer.style.right = '-100vw';

        const reticle = document.getElementById('targeting-reticle');
        if (reticle) {
          reticle.classList.remove('active');
          reticle.classList.remove('hazard');
          reticle.style.display = 'none';
        }

        new TWEEN.Tween(camera.position)
          .to({ x: defaultCamPos.x, y: defaultCamPos.y, z: defaultCamPos.z }, 1500)
          .easing(TWEEN.Easing.Cubic.InOut)
          .start();

        new TWEEN.Tween(controls.target)
          .to({ x: 0, y: 0, z: 0 }, 1500)
          .easing(TWEEN.Easing.Cubic.InOut)
          .start();
      };

      window.toggleMissionControls = function() {
        try {
          const pDoc = window.parent.document;
          if (!pDoc) return;

          const expandBtn = pDoc.querySelector('[data-testid="stExpandSidebarButton"] button, [data-testid="stExpandSidebarButton"], [data-testid="stSidebarTrigger"] button, [data-testid="stSidebarTrigger"], [data-testid="collapsedControl"] button, section[data-testid="collapsedControl"] button, button[aria-label="Expand sidebar"]');
          if (expandBtn) {
            expandBtn.click();
            return;
          }

          const collapseBtn = pDoc.querySelector('[data-testid="stSidebarCollapseButton"] button, [data-testid="stSidebarCollapseButton"], button[aria-label="Collapse sidebar"]');
          if (collapseBtn) {
            collapseBtn.click();
            return;
          }
        } catch (err) {
          console.warn("Could not toggle mission controls sidebar:", err);
        }
      };

      const drawerCloseBtn = document.getElementById('drawer-close-btn') || document.querySelector('.close-btn') || document.querySelector('.drawer-close');
      if (drawerCloseBtn) {
        const onDrawerClose = (ev) => {
          if (ev) {
            ev.preventDefault();
            ev.stopPropagation();
          }
          window.resetToEarthView();
        };
        drawerCloseBtn.addEventListener('click', onDrawerClose);
        drawerCloseBtn.addEventListener('touchend', onDrawerClose);
      }

      function renderSilhouette(diameterM, scaleAnalogy) {
        const silContainer = document.getElementById('drawer-silhouette');
        if (!silContainer) return;

        let refLabel = "Boeing 737 (35m)";
        let refHeight = 35;
        if (diameterM < 15) {
          refLabel = "School Bus (12m)";
          refHeight = 12;
        } else if (diameterM < 50) {
          refLabel = "Airplane (38m)";
          refHeight = 38;
        } else if (diameterM < 150) {
          refLabel = "Football Stadium (110m)";
          refHeight = 110;
        } else if (diameterM < 400) {
          refLabel = "Skyscraper (300m)";
          refHeight = 300;
        } else {
          refLabel = "Burj Khalifa (828m)";
          refHeight = 828;
        }

        const astPx = Math.min(62, Math.max(16, (diameterM / (diameterM + refHeight)) * 72));
        const refPx = Math.min(62, Math.max(12, (refHeight / (diameterM + refHeight)) * 72));

        silContainer.innerHTML = `
          <div style="display:flex; flex-direction:column; align-items:center; gap:4px;">
            <div style="width:${astPx}px; height:${astPx}px; background:#00f0ff; border-radius:50%; box-shadow:0 0 10px rgba(0,240,255,0.6);"></div>
            <span style="font-size:9px; color:#00f0ff; font-weight:700;">NEO (${Math.round(diameterM)}m)</span>
          </div>
          <div style="display:flex; flex-direction:column; align-items:center; gap:4px;">
            <div style="width:${Math.max(6, refPx * 0.38)}px; height:${refPx}px; background:rgba(255,255,255,0.4); border-radius:2px;"></div>
            <span style="font-size:9px; color:rgba(255,255,255,0.6);">${refLabel}</span>
          </div>
        `;
      }

      // Auto-pilot tour mode
      let autoPilotInterval = null;
      let autoPilotIndex = 0;

      function stopAutoPilot() {
        if (autoPilotInterval !== null) {
          clearInterval(autoPilotInterval);
          autoPilotInterval = null;
          console.warn("[AUTOPILOT] Manual override detected. Disengaging.");
          const apBadge = document.getElementById('autopilot-nav-badge');
          if (apBadge) apBadge.style.display = 'none';
        }
      }

      function triggerAutoPilot() {
        if (!AUTO_PILOT_ENABLED) return;
        if (autoPilotInterval !== null) {
          clearInterval(autoPilotInterval);
          autoPilotInterval = null;
        }

        console.log("[AUTOPILOT] Auto-Pilot engaged. Initializing 8-second cycle.");
        const apBadge = document.getElementById('autopilot-nav-badge');
        if (apBadge) apBadge.style.display = 'inline-block';

        function cycleNextTarget() {
          if (!asteroidData || asteroidData.length === 0 || !asteroidGroups || asteroidGroups.length === 0) {
            return;
          }

          const target = asteroidGroups[autoPilotIndex];
          const targetName = (target && target.name) ? target.name : (asteroidData[autoPilotIndex] ? asteroidData[autoPilotIndex].Name : `TARGET-${autoPilotIndex + 1}`);

          console.log("[AUTOPILOT] Engaging target lock: " + targetName);
          autoPilotIndex = (autoPilotIndex + 1) % asteroidGroups.length;

          if (target && target.hitbox) {
            flyToAsteroid(target.hitbox);
          } else if (target && target.group) {
            flyToAsteroid(target.group);
          }
        }

        cycleNextTarget();
        autoPilotInterval = setInterval(cycleNextTarget, 8000);
      }

      window.triggerAutoPilot = triggerAutoPilot;
      window.stopAutoPilot = stopAutoPilot;

      // Render loop
      const clock = new THREE.Clock();

      function animate() {
        requestAnimationFrame(animate);
        const elapsed = clock.getElapsedTime();

        TWEEN.update();

        // 4. PER-FRAME BILLBOARDING & LIGHTING SYNCHRONIZATION
        sunGroup.position.copy(sunPosition);
        sunCorona.quaternion.copy(camera.quaternion);
        sunLight.position.copy(sunGroup.position);
        sunLight.target.position.set(0, 0, 0);
        sunLight.target.updateMatrixWorld();

        const currentSunDir = sunGroup.position.clone().normalize();
        if (earthShaderUniforms && earthShaderUniforms.uSunDir) {
          earthShaderUniforms.uSunDir.value.copy(currentSunDir);
        }
        if (typeof atmosphereMat !== 'undefined' && atmosphereMat.uniforms && atmosphereMat.uniforms.uSunPos) {
          atmosphereMat.uniforms.uSunPos.value.copy(sunGroup.position);
        }

        // Planetary rotation
        earthMesh.rotation.y += 0.0011;
        cloudMesh.rotation.y += 0.0017;

        // Ground station radar pulse
        const pingPhase = (elapsed * 1.8) % 1.0;
        pingRing.scale.set(1.0 + pingPhase * 3.2, 1.0 + pingPhase * 3.2, 1.0);
        ringMat.opacity = Math.max(0.0, 0.9 * (1.0 - pingPhase));
        maleLight.intensity = 1.2 + 0.8 * Math.sin(elapsed * 6.0);

        // Asteroid kinematics and tumbling
        asteroidGroups.forEach((item) => {
          item.t = (item.t + item.speed * TIME_SCALE) % 1.0;
          const currentPos = item.curve.getPoint(item.t);
          item.group.position.copy(currentPos);

          if (item.rotAxis && item.rotSpeed) {
            item.rock.rotateOnAxis(item.rotAxis, item.rotSpeed);
          }
        });

        // Target tracking and screen-space reticle projection
        if (isTracking && selectedMesh) {
          controls.target.copy(selectedMesh.position);

          // Holographic Scale Landmark Tracking & Flicker Animation
          if (hologramGroup && hologramGroup.visible) {
            const rightVec = new THREE.Vector3(1, 0, 0).applyQuaternion(camera.quaternion).normalize();
            const gSize = (selectedMesh.userData && selectedMesh.userData.geoSize) ? selectedMesh.userData.geoSize : 1.5;
            const offsetDist = gSize * 2.8 + 1.2;
            hologramGroup.position.copy(selectedMesh.position).addScaledVector(rightVec, offsetDist);
            hologramGroup.quaternion.copy(camera.quaternion);

            if (window.hologramMaterial) {
              window.hologramMaterial.opacity = 0.75 + 0.15 * Math.sin(Date.now() * 0.012);
            }
          }

          const reticle = document.getElementById('targeting-reticle');
          if (reticle && reticle.classList.contains('active')) {
            const vector = selectedMesh.position.clone();
            vector.project(camera);
            if (vector.z < 1.0) {
              const x = (vector.x * 0.5 + 0.5) * window.innerWidth;
              const y = (vector.y * -0.5 + 0.5) * window.innerHeight;
              reticle.style.left = x + 'px';
              reticle.style.top = y + 'px';
              reticle.style.display = 'block';
            } else {
              reticle.style.display = 'none';
            }
          }
        }

        // Raycast hover detection
        raycaster.setFromCamera(mouse, camera);
        const hits = raycaster.intersectObjects(asteroidGroup.children, true);

        if (hits.length > 0) {
          const hitObj = hits[0].object;
          if (hoveredMesh !== hitObj) {
            hoveredMesh = hitObj;
            document.body.style.cursor = 'pointer';
            tooltip.style.display = 'block';
            if (hoveredMesh.userData.isStation) {
              tooltip.innerHTML = `<span style="color:#00f0ff; font-weight:700;">📡 ${hoveredMesh.userData.name}</span><br><span style="color:rgba(255,255,255,0.7); font-size:10px;">[${hoveredMesh.userData.coords}]</span>`;
            } else {
              const u = hoveredMesh.userData;
              tooltip.innerHTML = `<span style="color:#00f0ff; font-weight:700;">⌖ ${u.name}</span> • ${u.isHazard ? '<span style="color:#ff003c; font-weight:700;">⚠️ HAZARDOUS</span>' : '<span style="color:#00ff88; font-weight:700;">NOMINAL</span>'}<br><span style="color:rgba(255,255,255,0.6); font-size:10px;">CLICK TO LOCK TARGET</span>`;
            }
          }
        } else {
          if (hoveredMesh) {
            hoveredMesh = null;
            document.body.style.cursor = 'default';
            tooltip.style.display = 'none';
          }
        }

        controls.update();
        renderer.render(scene, camera);
      }

      animate();

      if (typeof AUTO_PILOT_ENABLED !== 'undefined' && AUTO_PILOT_ENABLED) {
        triggerAutoPilot();
      }

      function onWindowResize() {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight, true);
        if (!isTracking && !drawer.classList.contains('open') && drawer.style.right !== '0px') {
          drawer.style.right = '-100vw';
        }
      }

      window.addEventListener('resize', onWindowResize);
      window.addEventListener('orientationchange', () => {
        setTimeout(onWindowResize, 150);
      });

    } catch (error) {
      document.body.innerHTML = "<h1 style='color:red; text-align:center; margin-top: 20%; font-family:monospace;'>CRASH: " + error.message + "</h1><pre style='color:#ff8888; text-align:center; font-family:monospace;'>" + (error.stack || '') + "</pre>";
      console.error("CRASH:", error);
    }
  </script>
</body>
</html>
"""

def render_eyes_on_asteroids(df: pd.DataFrame, target_date: str, autopilot_enabled: bool = False) -> str:
    if df is None or df.empty:
        df = create_guaranteed_mock_df()
        
    records = df[[
        "Name", "Hazardous", "Diameter (m)", "Velocity (km/h)",
        "Miss Distance (km)", "Lunar Distance (LD)", "Scale Analogy"
    ]].to_dict(orient="records")
    
    json_str = json.dumps(records)
    html_code = CINEMATIC_THREEJS_TEMPLATE.replace("__ASTEROID_DATA_JSON__", json_str)
    html_code = html_code.replace("__TARGET_DATE__", target_date)
    html_code = html_code.replace("__TRACKED_COUNT__", str(len(records)))
    html_code = html_code.replace("__AUTO_PILOT_ENABLED__", "true" if autopilot_enabled else "false")
    return html_code


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

    df = fetch_asteroid_data(target_date)

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

    html_content = render_eyes_on_asteroids(df, target_date, autopilot_enabled=autopilot_toggle)
    components.html(html_content, height=1000, scrolling=False)

if __name__ == "__main__":
    main()

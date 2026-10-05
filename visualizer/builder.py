"""Builder module for assembling the Three.js WebGL visualizer."""

import json
from pathlib import Path
from typing import Any, Dict, List, Union
import pandas as pd

from core.nasa_client import create_guaranteed_mock_df

VISUALIZER_DIR = Path(__file__).parent
HTML_TEMPLATE_PATH = VISUALIZER_DIR / "index.html"
JS_DIR = VISUALIZER_DIR / "js"

JS_MODULE_ORDER = [
    "celestial.js",
    "asteroids.js",
    "hologram.js",
    "interaction.js",
    "main.js",
]


def _load_js_bundle() -> str:
    """Concatenates JS modules in strict dependency order."""
    chunks = []
    for mod_name in JS_MODULE_ORDER:
        file_path = JS_DIR / mod_name
        if file_path.exists():
            chunks.append(f"// --- BEGIN MODULE: {mod_name} ---\n" + file_path.read_text(encoding="utf-8") + f"\n// --- END MODULE: {mod_name} ---")
        else:
            raise FileNotFoundError(f"Missing visualizer module: {file_path}")
    return "\n\n".join(chunks)


def build_visualizer_html(
    neo_data: Union[pd.DataFrame, List[Dict[str, Any]], None],
    target_date: str = "",
    autopilot_enabled: bool = False,
) -> str:
    """
    Constructs the complete standalone HTML visualizer document with embedded
    WebGL logic, styles, and asteroid ephemeris dataset.
    """
    if neo_data is None:
        df = create_guaranteed_mock_df()
        records = df.to_dict(orient="records")
    elif isinstance(neo_data, pd.DataFrame):
        if neo_data.empty:
            df = create_guaranteed_mock_df()
        else:
            df = neo_data
        cols = [c for c in [
            "Name", "Hazardous", "Diameter (m)", "Velocity (km/h)",
            "Miss Distance (km)", "Lunar Distance (LD)", "Scale Analogy"
        ] if c in df.columns]
        records = df[cols].to_dict(orient="records")
    elif isinstance(neo_data, list):
        records = neo_data
    else:
        records = []

    json_str = json.dumps(records)
    tracked_count = str(len(records))
    autopilot_bool = "true" if autopilot_enabled else "false"

    data_script = f"""
    const AUTO_PILOT_ENABLED = {autopilot_bool};
    let asteroidData = [];
    try {{
      asteroidData = JSON.parse(String.raw`{json_str}`);
    }} catch (e) {{
      asteroidData = [];
    }}

    if (!asteroidData || asteroidData.length === 0) {{
      asteroidData = [
        {{"Name": "SIM-ALPHA", "Diameter (m)": 250, "Velocity (km/h)": 45000, "Miss Distance (km)": 2500000, "Hazardous": true, "Scale Analogy": "Eiffel Tower scale", "Lunar Distance (LD)": 6.5}},
        {{"Name": "SIM-BETA", "Diameter (m)": 120, "Velocity (km/h)": 28000, "Miss Distance (km)": 14000000, "Hazardous": false, "Scale Analogy": "Football Stadium scale", "Lunar Distance (LD)": 36.4}}
      ];
    }}
    """

    js_bundle = _load_js_bundle()

    if not HTML_TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"HTML shell not found at: {HTML_TEMPLATE_PATH}")

    html_shell = HTML_TEMPLATE_PATH.read_text(encoding="utf-8")

    # Replace placeholders
    html_output = html_shell.replace("/* __NEO_DATA__ */", data_script)
    html_output = html_output.replace("/* __MODULE_SCRIPTS__ */", js_bundle)
    html_output = html_output.replace("__TARGET_DATE__", target_date)
    html_output = html_output.replace("__TRACKED_COUNT__", tracked_count)

    return html_output

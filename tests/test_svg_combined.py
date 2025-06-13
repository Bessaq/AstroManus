from pathlib import Path
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from kerykeion import AstrologicalSubject
from app.utils.svg_combined_chart import create_combined_chart_svg


def test_create_combined_chart_svg(tmp_path: Path):
    natal_subject = AstrologicalSubject(
        name="Joao",
        year=1997,
        month=10,
        day=13,
        hour=22,
        minute=0,
        city="Fortaleza",
        lng=-38.5247,
        lat=-3.7172,
        tz_str="America/Fortaleza",
    )

    transit_subject = AstrologicalSubject(
        name="Transitos_02_06_2025",
        year=2025,
        month=6,
        day=2,
        hour=12,
        minute=0,
        city="Fortaleza",
        lng=-38.5247,
        lat=-3.7172,
        tz_str="America/Fortaleza",
    )

    output = tmp_path / "chart.svg"
    result = create_combined_chart_svg(natal_subject, transit_subject, output)
    assert Path(result).exists()

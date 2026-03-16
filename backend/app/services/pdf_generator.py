from __future__ import annotations

import base64
import logging
from pathlib import Path

import weasyprint
from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)

TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"


class PdfGenerationError(Exception):
    pass


def _render_html(
    analysis_result: dict,
    report_config: dict,
    chart_images: dict[str, str],
) -> str:
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("report_base.html")

    # Sanitise chart_images: only accept data-URLs (base64 PNG/JPEG)
    safe_images: dict[str, str] = {}
    for key, value in chart_images.items():
        if isinstance(value, str) and value.startswith("data:image/"):
            safe_images[key] = value

    context = {
        "result": analysis_result,
        "config": report_config,
        "images": safe_images,
        "heights": analysis_result.get("analysis_heights", []),
    }
    return template.render(**context)


def generate_pdf(
    analysis_result: dict,
    report_config: dict,
    chart_images: dict[str, str],
) -> bytes:
    try:
        html_str = _render_html(analysis_result, report_config, chart_images)
        pdf = weasyprint.HTML(
            string=html_str,
            base_url=str(TEMPLATES_DIR),
        ).write_pdf()
        return pdf
    except Exception as exc:
        logger.exception("WeasyPrint 渲染失败")
        raise PdfGenerationError(str(exc)) from exc

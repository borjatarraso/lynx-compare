"""REST API server for Lynx Compare.

Exposes comparison, about, and export endpoints via Flask.

Usage
-----
    lynx-compare-server                # defaults to port 5000
    lynx-compare-server --port 8080    # custom port

Or programmatically::

    from lynx_compare.server import create_app
    app = create_app()
    app.run(port=8080)
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from dataclasses import asdict

import re

from lynx_compare import __version__, SUITE_NAME, SUITE_VERSION
from lynx_compare.about import (
    APP_NAME,
    DEVELOPER,
    DEVELOPER_EMAIL,
    LICENSE_NAME,
    LICENSE_TEXT,
    about_text,
    easter_egg_text,
    check_easter_egg,
)

# Narrow regex for user-supplied tickers / ISINs / names.
# Letters, digits, dots, hyphens, underscore, caret (^GSPC) — nothing that
# could inject CR/LF or semicolons into the Content-Disposition header.
_TICKER_SAFE_RE = re.compile(r"^[A-Za-z0-9._\-\^]{1,24}$")


def _validate_identifier(raw: str) -> tuple[str, str]:
    """Return ``(normalised, error)``; ``error`` empty on success."""
    if not raw:
        return "", "identifier cannot be empty"
    if len(raw) > 24:
        return "", "identifier too long (max 24 characters)"
    if not _TICKER_SAFE_RE.match(raw):
        return "", "identifier contains disallowed characters"
    return raw.upper(), ""


def create_app(run_mode: str = "production"):
    """Create and configure the Flask application."""
    from flask import Flask, jsonify, request, Response

    app = Flask(__name__)

    # Activate storage mode once
    from lynx.core.storage import set_mode
    set_mode(run_mode)

    # -------------------------------------------------------------------
    # Health / root
    # -------------------------------------------------------------------

    @app.route("/")
    def index():
        return jsonify({
            "name": APP_NAME,
            "version": __version__,
            "suite": SUITE_NAME,
            "suite_version": SUITE_VERSION,
            "endpoints": [
                "/about",
                "/compare",
                "/export",
                "/health",
            ],
        })

    @app.route("/health")
    def health():
        return jsonify({
            "status": "ok",
            "version": __version__,
            "suite_version": SUITE_VERSION,
        })

    # -------------------------------------------------------------------
    # About
    # -------------------------------------------------------------------

    @app.route("/about")
    def about():
        return jsonify({
            "name": APP_NAME,
            "version": __version__,
            "suite": SUITE_NAME,
            "suite_version": SUITE_VERSION,
            "developer": DEVELOPER,
            "email": DEVELOPER_EMAIL,
            "license": LICENSE_NAME,
            "license_text": LICENSE_TEXT,
        })

    # -------------------------------------------------------------------
    # Easter egg
    # -------------------------------------------------------------------

    @app.route("/easter-egg")
    def easter_egg():
        return Response(easter_egg_text(), mimetype="text/plain")

    # -------------------------------------------------------------------
    # Compare
    # -------------------------------------------------------------------

    @app.route("/compare", methods=["GET", "POST"])
    def compare_endpoint():
        """Compare two companies.

        GET  /compare?a=AAPL&b=MSFT
        POST /compare  {"a": "AAPL", "b": "MSFT"}

        Optional parameters: refresh, download_reports, download_news, verbose
        """
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
        else:
            data = request.args.to_dict()

        id_a = data.get("a", "").strip()
        id_b = data.get("b", "").strip()

        if not id_a or not id_b:
            return jsonify({
                "error": "Both 'a' and 'b' parameters are required.",
                "usage": "GET /compare?a=AAPL&b=MSFT",
            }), 400

        id_a, err_a = _validate_identifier(id_a)
        if err_a:
            return jsonify({"error": f"parameter 'a': {err_a}"}), 400
        id_b, err_b = _validate_identifier(id_b)
        if err_b:
            return jsonify({"error": f"parameter 'b': {err_b}"}), 400
        if id_a == id_b:
            return jsonify({"error": "identifiers 'a' and 'b' must differ"}), 400

        refresh = _bool_param(data.get("refresh", False))
        download_reports = _bool_param(data.get("download_reports", False))
        download_news = _bool_param(data.get("download_news", False))
        verbose = _bool_param(data.get("verbose", False))

        try:
            from lynx_compare.api import compare_companies
            view = compare_companies(
                id_a, id_b,
                refresh=refresh,
                download_reports=download_reports,
                download_news=download_news,
                verbose=verbose,
            )
            return jsonify({
                "summary": view.summary(),
                "winner": view.winner_ticker,
                "data": view.to_dict(),
            })
        except Exception as exc:
            # Log the true error server-side; surface a generic message.
            app.logger.exception("compare failed for %r / %r", id_a, id_b)
            return jsonify({"error": "comparison failed"}), 500

    # -------------------------------------------------------------------
    # Export
    # -------------------------------------------------------------------

    @app.route("/export", methods=["GET", "POST"])
    def export_endpoint():
        """Export a comparison in HTML, text, or PDF format.

        GET  /export?a=AAPL&b=MSFT&format=html
        POST /export  {"a": "AAPL", "b": "MSFT", "format": "pdf"}
        """
        if request.method == "POST":
            data = request.get_json(silent=True) or {}
        else:
            data = request.args.to_dict()

        id_a = data.get("a", "").strip()
        id_b = data.get("b", "").strip()
        fmt = data.get("format", "html").strip().lower()

        if not id_a or not id_b:
            return jsonify({
                "error": "Both 'a' and 'b' parameters are required.",
            }), 400

        id_a, err_a = _validate_identifier(id_a)
        if err_a:
            return jsonify({"error": f"parameter 'a': {err_a}"}), 400
        id_b, err_b = _validate_identifier(id_b)
        if err_b:
            return jsonify({"error": f"parameter 'b': {err_b}"}), 400

        if fmt not in ("html", "text", "txt", "pdf"):
            return jsonify({
                "error": f"Unsupported format '{fmt}'. Use: html, text, pdf",
            }), 400

        try:
            from lynx_compare.api import compare_companies
            from lynx_compare.export import export_html, export_text, export_pdf

            view = compare_companies(id_a, id_b)
            cr = view.raw

            if fmt in ("text", "txt"):
                content = export_text(cr)
                return Response(
                    content,
                    mimetype="text/plain",
                    headers={
                        "Content-Disposition":
                            f"attachment; filename={cr.ticker_a}_vs_{cr.ticker_b}.txt"
                    },
                )

            if fmt == "pdf":
                import tempfile
                import os
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                    tmp_path = tmp.name
                try:
                    export_pdf(cr, tmp_path)
                    with open(tmp_path, "rb") as f:
                        pdf_bytes = f.read()
                    return Response(
                        pdf_bytes,
                        mimetype="application/pdf",
                        headers={
                            "Content-Disposition":
                                f"attachment; filename={cr.ticker_a}_vs_{cr.ticker_b}.pdf"
                        },
                    )
                finally:
                    os.unlink(tmp_path)

            # HTML
            content = export_html(cr)
            return Response(
                content,
                mimetype="text/html",
                headers={
                    "Content-Disposition":
                        f"attachment; filename={cr.ticker_a}_vs_{cr.ticker_b}.html"
                },
            )

        except Exception as exc:
            app.logger.exception("export failed for %r / %r", id_a, id_b)
            return jsonify({"error": "export failed"}), 500

    return app


def _bool_param(val) -> bool:
    if isinstance(val, bool):
        return val
    if isinstance(val, str):
        return val.lower() in ("true", "1", "yes")
    return bool(val)


def run_server() -> None:
    """CLI entry point for the API server."""
    parser = argparse.ArgumentParser(
        prog="lynx-compare-server",
        description="Lynx Compare REST API server",
    )
    parser.add_argument(
        "--port", type=int, default=5000,
        help="Port to listen on (default: 5000)",
    )
    parser.add_argument(
        "--host", default="127.0.0.1",
        help="Host to bind to (default: 127.0.0.1)",
    )
    parser.add_argument(
        "-p", "--production-mode",
        action="store_const", const="production", dest="run_mode",
        help="Production mode (use cached data)",
    )
    parser.add_argument(
        "-t", "--testing-mode",
        action="store_const", const="testing", dest="run_mode",
        help="Testing mode (fresh data)",
    )
    parser.add_argument(
        "--debug", action="store_true",
        help="Enable Flask debug mode",
    )
    args = parser.parse_args()
    mode = args.run_mode or "production"

    app = create_app(run_mode=mode)
    print(f"Lynx Compare API server starting on {args.host}:{args.port} ({mode} mode)")
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    run_server()

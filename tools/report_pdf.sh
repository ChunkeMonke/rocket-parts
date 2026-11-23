#!/usr/bin/env bash
# Render a project's engineering report to PDF:  tools/report_pdf.sh [project]   (default l1-cheap)
# Wrapper for tools/report_build.py (pandoc markdown -> formal monochrome template -> two-pass Chromium PDF).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec "$ROOT/.venv/bin/python" "$ROOT/tools/report_build.py" "${1:-l1-cheap}"

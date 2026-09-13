#!/bin/zsh
set -e

KICAD_CLI="/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
REPORT="$ROOT/docs/ai-reports"

"$KICAD_CLI" pcb drc \
  -o "$REPORT/latest-drc.rpt" \
  "$ROOT/DSP_Controller.kicad_pcb"

echo "DRC report: $REPORT/latest-drc.rpt"

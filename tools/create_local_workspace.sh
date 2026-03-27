#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR=${1:-exam-ai-workspace}
mkdir -p "$ROOT_DIR/backend-exam-engine" "$ROOT_DIR/mobile-flutter-app" "$ROOT_DIR/shared-assets"

echo "Created workspace structure:"
echo "  $ROOT_DIR/backend-exam-engine"
echo "  $ROOT_DIR/mobile-flutter-app"
echo "  $ROOT_DIR/shared-assets"
echo
echo "Next steps:"
echo "1) Put this repo code into $ROOT_DIR/backend-exam-engine"
echo "2) Run: flutter create $ROOT_DIR/mobile-flutter-app"
echo "3) Start backend + flutter app locally"

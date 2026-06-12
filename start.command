#!/usr/bin/env bash
# macOS: Finder에서 더블클릭으로 실행
cd "$(dirname "$0")"
./start.sh
echo ""
read -p "이 창을 닫으려면 Enter를 누르세요..." _

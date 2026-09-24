#!/usr/bin/env bash
fail=0
check() {
  if eval "$2" >/dev/null 2>&1; then
    printf 'PASS %-18s %s
' "$1" "$3"
  else
    printf 'FAIL %-18s %s
' "$1" "$3"
    fail=1
  fi
}
check wsl 'env | grep -q "^WSL_DISTRO_NAME="' "WSL distro is active"
check systemd 'systemctl --user list-units >/dev/null 2>&1' "user systemd reachable"
check python 'python3 -c "import sys; raise SystemExit(sys.version_info < (3,11))"' "Python >= 3.11"
check git 'git --version' "git available"
check disk '[ "$(df -Pk . | awk "NR==2{print \$4}")" -gt 52428800 ]' ">50 GiB free"
check dns 'getent hosts github.com' "DNS resolves github.com"
check https 'curl -fsSIL --max-time 10 https://github.com/ >/dev/null' "HTTPS egress works"
check origin 'git ls-remote origin HEAD' "GitHub origin reachable"
if command -v nvidia-smi >/dev/null 2>&1; then
  echo "INFO gpu                discrete NVIDIA detected"
else
  echo "INFO gpu                no NVIDIA GPU; generation stays benchmark-blocked"
fi
if command -v ffmpeg >/dev/null 2>&1; then
  echo "INFO ffmpeg             installed"
else
  echo "INFO ffmpeg             not installed; needed before M6 edit/export"
fi
exit "$fail"

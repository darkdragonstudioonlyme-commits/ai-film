#!/bin/sh
# Static source is delivered via stdin to /bin/sh -s -- <data arguments>.
# No eval/source/os-release execution. stdout is an allowlisted base64 TSV frame.
set -eu
LC_ALL=C; export LC_ALL
PATH=/usr/sbin:/usr/bin:/sbin:/bin; export PATH
[ "$#" -eq 2 ] || exit 10
operation=$1
bound_user=$2
case "$bound_user" in ''|root|*[!a-z0-9_-]*) exit 10;; esac
emit() { printf '%s\t' "$1"; printf '%s' "$2" | /usr/bin/base64 -w0; printf '\n'; }
[ "$(/usr/bin/id -un)" = "$bound_user" ] || exit 12
case "$operation" in
  INVENTORY)
    emit uid "$(/usr/bin/id -u)"
    emit gid "$(/usr/bin/id -g)"
    emit user "$(/usr/bin/id -un)"
    emit groups "$(/usr/bin/id -Gn)"
    home=$(/usr/bin/getent passwd "$bound_user" | /usr/bin/cut -d: -f6)
    emit home "$home"
    if [ -w "$home" ]; then emit home_access_writable 1; else emit home_access_writable 0; fi
    emit os_id "$(/usr/bin/awk -F= '$1=="ID" {gsub(/\"/,"",$2);print $2}' /etc/os-release)"
    emit version_id "$(/usr/bin/awk -F= '$1=="VERSION_ID" {gsub(/\"/,"",$2);print $2}' /etc/os-release)"
    emit architecture "$(/usr/bin/uname -m)"
    emit kernel "$(/usr/bin/uname -r)"
    emit kernel_boot_id "$(/usr/bin/cat /proc/sys/kernel/random/boot_id)"
    emit pid1_start_ticks "$(/usr/bin/awk '{print $22}' /proc/1/stat)"
    emit pid1_comm "$(/usr/bin/cat /proc/1/comm)"
    emit logical_cpu "$(/usr/bin/getconf _NPROCESSORS_ONLN)"
    emit mem_total_kib "$(/usr/bin/awk '$1=="MemTotal:" {print $2}' /proc/meminfo)"
    emit mem_available_kib "$(/usr/bin/awk '$1=="MemAvailable:" {print $2}' /proc/meminfo)"
    emit fs_available_kib "$(/usr/bin/df -Pk -- "$home" | /usr/bin/awk 'NR==2 {print $4}')"
    if [ -f /etc/wsl.conf ]; then
      emit wsl_conf_sha256 "$(/usr/bin/sha256sum /etc/wsl.conf | /usr/bin/cut -d' ' -f1)"
    else emit wsl_conf_sha256 ABSENT; fi
    ;;
  *) exit 10;;
esac
emit completed 1

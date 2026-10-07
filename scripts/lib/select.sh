#!/usr/bin/env bash
# Rows are ID<TAB>description arguments. stdout contains IDs only.
set -euo pipefail
ui=$1
shift
if [[ $ui != bash ]] && command -v gum >/dev/null; then
  # gum exit/cancellation is fatal, never interpreted as an empty choice.
  selected=$(gum choose --no-limit -- "$@") || exit 2
  while IFS= read -r row; do
    [[ -z $row ]] || printf '%s\n' "${row%%$'\t'*}"
  done <<< "$selected"
  exit 0
fi
rows=("$@")
for index in "${!rows[@]}"; do
  printf '%d. %s\n' "$((index + 1))" "${rows[index]}" >&2
done
printf 'Numbers separated by spaces (Enter = none, q = cancel): ' >&2
IFS= read -r response || exit 2
[[ $response != q ]] || exit 2
for number in $response; do
  [[ $number =~ ^[0-9]+$ && ${#number} -lt 6 ]] || { echo 'Invalid selection' >&2; exit 2; }
  number=$((10#$number))
  ((number >= 1 && number <= ${#rows[@]})) || { echo 'Invalid selection' >&2; exit 2; }
  printf '%s\n' "${rows[number-1]%%$'\t'*}"
done

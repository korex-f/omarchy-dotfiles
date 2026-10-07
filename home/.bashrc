# Portable copy reviewed 2026-09-27. Omarchy defaults remain package-owned.
[[ $- != *i* ]] && return

if [[ -f /etc/omarchy.conf ]]; then
  source /etc/omarchy.conf
  export OMARCHY_PATH="${OMARCHY_PATH:-/usr/share/omarchy}"
else
  export OMARCHY_PATH=/usr/share/omarchy
fi
source "$OMARCHY_PATH/default/bash/rc"

. "$HOME/.local/share/../bin/env"
export RUFF_TARGET_VERSION=py314

alias ll='eza -lah --icons'
alias ls='eza --icons'
alias gs='git status'
alias gad='git add'
alias gc='git commit'
alias gpush='git push'
alias gpull='git pull'
alias glog='git log'
alias gdiff='git diff'
alias gsearch='git search'
alias lg='lazygit'
alias zed='zeditor'

eval "$(starship init bash)"
eval "$(zoxide init bash)"
eval "$(fzf --bash)"

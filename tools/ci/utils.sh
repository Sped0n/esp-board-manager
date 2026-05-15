#!/usr/bin/env bash

set -euo pipefail

function add_ssh_key() {
  local key_string="${1:-}"
  local key_name="${2:-id_rsa}"
  if [[ -z "${key_string}" ]]; then
    echo "SSH key for ${key_name} is empty; skip key setup."
    return
  fi

  mkdir -p ~/.ssh
  chmod 700 ~/.ssh
  printf "%s" "${key_string}" > "${HOME}/.ssh/${key_name}_base64"
  base64 --decode --ignore-garbage "${HOME}/.ssh/${key_name}_base64" > "${HOME}/.ssh/${key_name}"
  chmod 600 "${HOME}/.ssh/${key_name}"
}

function add_gitlab_ssh_keys() {
  add_ssh_key "${GITLAB_KEY:-}" "id_rsa"

  mkdir -p ~/.ssh
  chmod 700 ~/.ssh
  {
    printf "Host gitlab.espressif.cn\n\tStrictHostKeyChecking no\n"
    if [[ -n "${LOCAL_GITLAB_SSH_SERVER:-}" ]]; then
      local srv="${LOCAL_GITLAB_SSH_SERVER##*@}"
      srv="${srv%%:*}"
      printf "Host %s\n\tStrictHostKeyChecking no\n" "${srv}"
    fi
  } >> ~/.ssh/config
}

function add_github_ssh_keys() {
  add_ssh_key "${GH_PUSH_KEY:-}" "id_rsa_github"

  mkdir -p ~/.ssh
  chmod 700 ~/.ssh
  {
    printf "Host github.com\n"
    printf "\tIdentityFile ~/.ssh/id_rsa_github\n"
    printf "\tIdentitiesOnly yes\n"
    printf "\tStrictHostKeyChecking no\n"
  } >> ~/.ssh/config
}

function add_github_https_credentials() {
  local github_user="${GH_PUSH_USER:-${GITHUB_USER:-}}"
  local github_token="${GH_PUSH_TOKEN:-${GITHUB_TOKEN:-}}"

  if [[ -z "${github_user}" ]]; then
    echo "GH_PUSH_USER or GITHUB_USER is required for GitHub HTTPS push."
    exit 1
  fi

  if [[ -z "${github_token}" ]]; then
    echo "GH_PUSH_TOKEN or GITHUB_TOKEN is required for GitHub HTTPS push."
    exit 1
  fi

  local askpass
  askpass="$(mktemp)"
  {
    printf '#!/usr/bin/env bash\n'
    printf 'case "$1" in\n'
    printf '  *Username*) printf "%%s\\n" "${GITHUB_HTTPS_USER:?GITHUB_HTTPS_USER is not set}" ;;\n'
    printf '  *Password*) printf "%%s\\n" "${GITHUB_HTTPS_TOKEN:?GITHUB_HTTPS_TOKEN is not set}" ;;\n'
    printf '  *) printf "\\n" ;;\n'
    printf 'esac\n'
  } > "${askpass}"
  chmod 700 "${askpass}"

  export GITHUB_HTTPS_USER="${github_user}"
  export GITHUB_HTTPS_TOKEN="${github_token}"
  export GIT_ASKPASS="${askpass}"
  export GIT_TERMINAL_PROMPT=0
}

function get_github_https_remote() {
  local github_remote="${TARGET_GITHUB_REPO:-https://github.com/espressif/esp-board-manager.git}"

  case "${github_remote}" in
    git@github.com:*)
      github_remote="https://github.com/${github_remote#git@github.com:}"
      ;;
    ssh://git@github.com/*)
      github_remote="https://github.com/${github_remote#ssh://git@github.com/}"
      ;;
  esac

  if [[ "${github_remote}" != https://github.com/* ]]; then
    echo "GitHub remote must use https://github.com/ for token push: ${github_remote}"
    exit 1
  fi

  printf "%s\n" "${github_remote}"
}

function push_to_github() {
  if [[ -n "${CI_COMMIT_TAG:-}" ]]; then
    git push github "${CI_COMMIT_TAG}"
  else
    git push github "${CI_COMMIT_SHA}:refs/heads/${CI_COMMIT_REF_NAME}"
  fi
}

function install_bmgr_assist() {
  echo "Installing esp-bmgr-assist into ESP-IDF Python environment"
  python -m pip install --upgrade "${ESP_BMGR_ASSIST_INSTALL_SPEC:?ESP_BMGR_ASSIST_INSTALL_SPEC is not set}"
}

function setup_ci_venv() {
  pip install --upgrade pip
  pip install --upgrade "${IDF_CI_INSTALL_SPEC:?IDF_CI_INSTALL_SPEC is not set}"
}

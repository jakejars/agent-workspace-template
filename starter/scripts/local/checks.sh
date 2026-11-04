# scripts/local/checks.sh: this project's own checks. Sourced by scripts/check.sh, which supplies
#   run <name> <command...>   run one check, print ok/FAIL
#   full                      true in `check.sh full`
#   have <tool>               true when a command exists
# This file belongs to the project; template upgrades never touch it. Examples:
# run "no network in core" scripts/local/check-no-network.sh
# full && run "end-to-end" ./run-e2e.sh

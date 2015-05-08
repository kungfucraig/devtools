#
# Source this file to get all of the things.
#

if [ -z ${DT_DIR} ]; then
    echo "ERROR: DT_DIR not set"
    return
fi

export DT_CONFIG_DIR="${HOME}/.devtools"

source ${DT_DIR}/shellutil/go.sh
source ${DT_DIR}/shellutil/edit.sh
source ${DT_DIR}/shellutil/sandbox.sh
source ${DT_DIR}/shellutil/aliases.sh

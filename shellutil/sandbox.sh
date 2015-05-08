#
# Setup the idea of a sandbox where subdirectories under a common
# subdirectory name 'sandboxes'.
#

if [ -z "${DT_SANDBOX_ROOT}" ]; then
    export DT_SANDBOX_ROOT="${HOME}/dev"
fi

if [ -z ${DT_CURRENT_SANDBOX} ]; then
    export DT_CURRENT_SANDBOX="default"
fi

function dt_set_sandbox {
    if [ -z "$1" ]; then
        echo "ERROR: sandbox name not specified"
        return
    fi
    suggested="$1"

    if [ ! -e "${DT_SANDBOX_ROOT}/${suggested}" ]; then
       echo "ERROR: no such sandbox found in ${DT_SANDBOX_ROOT}"
    else
        export DT_SANDBOX=$suggested
        export DT_WORK_DIR=${DT_SANDBOX_ROOT}/${DT_SANDBOX}
    fi
}

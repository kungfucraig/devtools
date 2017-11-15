
# Setup the idea of a sandbox where subdirectories under a common
# subdirectory name 'sandboxes'.
#

export DT_SANDBOX_FILE="${DT_CONFIG_DIR}/sandbox"

if [ -z "${DT_SANDBOX_ROOT}" ]; then
    export DT_SANDBOX_ROOT="${HOME}/dev"
fi

function dt_read_sandbox {
    if [ -e $DT_SANDBOX_FILE ]; then
        export DT_SANDBOX_CURRENT=`cat $DT_SANDBOX_FILE`
    else
        export DT_SANDBOX_CURRENT="default"
    fi
    export DT_WORK_DIR=${DT_SANDBOX_ROOT}/${DT_SANDBOX_CURRENT}
    mkdir -p ${DT_WORK_DIR}
}

dt_read_sandbox

function dt_set_sandbox {
    if [ -z "$1" ]; then
        echo "ERROR: sandbox name not specified"
        return
    fi

    suggested="$1"

    if [ ! -e "${DT_SANDBOX_ROOT}/${suggested}" ]; then
       echo "ERROR: no such sandbox found in ${DT_SANDBOX_ROOT}"
    else
        echo $suggested > $DT_SANDBOX_FILE
        dt_read_sandbox
        # rebuild location table and go to work dir
        # TODO: make options out of these
        cd ${DT_WORK_DIR}
        me -r &
    fi
}

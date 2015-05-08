# This file defines a utility called "go". It works with a set of
# static go locations defined in a file specified by the environment
# variable DT_GO_FILE. The format of the file is as follows:

if [ -z "$DT_GO_FILE" ]; then
    export DT_GO_FILE=${DT_CONFIG_DIR}/go_locations
fi

##############################################
# GO
#
# Inspired by some Windows Power Shell code
# from Peter Provost (peterprovost.org)
#
# Here are some examples entries:
# work:${WORK_DIR}
# source:${SOURCE_DIR}
# dev:/c/dev
# object:${USER_OBJECT_DIR}
# debug:${USER_OBJECT_DIR}/debug
###############################################
function dt_go
{
    if [ -z "${DT_GO_FILE}" ]; then
        echo "The variable DT_GO_FILE is not set."
        return
    fi

    if [ ! -e "${DT_GO_FILE}" ]; then
        echo "The 'go file': '${DT_GO_FILE}' does not exist."
        return
    fi

    if [ -z "$1" ]; then
        echo "ERROR: expected the first argument to be the directory to go to"
        return
    fi

    IFS=$'\n'
    dest=""
    for entry in `cat ${DT_GO_FILE}`; do
        if [ "$1" = ${entry%%:*} ]; then
            dest=${entry##*:}
            break
        fi
    done

    if [ -z "${dest}" ]; then
        me=`which me`
        if [ -n ${me} ]; then
            dest=`$me -d "$1"`
        fi
    fi

    if [ -n "${dest}" ]; then
        cd `eval echo $dest`
    else
        echo "Invalid location, valid locations are:"
        cat ${DT_GO_FILE}
    fi
}

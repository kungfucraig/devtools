#
# Finds a file as go does, but instead of going to the directory with
# that file in it, this function invodes $EDITOR on it.
#

if [ -z "${EDITOR}" ]; then
    export EDITOR=vi
fi

function dt_edit {
    if [ -z "${EDITOR}" ]; then
        echo "ERROR: the variable editor must be set"
        return
    fi

    if [ -z "$1" ]; then
        echo "ERROR: expected the first argument to be the file to edit"
        return
    fi

    me=`which me`
    if [ -n ${me} ]; then
        f=`$me -f $@`
        if [ ! -z "${f}" ]; then
            command="$EDITOR $f"
            eval $command
        fi
    fi
}

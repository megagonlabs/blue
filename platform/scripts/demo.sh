#/bin/bash

# initialize positional args
POSITIONAL_ARGS=()

while [[ $# -gt 0 ]]; do
  case $1 in
    -e|--extension)
      EXTENSION="$2"
      # pass argument and value
      shift 
      shift 
      ;;
    -s|--searchpath)
      SEARCHPATH="$2"
      # pass argument and value
      shift 
      shift 
      ;;
    --default)
      # set default value
      DEFAULT=YES
      # pass value
      shift
      ;;
    -*|--*)
      echo "Unknown option $1"
      exit 1
      ;;
    *)
      POSITIONAL_ARGS+="$1 " 
      # pass 
      shift 
      ;;
  esac
done
# restore positional args
set -- "${POSITIONAL_ARGS[@]}" 

echo "FILE EXTENSION  = ${EXTENSION}"
echo "SEARCH PATH     = ${SEARCHPATH}"
echo "DEFAULT         = ${DEFAULT}"
echo "POSITIONAL_ARGS = ${POSITIONAL_ARGS}"

EOF

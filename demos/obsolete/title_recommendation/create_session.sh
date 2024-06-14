#/bin/bash
export sid=$(blue session --output json --query '$.id' create | tr -d '"')
echo $sid > .sid

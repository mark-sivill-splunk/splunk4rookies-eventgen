#!/usr/bin/env bash

export BUNDLE_DIR=$1

term_handler() {
  if [ $pid -ne 0 ]; then
    kill -SIGTERM "$pid"
    wait "$pid"
  fi
  exit 143; # 128 + 15 -- SIGTERM
}

trap 'kill ${!}; term_handler' SIGTERM

if [ "$DEBUG" = "1" ]
    then
     exec python -m splunk_eventgen -vv generate "$@"
     pid="$!"

    else
     exec python -m splunk_eventgen -v generate "$@"
     pid="$!"
fi

while true
do
  tail -f /dev/null & wait ${!}
done


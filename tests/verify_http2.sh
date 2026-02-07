#!/bin/bash

cp run.sh run_dryrun.sh
# Replace 'exec $CMD' with 'echo "CMD_TO_RUN: $CMD"'
sed -i 's/exec $CMD/echo "CMD_TO_RUN: $CMD"/' run_dryrun.sh
# Disable frontend build to speed up test and avoid node version issues
sed -i 's/build_frontend/# build_frontend/g' run_dryrun.sh

chmod +x run_dryrun.sh

echo "--- Test 1: HTTP/2 Enabled by default or generic ---"
CMD_OUT=$(./run_dryrun.sh)
if [[ "$CMD_OUT" == *"--http2"* ]]; then
    echo "PASS: HTTP/2 enabled by default"
else
    echo "FAIL: HTTP/2 NOT enabled by default"
    echo "Output: $CMD_OUT"
fi

echo "--- Test 2: HTTP/2 Disabled via env ---"
CMD_OUT=$(ENABLE_HTTP2=false ./run_dryrun.sh)
if [[ "$CMD_OUT" != *"--http2"* ]]; then
    echo "PASS: HTTP/2 disabled via env"
else
    echo "FAIL: HTTP/2 NOT disabled via env"
    echo "Output: $CMD_OUT"
fi

echo "--- Test 3: HTTP/2 Enabled via env ---"
CMD_OUT=$(ENABLE_HTTP2=true ./run_dryrun.sh)
if [[ "$CMD_OUT" == *"--http2"* ]]; then
    echo "PASS: HTTP/2 enabled via env"
else
    echo "FAIL: HTTP/2 NOT enabled via env"
    echo "Output: $CMD_OUT"
fi

rm run_dryrun.sh

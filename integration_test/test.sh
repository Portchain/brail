#!/usr/bin/env bash
# This integration test is designed to treat the brail binary as a black box

set -e
cd "$(dirname "$0")"

# Create a test repo
rm -rf test_repo
mkdir test_repo
cd test_repo

# Create a master branch with a brail directory and a brailconf file
git init 1>/dev/null
mkdir braildir
cp ../brailconf1.json .brailconf
touch braildir/.gitkeep
echo 'Hello a' > a.txt
echo 'Hello b' > b.txt
git add braildir/.gitkeep a.txt b.txt .brailconf
git commit -m 'commit 1' 1>/dev/null

# Create a feature branch
git checkout -b feature1 2>/dev/null

# Add a brail annotation
PYTHONPATH="../.." python3 ../../bin/brail feat -m add_file_c 1>/dev/null

# Check that a record has been written to the brail directory
if [[ $(diff <(ls braildir | wc) <(cat ../wc1.txt)) ]]; then
    echo "braildir contents are not as expected"
    exit 1
fi

# Commit and verify that brail diff produces the expected output
git commit -m 'commit 2' 1>/dev/null
if [[ $(diff <(PYTHONPATH="../.." python3 ../../bin/brail diff) <(cat ../output1.txt)) ]]; then
    echo "brail diff output is not as expected"
    exit 1
fi
echo 'Success'
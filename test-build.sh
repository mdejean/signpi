#!/bin/bash
# Build and install the package on the Pi, including unstaged changes
# Requires git-buildpackage to be installed on the pi
# Clone the repo on the Pi before using
set -e

REMOTE=user@signpi.local

rsync $(cut -d ' ' -f 1 debian/install) debian/*.service $REMOTE:~/signpi/

ssh $REMOTE /bin/bash -c '"
set -e
cd signpi
gbp dch --snapshot
gbp buildpackage --git-ignore-new
cd ..
sudo dpkg -i signpi_*.deb
rm signpi_*
"'

#!/bin/bash

echo "Installing the following software:"
echo "1) phantomjs"
echo ""
sudo apt install phantomjs

echo "Done"
echo ""
echo "Setting up bin links."
sudo ln -f -s $(pwd)/screenshot-html.py /usr/bin/screenshot-html

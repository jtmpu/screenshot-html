#!/usr/bin/env python
import subprocess
import argparse
import requests
import sys
import os

def main(args):
    '''
    Takes a screenshot of the destination URLs web page.
    Returns ??
    
    Args is expected to a dict containing:
     1) args["urls"] = [ "url1", ... ]
     2) args["basefolder"] = "<path-to-folder>" - folder to store screenshots

    Optional args:
     1) args["verbose"] = True - debug output
    
    URLs can be in variations of the following formats:
    1) 127.0.0.01
    2) example.com
    3) https://example.com
    4) 127.0.0.1:9000 
    '''
    verbose_enabled = "verbose" in args and args["verbose"] == True

    phantomjs_script_path = "/tmp/phantomjs_bootstrap.js"
    setup_base(args, phantomjs_script_path)
    urls = setup_urls(args["urls"]) 

    results = {}
    for url in urls:
        if verbose_enabled:
            print("[+] Fetching %s" % url)
        results[url] = {}
        result_path = os.path.abspath(args["basefolder"] + "/" + url_to_filename(url) + ".png")
        process = subprocess.Popen(["phantomjs", phantomjs_script_path, url, result_path], stdout=subprocess.PIPE)
        line = process.stdout.readline().strip()
        results[url]["path"] = result_path
        results[url]["status"] = line

        if verbose_enabled:
            print("[+] Done: %s " % line)
    return results

def plugin_run(args):
    '''
    Run the tool as a plugin, using the given args to execute
    '''
    return main(args)

def parse_cmdline():
    description="""Testar testsson.
    """
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("-u", "--urls", help="The url to take a screenshot of.", nargs="*", default=[])
    parser.add_argument("-r", "--read", help="Read urls from the specified file.")
    parser.add_argument("-f", "--format", help="The format to use for the output", choices=["json", "grep"], default="grep")
    parser.add_argument("-b", "--basefolder", help="The folder to place the screenshots in.", default="./screenshots")
    parser.add_argument("-v", "--verbose", help="Outputs the status of the script.", action="store_true")
    args = parser.parse_args()
    
    if args.read:
        with open(args.read, "r") as f:
            lines = f.readlines()
            args.urls.extend(map(lambda x: x.strip(), lines))
    elif args.urls == []: 
        lines = sys.stdin.readlines()
        args.urls.extend(map(lambda x: x.strip(), lines))

    return args

def setup_base(args, payload_path):
    '''
    Prepare the resources required.
    '''
    javascript_payload = """
var page = require("webpage").create();
var system = require("system");
var args = system.args;
page.open(args[1], function(status) {
    if (status == "success") {
        page.render(args[2]);
    } 
    console.log(status)
    phantom.exit();
});
"""
    with open(payload_path, "w") as f:
        f.write(javascript_payload)

    if not os.path.exists(args["basefolder"]):
       os.makedirs(args["basefolder"]) 

def url_to_filename(url):
    return url.replace("/", "_").replace("\\", "_").replace("?", "_") 

def setup_urls(urls):
    ret = []
    for url in urls:
        if not url.startswith("http"):
            ret.append("http://" + url)
            ret.append("https://" + url) 
        else:
            ret.append(url)
    return list(set(ret))

if __name__ == "__main__":
    args = parse_cmdline()
    results = main(vars(args))
    print("CLI Done.")

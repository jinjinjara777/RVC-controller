"""Install build/test dependencies into this workspace; no global install."""
from pathlib import Path
import argparse
import os
import subprocess
import sys
import urllib.request
import zipfile
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--browser',action='store_true');args=parser.parse_args()
tools=ROOT/'.tools';tools.mkdir(exist_ok=True)
packages=['cmake==4.4.4']
if args.browser: packages+=['playwright==1.64.1']
subprocess.run([sys.executable,'-m','pip','install','--target',str(tools/'python'),'--upgrade',*packages],check=True)
if not (tools/'googletest-1.15.2').exists():
    archive=tools/'googletest.zip'
    urllib.request.urlretrieve('https://codeload.github.com/google/googletest/zip/refs/tags/v1.15.2',archive)
    with zipfile.ZipFile(archive) as bundle:
        for member in bundle.infolist():
            if not (tools/member.filename).resolve().is_relative_to(tools.resolve()): raise ValueError('Invalid archive path')
        bundle.extractall(tools)
if args.browser:
    env=dict(os.environ,PYTHONPATH=str(tools/'python'),PLAYWRIGHT_BROWSERS_PATH=str(tools/'browsers'))
    subprocess.run([sys.executable,'-m','playwright','install','chromium'],env=env,check=True)
print('Local dependencies ready.')

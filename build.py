#!/usr/bin/env python3
"""
Build HRH_AFA_V1.html from source files in src/

Usage:
    python3 build.py

Source files:
    src/template.html  - HTML structure with %%STYLES%% and %%SCRIPTS%% placeholders
    src/styles.css     - CSS (injected into <style> tag)
    src/app.js         - JavaScript (injected into <script> tag)

Output:
    HRH_AFA_V1.html    - The complete single-file app
"""

import os

SRC_DIR = os.path.join(os.path.dirname(__file__), 'src')
OUTPUT = os.path.join(os.path.dirname(__file__), 'HRH_AFA_V1.html')

with open(os.path.join(SRC_DIR, 'template.html'), 'r') as f:
    template = f.read()

with open(os.path.join(SRC_DIR, 'styles.css'), 'r') as f:
    styles = f.read()

with open(os.path.join(SRC_DIR, 'app.js'), 'r') as f:
    scripts = f.read()

output = template.replace('%%STYLES%%', styles).replace('%%SCRIPTS%%', scripts)

with open(OUTPUT, 'w') as f:
    f.write(output)

print(f'Build complete: {OUTPUT}')
print(f'  styles.css : {len(styles.splitlines())} lines')
print(f'  app.js     : {len(scripts.splitlines())} lines')
print(f'  output     : {len(output.splitlines())} lines total')

#!/usr/bin/env python3

from flask import Flask, render_template, request
import itertools
import subprocess

app = Flask('web-apertium')

#AVAILABLE_TRANSLATION_MODES = [] # [(lang1, lang2, code, path), ...]
AVAILABLE_TRANSLATION_MODES = {
    'eng': {
        'spa': ('eng-spa', '/home/daniel/apertium/apertium-data/apertium-eng-spa'),
        'cat': ('eng-cat', '/home/daniel/apertium/apertium-data/apertium-eng-cat'),
    },
    'spa': {
        'eng': ('spa-eng', '/home/daniel/apertium/apertium-data/apertium-eng-spa'),
    },
}
DETECT_ENABLED = False
LANGUAGE_NAMES = { # TODO: load from somewhere
    'eng': 'English',
    'spa': 'Spanish',
    'tur': 'Turkish',
    'cat': 'Catalan',
}

@app.get('/')
def main():
    return render_template('index.html')

def codes_to_name_list(codes):
    return sorted([(LANGUAGE_NAMES[c], c) for c in set(codes)])

@app.get('/target_langs')
def get_target_langs():
    source = request.args['src']
    target = request.args['tgt']
    if source and source != 'detect':
        langs = codes_to_name_list(AVAILABLE_TRANSLATION_MODES[source].keys())
    else:
        langs = codes_to_name_list(itertools.chain.from_iterable(
            d.keys() for d in AVAILABLE_TRANSLATION_MODES.values()))
    ret = []
    for name, code in langs:
        sel = ' selected' if code == target else ''
        # TODO: escape
        ret.append(f'<option value="{code}"{sel}>{name}</option>')
    return '\n'.join(ret)

@app.get('/translate')
def get_translate(source=None, target=None):
    modes = AVAILABLE_TRANSLATION_MODES
    srcLangs = codes_to_name_list(modes.keys())
    if source is None:
        if DETECT_ENABLED:
            source = 'detect'
        elif srcLangs:
            source = srcLangs[0][1]
        else:
            return 'No languages available!'
    return render_template('translate.html',
                           srcLangs=srcLangs, detect=DETECT_ENABLED)

@app.post('/translate')
def post_translate():
    source = request.form['src']
    target = request.form['tgt']
    mode, path = AVAILABLE_TRANSLATION_MODES.get(source, {}).get(target, (None, None))
    if not mode:
        return '[[Something went wrong]]'
    cmd = ['apertium']
    if path:
        cmd += ['-d', path]
    cmd.append(mode)
    proc = subprocess.run(cmd, input=request.form['input'], encoding='utf-8',
                          capture_output=True)
    return proc.stdout

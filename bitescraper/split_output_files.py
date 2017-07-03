# script to split massive JSON object into useful CSV files for neo4j
import argparse
import json
import pandas as pd
from termcolor import colored

try:
    from pathlib import Path
except ImportError:
    print(colored('This script is only compatibale with python 3', 'magenta'))
    exit()


parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser()
parser.add_argument("json_file", help="path to JSON file")
args = parser.parse_args()

try:
    # make sure file is speficied
    assert args.json_file is not None and args.json_file != ''
    fn = args.json_file
    # open it and read it to JSON
    with open(fn) as fh:
        d = fh.read()
    records = json.loads(d)
except AssertionError:
    print(colored('ERROR!', 'magenta'), 'You must specify a filename to split.')
    exit()
except FileNotFoundError:
    print(colored('ERROR!', 'magenta'), 'File', colored(fn, 'cyan'), 'not found!')
    exit()
except json.decoder.JSONDecodeError:
    print(colored('ERROR!', 'magenta'), 'There was a problem with the specified file:', colored(fn, 'cyan'))
    exit()
else:
    print(colored('Loaded and parsed file OK:', 'green'), args.json_file)

# setup arrays to take data
pubs, comments = [], []

# split
for r in records:
    if 'name' in r:
        # it's a pub
        pubs.append(r)
    elif 'comment' in r:
        # it's a comment
        comments.append(r)
    else:
        print(colored('DEBUG: Error processing record', 'cyan'), r)
else:
    del r

print(colored('Parsed OK:', 'green'),
    'found',
    colored(format(len(pubs), ',d'), 'cyan'),
    'pubs, and',
    colored(format(len(comments), ',d'), 'cyan'),
    'comments.')

# work out the filenames to output
print(colored('Finding safe output filenames', 'yellow'))
file_int = 0
def make_filename(f : str, i : int) -> str:
    """Return a filename based on name and counter"""
    return 'output-{0}-{1:04d}.csv'.format(f, i)
while Path(make_filename('comments', file_int)).exists() \
    or Path(make_filename('pubs', file_int)).exists():
    file_int += 1
comments_fn, pubs_fn = make_filename('comments', file_int), make_filename('pubs', file_int)

print(colored('Found filenames OK:', 'green'),
    colored(pubs_fn, 'cyan'),
    colored(comments_fn, 'cyan'))

# export files
def to_kb(b : int) -> str:
    """Format an integer of bytes as a KB string."""
    return '{0:,d} Kb'.format(int(b / 1000))

print(colored('Exporting split files.', 'yellow'))
df_pubs = pd.DataFrame(pubs)
df_pubs.to_csv(pubs_fn)
print(
    colored('Exported pubs OK:', 'green'),
    colored(pubs_fn, 'cyan'),
    to_kb(Path(pubs_fn).stat().st_size))
df_comments = pd.DataFrame(comments)
df_comments.to_csv(comments_fn)
print(
    colored('Exported comments OK:', 'green'),
    colored(comments_fn, 'cyan'),
    to_kb(Path(comments_fn).stat().st_size))

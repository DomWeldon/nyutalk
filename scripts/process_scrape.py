# script to split massive JSON object into useful CSV files for neo4j
import argparse
from collections import Counter
from datetime import datetime
from itertools import groupby
import json
import nltk
from operator import itemgetter
import pandas as pd
from string import punctuation, printable
from termcolor import colored
import time
import unicodedata

from common import *

nltk.download('stopwords')

# 1. USER INPUT AND SCRIPT SETUP

# take command from user
parser = argparse.ArgumentParser()
parser = argparse.ArgumentParser()
parser.add_argument("json_file", help="path to JSON file")
args = parser.parse_args()

# load the specified json object
records = load_json_file(args.json_file)

# 2. SPLIT APART PUB AND COMMENT DATA

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

# 3. GROUP TOGETHER COMMENTS BY PUB AS AN INTERNAL DICTIONARY FOR OUR USE

print(colored('Grouping comments', 'yellow'))
keyfunc = itemgetter('source_pub_id')
grouped_comments = groupby(sorted(comments, key = keyfunc), keyfunc)
comments_dict = { x[0]: [y for y in x[1] ] for x in grouped_comments }
del grouped_comments, keyfunc
print(colored('Comments grouped OK', 'green'))

# 4. ITERATE THROUGH PUBS TO:
#    A) SEE IF THEY HAVE A POSTCODE
#    B) EXTRACT MOST COMMON WORDS FROM THEIR COMMENTS
print(colored('Finding postcodes in addresses and getting pub keywords', 'yellow'))

# required for postcode search
is_valid_postcode = get_postcode_matcher()
not_found_pc_count, found_pc_count = 0, 0
# required for keywords:
stopwords = set(nltk.corpus.stopwords.words('english'))

# start the iteration
for i, p in enumerate(pubs):
    # find a postcode
    try:
        pc = p['address'].split(',')[-1].strip()
        assert is_valid_postcode(pc)
        found_pc_count += 1
    except:
        pc = None
        not_found_pc_count += 1
    pubs[i]['postcode'] = pc
    if p['source_pub_id'] in comments_dict:
        keyword_counter = Counter()
        for c in comments_dict[p['source_pub_id']]:
            # count the keywords
            comment_clean = ''.join([
                c
                for c in c['comment'] \
                if c not in punctuation and c in printable])
            spl = comment_clean.split()
            keyword_counter.update(
                w.lower().rstrip(punctuation)
                for w in spl \
                    if w.lower().rstrip(punctuation) not in stopwords \
                        and w not in punctuation

            )
        pubs[i]['keywords'] = cypher_collection_syntax([
            '{0}: {1}'.format(x[0], x[1]) for x in keyword_counter.most_common(15)
        ])
    else:
        pubs[i]['keywords'] = None
    # tidy up features
    pubs[i]['facilities'] = cypher_collection_syntax(
        [f[0:f.index('(')].strip() if '(' in f else f for f in p['facilities']]
    )
    pubs[i]['nearby_tube_stations'] = cypher_collection_syntax([x['name'] for x in p['nearby_tube_stations']])
print(
    'Postcode search finished:',
    colored('found {0:,d}'.format(found_pc_count)),
    colored('not found {0:,d}'.format(not_found_pc_count)))

# 5. USE EXTERNAL DATA TO LOOKUP THEIR LAT/LONG BASED ON POSTCODE
with BulkPostCodeParser([ p['postcode'] for p in pubs if p['postcode'] is not None ]) as postcode_lookup:
    pcl_count = postcode_lookup.parse()

    print(
        'Postcode lookup finished:',
        colored('found {0:,d}'.format(pcl_count.successes)),
        colored('not found {0:,d}'.format(pcl_count.failures)))

    print(colored('Storing successes with pubs.', 'yellow'))
    for i, p in enumerate(pubs):
        try:
            pc = postcode_lookup[p['postcode']]
            pubs[i]['latitude'] = pc['latitude']
            pubs[i]['longitude'] = pc['longitude']
            pubs[i]['parliamentary_constituency'] = pc['parliamentary_constituency']
            pubs[i]['admin_ward'] = pc['admin_ward']
        except KeyError:
            pass
    else:
        pass

# 6. PARSE COMMENT DATES NICELY
print(colored('Processing and sorting comment dates.', 'yellow'))
for i, c in enumerate(comments):
    try:
        c['created_timestamp'] = int(time.mktime(datetime.strptime(c['created'], '%Y-%m-%d %H:%M:%S').timetuple()))
    except KeyError:
        pass
        #print(colored('DEBUG: no created found', 'cyan'), c)
        c['created_timestamp'] = 0
    except ValueError:
        print(colored('could not parse date:', 'red'), c['created'])
        c['created_timestamp'] = 0

comments.sort(key = itemgetter('created_timestamp'), reverse = False)
print(colored('Comment dates processed and sorted OK.', 'green'))

# 7. PREPARE TO OUTPUT THE FILES
# work out the filenames to output
print(colored('Finding safe output filenames', 'yellow'))
file_int = 0
while Path(make_filename('comments', file_int)).exists() \
    or Path(make_filename('pubs', file_int)).exists():
    file_int += 1
comments_fn, pubs_fn = make_filename('comments', file_int), make_filename('pubs', file_int)

print(colored('Found filenames OK:', 'green'),
    colored(pubs_fn, 'cyan'),
    colored(comments_fn, 'cyan'))

# 8. SAVE OUTPUT

# export files
print(colored('Exporting split files.', 'yellow'))
df_pubs = pd.DataFrame(pubs)
df_pubs.to_csv(pubs_fn, index_label = 'import_offset')
print(
    colored('Exported pubs OK:', 'green'),
    colored(pubs_fn, 'cyan'),
    to_kb(Path(pubs_fn).stat().st_size))
df_comments = pd.DataFrame(comments)
df_comments.to_csv(comments_fn, index_label = 'import_offset')
print(
    colored('Exported comments OK:', 'green'),
    colored(comments_fn, 'cyan'),
    to_kb(Path(comments_fn).stat().st_size))

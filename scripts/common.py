import collections
import json
import math
import re
import requests
try:
    from pathlib import Path
except ImportError:
    print(colored('This script is only compatibale with python 3', 'magenta'))
    exit()
from termcolor import colored

# NATURAL LANGUAGE PROCESSING

# POSTCODE FUNCTIONS
def get_postcode_matcher():
    """Get a regex match function for a postcode"""
    pcr = r'^(GIR ?0AA|[A-PR-UWYZ]([0-9]{1,2}|([A-HK-Y][0-9]([0-9ABEHMNPRV-Y])?)|[0-9][A-HJKPS-UW]) ?[0-9][ABD-HJLNP-UW-Z]{2})$'
    return re.compile(pcr).match

class PostCodeQueryError(Exception): pass

PostCodeLookupCount = collections.namedtuple('PostCodeLookupCount', [ 'successes', 'failures' ])

class BulkPostCodeParser(collections.UserDict):
    api_endpoint = 'http://api.postcodes.io/postcodes'
    cache_file = 'data/postcodes.json'
    batch_size = 100

    def __init__(self, postcodes : list, cache_active = True): # -> BulkPostCodeParser
        """Take a list of postcodes to lookup"""
        self.cache_active = cache_active
        self.arg_postcodes = list({ pc for pc in postcodes if pc is not None })
        self.data = {}
        self.error_postcodes = []
        # load the cache


    def load_cache(self):
        """load cache from file"""
        try:
            with open(self.cache_file, 'r') as _:
                d = json.loads(_.read())
                self.data = d['data']
                self.error_postcodes = d['error_postcodes']
        except FileNotFoundError:
            pass

    def save_cache(self):
        """save cache to file"""
        with open(self.cache_file, 'w') as _:
            _.write(json.dumps({
                'data': self.data,
                'error_postcodes': self.error_postcodes,
            }))

    def __enter__(self):
        if self.cache_active:
            self.load_cache()

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.cache_active:
            self.save_cache()

        return self

    def parse(self): # -> BulkPostCodeParser
        """Get details for the postcodes from web service."""
        # do this in batches
        self.arg_postcodes = [pc for pc in self.arg_postcodes if pc not in self and pc not in self.error_postcodes]
        for i in range(math.ceil(len(self.arg_postcodes) / self.batch_size)):
            # calculate the splice to use this batch
            batch_slice = slice(
                self.batch_size * i,
                min(
                    self.batch_size * (i + 1),
                    len(self.arg_postcodes)
                ),
                1
            )
            print(batch_slice)
            if batch_slice.stop - batch_slice.start > 1:
                # marke the request and parse it
                self._parse_bulk_api_response(
                    requests.post(
                        self.api_endpoint,
                        data = {
                            'postcodes': self.arg_postcodes[batch_slice]
                        }
                    )
                )
            else:
                # has to use the single postcode API
                self._parse_single_api_response(
                    requests.get(
                        self.api_endpoint + '/' + self.arg_postcodes[batch_slice][0],
                    ),
                    postcode = self.arg_postcodes[batch_slice][0]
                )

        return PostCodeLookupCount(
            len(self),
            len(self.error_postcodes)
        )

    def _parse_bulk_api_response(self, r : requests.Response):
        """Take response and put it into internal dictionary."""
        r = json.loads(r.text)
        try:
            # response was successful
            assert r['status'] == 200
            for pc in r['result']:
                if pc['result'] is not None:
                    self.data[pc['query']] = pc['result']
                else:
                    self.error_postcodes.append(pc['query'])

        except AssertionError:
            raise PostCodeQueryError()

    def _parse_single_api_response(self, r : requests.Response, postcode = None):
        """Take response from single API call and put it into internal dictionary."""
        r = json.loads(r.text)
        try:
            # response was successful
            assert r['status'] == 200
            if r['result'] is not None:
                self.data[r['result']['postcode']] = r['result']
            elif postcode is not None:
                self.error_postcodes.append(postcode)

        except AssertionError:
            raise PostCodeQueryError()

def make_filename(f : str, i : int) -> str:
    """Return a filename based on name and counter, will figure out what directory we are in"""

    return 'data/output-{0}-{1:04d}.csv'.format(f, i)

def to_kb(b : int) -> str:
    """Format an integer of bytes as a KB string."""
    return '{0:,d} Kb'.format(int(b / 1000))


def load_json_file(fn):
    """Load a JSON file into the program, with nice error messages."""
    try:
        # make sure file is speficied
        assert fn is not None and fn != ''
        # open it and read it to JSON
        with open(fn) as fh:
            d = fh.read()
        d = json.loads(d)
    except AssertionError:
        print(colored('ERROR!', 'magenta'), 'You must specify a filename to process.')
        exit()
    except FileNotFoundError:
        print(colored('ERROR!', 'magenta'), 'File', colored(fn, 'cyan'), 'not found! Ensure you are running the script from the root directory.')
        exit()
    except json.decoder.JSONDecodeError:
        print(colored('ERROR!', 'magenta'), 'There was a problem with the specified file:', colored(fn, 'cyan'))
        exit()
    else:
        print(colored('Loaded and parsed file OK:', 'green'), fn)

    return d

#!/usr/bin/env python3

#
# Written in 2016, updated in 2020 and 2022 by Calvin Ardi <calvin@isi.edu>
#
# To the extent possible under law, the author(s) have dedicated all copyright
# and related and neighboring rights to this software to the public domain
# worldwide. This software is distributed without any warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication along
# with this software.
#
# If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
#

"""This snippet prints out an unmodified proofpoint "protected" (i.e., mangled) URL.

Usage:
    decode.py [-h] [--debug] [--unquote] [--verbose] url

Args:
    url         a proofpoint url (usually starts with urldefense.proofpoint.com or urldefense.com)

Optional Args:
    -h, --help     show this help message and exit
    --debug, -d    debugging trace mode (via pdb)
    --unquote      unquote cleaned URL (e.g., '%7B' -> '{')
    --verbose, -v  print more debugging output

Returns:
    A decoded (and optionally, unquoted) URL string.

"""

import argparse
import base64
import re
import sys
import pdb
import urllib.request, urllib.parse, urllib.error

DEBUG = False


#
# proofpoint "protected" v2 URLs take the form of:
#
#   https://urldefense.proofpoint.com/v2/url?[params]
#   https://urldefense.com/v2/url?[params]
#
# where [params] is described below
#
# TODO decode parameters
#
#  c := constant (per organization)
#  d := constant (per organization)
#  e := always empty?
#  m := ?
#  r := unique identifier tied to email address
#  s := ?
#  u := safe-encoded URL
#
#  'm' might be a hash of the URL or some metadata
#  's' might be a signature or checksum
#
def decode_ppv2(mangled_url):
    query = urllib.parse.urlparse(mangled_url).query
    param = urllib.parse.parse_qs(query)

    if "u" not in param:
        sys.exit("ERROR: check if URL is a proofpoint URL")
    else:
        u = param["u"][0].replace("-", "%").replace("_", "/")
        cleaned_url = urllib.parse.unquote(u)

    return cleaned_url


#
# proofpoint "protected" v3 URLs take the form of:
#
#   https://urldefense.com/v3/__[mangled_url]__;[b64-encoded_replacement_string]!![organization_id]![unique_identifier]$
#
# many symbols in the original URL are replaced with `*` in the [mangled_url] and
# copied over to the [b64-encoded_replacement_string].
#
# example:
#   mangled: http://www.example.com/*test*test
# 	replacement string: ##
# 	cleaned: http://www.example.com/#test#test
#
# however, if there are >=2 symbols that are encoded, it's mapped to something like
# `**A`, `**B`, and so on.
#
# `**` means that there are at least 2 characters in a row
# The character following is the number of characters (A == 2, B == 3, etc.)
#
# example:
#   mangled: http://www.example.com/**Dtest*test
#   replacement string: ######
#   cleaned: http://www.example.com/#####test#test
#
# after a "run" of a maximum of 65 characters, it simply repeats itself.
#
# example (replacement string consists of all `#`):
#   mangled: http://www.example.com/**_test
# 	number of #: 65
# 	cleaned: http://www.example.com/#################################################################test
#
# example (replacement string consists of all `#`):
#   mangled: http://www.example.com/**_*test
# 	number of #: 66
# 	cleaned: http://www.example.com/##################################################################test
#
# example (replacement string consists of all `#`):
#   mangled: http://www.example.com/**_**Atest
# 	number of #: 67
# 	cleaned: http://www.example.com/###################################################################test
#
# example (replacement string consists of all `#`):
#   mangled: http://www.example.com/**_**_test
# 	number of #: 130
# 	cleaned: http://www.example.com/##################################################################################################################################test
#
# the [organization_id] is a unique string per organization
# XXX unknown as to how this is derived
#
# the [unique_identifier] is tied to the recipient or sender email address
# (depending on whether the URL was rewritten inbound or outbound)
# XXX unknown as to how this is derived
#

replacement_str_mapping = {
    "A": 2,
    "B": 3,
    "C": 4,
    "D": 5,
    "E": 6,
    "F": 7,
    "G": 8,
    "H": 9,
    "I": 10,
    "J": 11,
    "K": 12,
    "L": 13,
    "M": 14,
    "N": 15,
    "O": 16,
    "P": 17,
    "Q": 18,
    "R": 19,
    "S": 20,
    "T": 21,
    "U": 22,
    "V": 23,
    "W": 24,
    "X": 25,
    "Y": 26,
    "Z": 27,
    "a": 28,
    "b": 29,
    "c": 30,
    "d": 31,
    "e": 32,
    "f": 33,
    "g": 34,
    "h": 35,
    "i": 36,
    "j": 37,
    "k": 38,
    "l": 39,
    "m": 40,
    "n": 41,
    "o": 42,
    "p": 43,
    "q": 44,
    "r": 45,
    "s": 46,
    "t": 47,
    "u": 48,
    "v": 49,
    "w": 50,
    "x": 51,
    "y": 52,
    "z": 53,
    "0": 54,
    "1": 55,
    "2": 56,
    "3": 57,
    "4": 58,
    "5": 59,
    "6": 60,
    "7": 61,
    "8": 62,
    "9": 63,
    "-": 64,
    "_": 65,
}


def decode_ppv3(mangled_url, unquote_url=False):
    # we don't use urlparse here because the mangled url confuses the function
    # (e.g., it's not sure if the query belongs to the inner or our URL)
    parsed_url = mangled_url

    # extract URL between `__`s (e.g., /v3/__https://www.example.com__;Iw!![organization_id]![unique_identifier]$)
    p = re.compile("__(.*)__;(.*)!!")
    ps = p.search(parsed_url)

    url = ps.group(1)
    DEBUG and print(url)

    # get string of b64-encoded replacement characters (e.g., "Iw" in  /v3/__https://www.example.com__;Iw!![organization_id]![unique_identifier]$)
    replacement_b64 = ps.group(2)

    # if the replacement string is empty, return extracted URL
    if len(replacement_b64) == 0:
        return url

    DEBUG and print(replacement_b64)

    # base64 decode replacement string
    replacement_str = (base64.b64decode(replacement_b64 + "==")).decode(
        "utf-8"
    )  # b64decode ignores any extra padding
    DEBUG and print(replacement_str)

    # replace `*` with actual symbols
    replacement_list = list(replacement_str)
    url_list = list(url)

    offset = 0
    # this regex says: find ("*" but not "**") or ("**A", "**B", "**C", ..., "**-", "**_")
    for m in re.finditer("(?<!\*)\*(?!\*)|\*{2}[A-Za-z0-9-_]", url):
        DEBUG and print("%d %d %s" % (m.start(), m.end(), m.group(0)))

        if m.group(0) == "*":
            # we only need to replace one character here
            url_list[m.start() + offset] = replacement_list.pop(0)
        elif m.group(0).startswith("**"):
            # we need to replace a certain number of characters
            # e.g., "foobar**Dfoo" --> "foobar#####foo"
            num_chars = replacement_str_mapping[m.group(0)[-1]]
            DEBUG and print("replacing {num_chars}".format(num_chars=num_chars))

            # replace "**[A-Za-z0-9-_]" with replacement characters
            replacement_chars = list()
            for i in range(num_chars):
                replacement_chars.append(replacement_list.pop(0))

            # replace a sub-list with a replacement list
            # works nicely even if the replacement list is shorter than the sub-list
            url_list[m.start() + offset : m.end() + offset] = replacement_chars

            # update offset as we're modifying url_list in place
            # (m.start() and m.end() refer to positions in the original `url` string)
            offset += num_chars - 3
        else:
            # shouldn't get here
            DEBUG and print("shouldn't get here")
            pass

    cleaned_url = "".join(url_list)

    # we don't know whether the original URL was quoted or not, so
    # give the option to unquote the URL.
    if unquote_url:
        cleaned_url = urllib.parse.unquote(cleaned_url)

    return cleaned_url


def decode(mangled_url, unquote_url=False):
    parsed_url = urllib.parse.urlparse(mangled_url)

    if (
        (
            (
                parsed_url.netloc == "urldefense.proofpoint.com"
                or parsed_url.netloc == "urldefense.com"
            )
            and parsed_url.path.startswith("/v2/")
        )
        or (parsed_url.path.startswith("urldefense.proofpoint.com/v2/"))
        or (parsed_url.path.startswith("urldefense.com/v2/"))
    ):
        cleaned_url = decode_ppv2(mangled_url)
    elif (
        parsed_url.netloc == "urldefense.com" and parsed_url.path.startswith("/v3/")
    ) or (parsed_url.path.startswith("urldefense.com/v3/")):
        cleaned_url = decode_ppv3(mangled_url, unquote_url)
    else:
        # assume URL hasn't been mangled
        return mangled_url

    return cleaned_url


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="decode proofpoint-mangled URLs")
    parser.add_argument(
        "--debug",
        "-d",
        help="debugging trace mode (via pdb)",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--unquote",
        action="store_true",
        default=False,
        help="unquote cleaned URL (e.g., '%%7B' -> '{')",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        help="print more debugging output",
        action="store_true",
        default=False,
    )
    parser.add_argument("url", type=str, help="URL to clean and decode")
    args = parser.parse_args()

    if args.verbose:
        DEBUG = True

    if args.debug:
        DEBUG = True
        pdb.set_trace()

    cleaned_url = decode(args.url, args.unquote)

    print(cleaned_url)

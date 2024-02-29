#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :

#
# Written in 2016, updated in 2022 by Calvin Ardi <calvin@isi.edu>
#
# To the extent possible under law, the author(s) have dedicated all copyright
# and related and neighboring rights to this software to the public domain
# worldwide. This software is distributed without any warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication along
# with this software.
# If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
#
#
# summary: normalizes malformed proofpoint urls and prints to stdout
#
# usage: cat email_with_headers | ./get_urls.py
#   or in mutt (or your favorite email client), pipe email to this script
#

import base64
import email, email.policy
import fileinput
import re
import sys
import urllib.request, urllib.parse, urllib.error

DEBUG = False
# source: https://gist.github.com/gruber/8891611
URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""


#
# proofpoint "protected" v2 URLs take the form of:
#
#   https://urldefense.proofpoint.com/v2/url?[params]
#   https://urldefense.{com,us}/v2/url?[params]
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
# however, if there are >=2 symbols/bytes that are encoded, it's mapped to
# something like `**A`, `**B`, and so on.
#
# `**` means that there are at least 2 bytes to replace
# The character following is the number of bytes (A == 2, B == 3, etc.)
#
# example:
#   mangled: http://www.example.com/**Dtest*test
#   replacement string: ######
#   cleaned: http://www.example.com/#####test#test
#
# after a "run" of a maximum of 65 bytes, it simply repeats itself.
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

    if ps is None:
        DEBUG and print("%s is not a valid URL?" % parsed_url)

        # return as is
        return parsed_url

    url = ps.group(1)
    DEBUG and print(url)

    # get string of b64-encoded replacement characters (e.g., "Iw" in  /v3/__https://www.example.com__;Iw!![organization_id]![unique_identifier]$)
    replacement_b64 = ps.group(2)

    # if the replacement string is empty, return extracted URL
    if len(replacement_b64) == 0:
        return url

    DEBUG and print("replacement b64 = %s" % replacement_b64)

    # base64 decode replacement string
    #
    # use `urlsafe_b64decode` as the base64-encoded string
    # uses - and _ instead of + and /, respectively.
    #
    # See Section 5 in RFC4648
    # <https://www.rfc-editor.org/rfc/rfc4648.html#page-7>.
    replacement_str = (base64.urlsafe_b64decode(replacement_b64 + "==")).decode(
        "utf-8"
    )  # b64decode ignores any extra padding
    DEBUG and print(
        "replacement string = %s (%d)"
        % (replacement_str, len(replacement_str.encode("utf-8")))
    )

    # XXX just some debugging code
    # for i in range(len(replacement_str)+1):
    #    test = replacement_str[0:i]
    #    print(f"{test} {len(test.encode('utf-8'))}")

    # replace `*` with actual symbols
    replacement_list = list(replacement_str)
    url_list = list(url)

    DEBUG and print("replacement list = %s" % replacement_list)

    offset = 0
    save_bytes = 0
    # this regex says: find ("*" but not "**") or ("**A", "**B", "**C", ..., "**-", "**_")
    for m in re.finditer(r"(?<!\*)\*(?!\*)|\*{2}[A-Za-z0-9-_]", url):
        DEBUG and print("%d %d %s" % (m.start(), m.end(), m.group(0)))

        if m.group(0) == "*":
            # we only need to replace one character here
            url_list[m.start() + offset] = replacement_list.pop(0)
        elif m.group(0).startswith("**"):
            # we need to replace a certain number of bytes
            # e.g., "foobar**Dfoo" --> "foobar#####foo"
            num_bytes = replacement_str_mapping[m.group(0)[-1]]

            DEBUG and print(f"replacing {num_bytes} + {save_bytes} bytes")

            if save_bytes != 0:
                num_bytes += save_bytes
                save_bytes = 0  # reset
            DEBUG and print(f"replacing {num_bytes} bytes total")

            # replace "**[A-Za-z0-9-_]" with replacement characters
            replacement_chars = list()

            i = 0
            while i < num_bytes:
                # previously we assumed that the replacement_str_mapping
                # referred to the number of characters, but it actually
                # represents the number of bytes to copy over, given the UTF-8
                # encoding. so we replace the for loop with a while loop and
                # increment a counter with the size of each character being
                # replaced.
                replacement_char = replacement_list.pop(0)
                replacement_chars.append(replacement_char)
                i += len(replacement_char.encode("utf-8"))

                DEBUG and print(
                    f"the character {replacement_char} takes {len(replacement_char.encode('utf-8'))} bytes - running total: {i}"
                )

                # there seems to be an edge case at the boundaries: if we have
                # a long consecutive list of non-ascii characters to replace,
                # pp seems to break it up into segments of length 65 (e.g.,
                # num_bytes % 65). this doesn't quite work if each character is
                # of size 2, and we'll hit an empty list sooner than later and
                # get an error.
                #
                # we will resolve this by checking the _next_ character in the
                # list and checking if its size will be greater than (num_bytes
                # - i), where `i` is the current number of bytes we've replaced
                # so far. if so, "save" the difference and add it on to the
                # next segment.
                #
                # for example, if we have 124 bytes to replace, pp will break
                # it up into 65 (`**_`) and 59 (`**5`). all of the replacement
                # characters are 2 bytes, which means when we get to byte 64,
                # we have 1 byte left. similarly the 59 bytes in the next
                # segment doesn't make sense, because again all replacement
                # characters are 2 bytes. so we'll "save" the 1 byte and add it
                # on to the next segment (i.e., we're really treating this as
                # segments of 64 (`**-`) and 60 (`**6`)
                #
                # (presumably we could also search for and combine sequences of
                # replacement strings, i.e., if we see `**_**5`, we can combine
                # the two and add them together to get 65+59=124, and so on.)
                #
                if len(replacement_list) != 0:
                    next_replacement_char = replacement_list[0]
                    next_replacement_char_size = len(
                        next_replacement_char.encode("utf-8")
                    )

                    if next_replacement_char_size > (num_bytes - i):
                        # save the difference and add it to the next segment.
                        save_bytes = num_bytes - i
                        # break out of loop
                        i += save_bytes

            # replace a sub-list with a replacement list
            # works nicely even if the replacement list is shorter than the sub-list
            url_list[m.start() + offset : m.end() + offset] = replacement_chars

            # update offset as we're modifying url_list in place
            # (m.start() and m.end() refer to positions in the original `url` string)
            offset += len(replacement_chars) - 3
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
                or parsed_url.netloc == "urldefense.us"
            )
            and parsed_url.path.startswith("/v2/")
        )
        or (parsed_url.path.startswith("urldefense.proofpoint.com/v2/"))
        or (parsed_url.path.startswith("urldefense.com/v2/"))
        or (parsed_url.path.startswith("urldefense.us/v2/"))
    ):
        cleaned_url = decode_ppv2(mangled_url)
    elif (
        (
            (
                parsed_url.netloc == "urldefense.com"
                or parsed_url.netloc == "urldefense.us"
            )
            and parsed_url.path.startswith("/v3/")
        )
        or (parsed_url.path.startswith("urldefense.com/v3/"))
        or (parsed_url.path.startswith("urldefense.us/v3/"))
    ):
        cleaned_url = decode_ppv3(mangled_url, unquote_url)
    else:
        # assume URL hasn't been mangled
        return mangled_url

    return cleaned_url


def process_payload(e):
    if e.is_multipart():
        for p in e.get_payload():
            process_payload(p)
    else:
        t = e.get_content_type()
        if t in ["text/plain", "text/html"]:
            print("type: %s" % t)
            urls = re.findall(URL_REGEX, e.get_content())
            for u in urls:
                u = decode(u, True)
                print(u)
            print("")


if __name__ == "__main__":
    # use the "new" 3.6+ API: https://stackoverflow.com/a/48101684
    e = email.message_from_string(
        "".join(sys.stdin.readlines()), policy=email.policy.default
    )
    process_payload(e)

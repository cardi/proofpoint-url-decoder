#!/usr/bin/env python3
# vim: set fileencoding=utf-8 :

# decode_email.py - normalizes malformed proofpoint urls and prints the entire
# email to stdout. recommended for use with procmail (please make backups!).
#
# Written in 2017 by Calvin Ardi <calvin@isi.edu>
#
# To the extent possible under law, the author(s) have dedicated all copyright
# and related and neighboring rights to this software to the public domain
# worldwide. This software is distributed without any warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication along
# with this software.
# If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
#
# usage: cat email | ./decode_email.py > email.cleaned
#

import email, email.policy, email.message
import fileinput
import re
import sys
import urllib.request, urllib.parse, urllib.error

# https://gist.github.com/gruber/8891611
URL_REGEX = r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))"""


def decode_ppurl(ppurl):
    ppurl = str(ppurl)
    query = urllib.parse.urlparse(ppurl).query
    param = urllib.parse.parse_qs(query)

    if 'u' not in param:
        sys.stderr.write('ERROR: check if URL is a proofpoint URL')
        return ppurl
    else:
        u = (param['u'][0].replace('-', '%').replace('_', '/'))
        url = urllib.parse.unquote(u)
        return url


def process_payload(e):
    if e.is_multipart():
        for p in e.get_payload():
            process_payload(p)
    else:
        t = e.get_content_type()
        # XXX are there any more formats we should consider?
        if t in ["text/plain", "text/html"]:
            encoding = e.get('Content-Transfer-Encoding')
            if encoding != None:
                encoding = encoding.lower()

            payload = e.get_content()

            # only clean proofpoint-encoded URLs--the "urldefense"
            # prefix might be different across installations
            payload_clean = \
              re.sub(URL_REGEX, \
                     lambda match: decode_ppurl(match.group()) \
                       if "urldefense.proofpoint.com" in match.group() \
                       else match.group(), \
                     payload)

            # modify the payload in place, which also sets the following:
            #
            #   Content-Type: text/plain, charset="utf-8"
            #   Content-Transfer-Encoding: 7bit
            e.set_content(payload_clean)

            # set content-type correctly, if we originally had text/html
            del e['Content-Type']
            charset = e.get_content_charset()
            if charset == None:
                charset = "utf-8"
            e.add_header('Content-Type', t, charset=charset)

            # XXX reset content-transfer-encoding header?
            #
            # set_content should take care of encoding, although it defaults to
            # 7bit. this might be problematic if we processed base64-encoded
            # parts and re-encoded to 7bit, but text/plain and text/html
            # _shouldn't_ be in base64 encoding anyways?
            #
            # python3.7 email APIs doesn't seem to have an easy way to deal
            # with changing the cte?

if __name__ == '__main__':
    # read email from STDIN
    e = email.message_from_string("".join(sys.stdin.readlines()), policy=email.policy.default)
    # process and replace URLs in place
    process_payload(e)
    # write email to STDOUT
    print(e)

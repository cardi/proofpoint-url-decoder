#!/usr/bin/env python3

#
# Written in 2016 by Calvin Ardi <calvin@isi.edu>
#
# To the extent possible under law, the author(s) have dedicated all copyright
# and related and neighboring rights to this software to the public domain
# worldwide. This software is distributed without any warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication along
# with this software.
# If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.
#

"""This snippet prints out an unmodified proofpoint "protected" URL.

Usage:
    ./decode.py url

Args:
    url: a proofpoint url (usually starts with urldefense.proofpoint.com)

Returns:
    A decoded URL string.

"""

import sys
import urllib.request, urllib.parse, urllib.error

if __name__ == '__main__':
  if len(sys.argv) != 2:
    sys.exit('Usage: %s encoded_url' % sys.argv[0])

  #
  # proofpoint "protected" URLs take the form of:
  #
  #   https://urldefense.proofpoint.com/v2/url?[params]
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

  query  = urllib.parse.urlparse(sys.argv[1]).query
  param  = urllib.parse.parse_qs(query)

  if 'u' not in param:
    sys.exit('ERROR: check if URL is a proofpoint URL')
  else:
    u   = (param['u'][0].replace('-', '%')
                        .replace('_', '/'))
    url = urllib.parse.unquote(u)

    print(url)

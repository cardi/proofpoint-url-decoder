#!/usr/bin/env python

# This is free and unencumbered software released into the public domain.
#
# Anyone is free to copy, modify, publish, use, compile, sell, or
# distribute this software, either in source code form or as a compiled
# binary, for any purpose, commercial or non-commercial, and by any
# means.
#
# In jurisdictions that recognize copyright laws, the author or authors
# of this software dedicate any and all copyright interest in the
# software to the public domain. We make this dedication for the benefit
# of the public at large and to the detriment of our heirs and
# successors. We intend this dedication to be an overt act of
# relinquishment in perpetuity of all present and future rights to this
# software under copyright law.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY CLAIM, DAMAGES OR
# OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# For more information, please refer to <http://unlicense.org/>
#
# Author: Calvin Ardi <calvin@isi.edu>

"""This snippet prints out an unmodified proofpoint "protected" URL.

Usage:
    ./decode.py url

Args:
    url: a proofpoint url (usually starts with urldefense.proofpoint.com)

Returns:
    A decoded URL string.

"""

import sys
import urllib
import urlparse

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

  query  = urlparse.urlparse(sys.argv[1]).query
  param  = urlparse.parse_qs(query)

  if 'u' not in param:
    sys.exit('ERROR: check if URL is a proofpoint URL')
  else:
    u   = (param['u'][0].replace('-', '%')
                        .replace('_', '/'))
    url = urllib.unquote(u)

    print url

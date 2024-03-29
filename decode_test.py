#!/usr/bin/env python3

#
# Written 2022 by Calvin Ardi <calvin@isi.edu>
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

import unittest
from parameterized import parameterized

from decode import decode_ppv3
from decode import decode_ppv2


class TestDecodeV2Methods(unittest.TestCase):
    def test_simple(self):
        url = "https://urldefense.com/v2/url?u=https-3A__www.example.com&d=&c=&r=&m=&s=&e="
        expected = "https://www.example.com"

        self.assertEqual(decode_ppv2(url), expected)

    def test_symbols_1(self):
        url = "https://urldefense.com/v2/url?u=https-3A__www.example.com_-23-23-23-23-23foobar&d=&c=&r=&m=&s=&e="
        expected = "https://www.example.com/#####foobar"

        self.assertEqual(decode_ppv2(url), expected)

    def test_symbols_2(self):
        url = "https://urldefense.com/v2/url?u=https-3A__www.example.com_-40-40-21-40foobar&d=&c=&r=&m=&s=&e="
        expected = "https://www.example.com/@@!@foobar"

        self.assertEqual(decode_ppv2(url), expected)


class TestDecodeV3Methods(unittest.TestCase):
    def test_simple(self):
        url = "https://urldefense.com/v3/__http://www.example.com__;!!foo!bar$"
        expected = "http://www.example.com"

        self.assertEqual(decode_ppv3(url), expected)

    def test_simple_noschema(self):
        url = "urldefense.com/v3/__http://www.example.com__;!!foo!bar$"
        expected = "http://www.example.com"

        self.assertEqual(decode_ppv3(url), expected)

    def test_empty(self):
        url = "urldefense.com/v3/____;Iw!!foo!bar$"
        expected = ""

        self.assertEqual(decode_ppv3(url), expected)

    def test_replace_one(self):
        url = (
            "https://urldefense.com/v3/__https://example.com/*newsletter__;Iw!!foo!bar$"
        )
        expected = "https://example.com/#newsletter"

        self.assertEqual(decode_ppv3(url), expected)

    def test_complex_quoted(self):
        url = "https://urldefense.com/v3/__http://example.com/?=a1!b2@c3*d4$5e*6*5E7&8*9(10*7C*5C**B7D*7B__;IyUlKiUlW10lJQ!!foo!bar$"
        expected = "http://example.com/?=a1!b2@c3#d4$5e%6%5E7&8*9(10%7C%5C[]%7D%7B"

        self.assertEqual(decode_ppv3(url), expected)

    def test_complex_unquoted_1(self):
        url = "https://urldefense.com/v3/__http://example.com/?=a1!b2@c3*d4$5e*6*5E7&8*9(10*7C*5C**B7D*7B__;IyUlKiUlW10lJQ!!foo!bar$"
        expected = r"http://example.com/?=a1!b2@c3#d4$5e%6^7&8*9(10|\[]}{"

        self.assertEqual(decode_ppv3(url, True), expected)

    def test_complex_unquoted_2(self):
        url = "https://urldefense.com/v3/__http://example.com/?=a1!b2@c3*d4$5e*6*5E7&8*9(10)-=_*__;IyUlKis!!foo!bar$"
        expected = "http://example.com/?=a1!b2@c3#d4$5e%6^7&8*9(10)-=_+"
        self.assertEqual(decode_ppv3(url, True), expected)

    def test_complex_unquoted_3(self):
        url = "https://urldefense.com/v3/__http://example.com/?=*7B*7D**Aa1!b2@c3**D__;JSVbXSMjIyMj!!foo!bar$"
        expected = "http://example.com/?={}[]a1!b2@c3#####"
        self.assertEqual(decode_ppv3(url, True), expected)

    def test_complex_unquoted_4(self):
        url = "https://urldefense.com/v3/__http://example.com/?=*22'*7B*7D**Aa1!b2@c3**D'*22__;JSUlW10jIyMjIyU!!foo!bar$"
        expected = "http://example.com/?=\"'{}[]a1!b2@c3#####'\""
        self.assertEqual(decode_ppv3(url, True), expected)

    def test_long_65(self):
        url = "https://urldefense.com/v3/__http://www.example.com/**_test__;IyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyM!!foo!bar$"
        expected = "http://www.example.com/#################################################################test"
        self.assertEqual(decode_ppv3(url), expected)

    def test_long_66(self):
        url = "https://urldefense.com/v3/__http://www.example.com/**_*test__;IyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMj!!foo!bar$"
        expected = "http://www.example.com/##################################################################test"
        self.assertEqual(decode_ppv3(url), expected)

    def test_long_67(self):
        url = "https://urldefense.com/v3/__http://www.example.com/**_**Atest__;IyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIw!!foo!bar$"
        expected = "http://www.example.com/###################################################################test"
        self.assertEqual(decode_ppv3(url), expected)

    def test_long_68(self):
        url = "https://urldefense.com/v3/__http://www.example.com/**_**Btest__;IyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyM!!foo!bar$"
        expected = "http://www.example.com/####################################################################test"
        self.assertEqual(decode_ppv3(url), expected)

    def test_long_130(self):
        url = "https://urldefense.com/v3/__http://www.example.com/**_**_test__;IyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIw!!foo!bar$"
        expected = "http://www.example.com/##################################################################################################################################test"
        self.assertEqual(decode_ppv3(url), expected)

    def test_long_131(self):
        url = "https://urldefense.com/v3/__http://www.example.com/**_**_*test__;IyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyMjIyM!!foo!bar$"
        expected = "http://www.example.com/###################################################################################################################################test"
        self.assertEqual(decode_ppv3(url), expected)

    def test_incomplete_url_v3(self):
        url = "https://urldefense.com/v3/__http://www.example.com/"
        expected = url
        self.assertEqual(decode_ppv3(url), expected)


class TestSequenceUTF8(unittest.TestCase):
    @parameterized.expand(
        [
            [
                0,
                "https://urldefense.com/v3/__http://www.example.com/**Aa*.html__;w60j!!foo!bar$",
                "http://www.example.com/ía#.html",
            ],
            [
                1,
                "https://urldefense.com/v3/__http://www.example.com/**Aa*a*.html__;w60jIw!!foo!bar$",
                "http://www.example.com/ía#a#.html",
            ],
            [
                2,
                "https://urldefense.com/v3/__http://www.example.com/**B.html__;w60j!!foo!bar$",
                "http://www.example.com/í#.html",
            ],
            [
                3,
                "https://urldefense.com/v3/__http://www.example.com/**C.html__;w60jIw!!foo!bar$",
                "http://www.example.com/í##.html",
            ],
            [
                4,
                "https://urldefense.com/v3/__http://www.example.com/**D.html__;w60jIyM!!foo!bar$",
                "http://www.example.com/í###.html",
            ],
            [
                5,
                "https://urldefense.com/v3/__http://www.example.com/**E.html__;w60jIyMj!!foo!bar$",
                "http://www.example.com/í####.html",
            ],
            [
                6,
                "https://urldefense.com/v3/__http://www.example.com/**F.html__;w60jIyMjIw!!foo!bar$",
                "http://www.example.com/í#####.html",
            ],
            [
                "long chain of accents",
                "https://urldefense.com/v3/__http://www.example.com/**_**5.html__;w6DDqMOsw7LDucOAw4jDjMOSw5nDocOpw63Ds8O6w73DgcOJw43Dk8Oaw53DosOqw67DtMO7w4LDisOOw5TDm8Ojw7HDtcODw5HDlcOkw6vDr8O2w7zDv8OEw4vDj8OWw5zFuMOlw4XDpsOGxZPFksOnw4fDsMOQw7jDmA!!foo!bar$",
                "http://www.example.com/àèìòùÀÈÌÒÙáéíóúýÁÉÍÓÚÝâêîôûÂÊÎÔÛãñõÃÑÕäëïöüÿÄËÏÖÜŸåÅæÆœŒçÇðÐøØ.html",
            ],
            [
                "accent-ascii sequence",
                "https://urldefense.com/v3/__http://www.example.com/**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Aa**Ca**Aa.html__;w6DDqMOsw7LDucOAw4jDjMOSw5nDocOpw63Ds8O6w73DgcOJw43Dk8Oaw53DosOqw67DtMO7w4LDisOOw5TDm8Ojw7HDtcODw5HDlcOkw6vDr8O2w7zDv8OEw4vDj8OWw5zFuMOlw4XDpsOGxZPFksOnw4fDsMOQw7jDmA!!foo!bar$",
                "http://www.example.com/àaèaìaòaùaÀaÈaÌaÒaÙaáaéaíaóaúaýaÁaÉaÍaÓaÚaÝaâaêaîaôaûaÂaÊaÎaÔaÛaãañaõaÃaÑaÕaäaëaïaöaüaÿaÄaËaÏaÖaÜaŸaåaÅaæaÆaœaŒaçaÇaðaÐøaØa.html",
            ],
            [
                "utf-8 characters",
                "https://urldefense.com/v3/__http://www.example.com/**E.html__;5L2g5aW9!!foo!bar$",
                "http://www.example.com/你好.html",
            ],
        ]
    )
    def test_accent(self, name, url, expected):
        self.assertEqual(decode_ppv3(url), expected)


if __name__ == "__main__":
    unittest.main()

# proofpoint-url-decoder

*proofpoint-url-decoder* is a collection of various Python scripts to
unmangle Proofpoint "protected" emails.

## Proofpoint Considered Harmful

Some reasons why Proofpoint is harmful (a non-exhaustive list):

1. Proofpoint makes it **harder** to read email: by mangling URLs, the
   user can no longer see what the actual URL is and must blindly trust in
   a third-party.

2. Proofpoint **erodes your privacy**: in addition to someone else
   scanning your email there are unique identifiers embedded in each
   mangled URL that tie each URL to an individual user, and Proofpoint will
   independently *visit* (and possibly even *crawl*) the URL after the user
   has clicked on it.

## Usage

Each program can be used standalone: pick and use the Python script that
is most relevant to your use case.

There are several files of note:

* `decode.py`: reads a URL as an input parameter, outputs a clean URL to `STDOUT`

  Example:
  ```shell
  $ set +H   # disable ! history substitution
  $ ./decode.py "https://urldefense.com/v3/__http://www.example.com__;!!foo!bar$"
  http://www.example.com
  ```
* `get_urls.py`: reads as input an email (from `STDIN`), extracts and
  outputs clean URLs to `STDOUT`
* `decode_email.py`: reads as input an email (from `STDIN`), and
  outputs the same email with clean URLs to `STDOUT`

  Example:
  ```shell
  $ cat email_message | ./decode_email.py > email_message.cleaned
  ```

### Tests

There are some unit tests:

```shell
python3 -v decode_test.py
```

## Contributing

Feel free to contribute code or send comments, suggestions, bugs to
<calvin@isi.edu>.

## Development Notes and Roadmap

For now, to keep each script independent, `decode_ppv2()` and
`decode_ppv3` are duplicated in each script.

## LICENSE

[CC0 1.0 Universal](./LICENSE)

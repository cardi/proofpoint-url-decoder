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

There are several files of note:

* `decode.py`: reads as input a string, outputs a clean URL
* `get_urls.py`: reads as input an email (from `STDIN`), extracts and
  outputs clean URLs
* `decode_email.py`: reads as input an email (from `STDIN`), and
  outputs the same email with clean URLs

Example:

    cat email_message | ./decode_email.py > email_message.cleaned

## Contributing

Feel free to contribute code or send comments, suggestions, bugs to
calvin@isi.edu. 

## LICENSE

[CC0 1.0 Universal](./LICENSE)

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

### fdm

Add the following rules to your `.fdm.conf`:

```
# An action to save to the maildir ~/Mail/inbox.
action "inbox" maildir "%h/Mail/inbox"
action "backup" maildir "%h/Mail/backup"

# Un-mangle ProofPoint URLs
action "unmangle" rewrite "/path/to/proofpoint-url-decoder/decode_email.py"

# (optional) keep a backup of all email
match all action "backup" continue

# 1. match all mail
# 2. run the "unmangle" action on each message (rewrite URLs)
# 3. run the "inbox" action on the resulting message (deliver to Maildir)
match all action "unmangle" continue
match all action "inbox"
```

Watch your log file (`.fdm.log`) for any issues. If you're processing a lot of
mail at any one time, you may have to configure additional settings in `.fdm.conf`:
see `man 5 fdm.conf` for more information.

### procmail

Add the following rule near the beginning of your `.procmailrc`:

```
:0 fw
| /path/to/proofpoint-url-decoder/decode_email.py
```

You could match on and filter emails containing the `X-Proofpoint-*` header
(which would be all emails on systems), but sometimes you will get emails
forwarded to you that might not have this header and still contain the
mangled URLs.

It's a good idea to keep a backup copy of the emails, in case something
in the processing pipeline goes wrong:

```
# copy all mail to the "backup" Maildir
:0c
backup/

# pipe message through decode_email.py
:0 fw
| /path/to/proofpoint-url-decoder/decode_email.py

# write resulting email into "inbox" Maildir
:0:
inbox/
```

You could also run `decode_email.py` on a copy of the email to test its
functionality:

```
# create a working copy
:0c
{
    # pipe message through decode_email.py
    :0 fw
    | /path/to/proofpoint-url-decoder/decode_email.py

    # write resulting email into "testing" Maildir
    :0:
    testing/
}
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

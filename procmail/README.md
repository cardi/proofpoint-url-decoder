# proofpoint-url-decoder/procmail

Some tests to see if things work with `procmail` and `decode_email.py`.

Pre-requisites:
- [`just`](https://github.com/casey/just#packages).
- `mutt`

```
# create mail directories
just create-maildir

# process first mail
just test-01

# process second mail
just test-02

# in a new terminal: run mutt
just run-mutt
```

Also see: `tail -F procmail/procmail.log`

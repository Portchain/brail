Brail is a command-line tool for release management

# For users
## Installing brail
- pip3 install brail

## Adding brail to a project
- Create a *record directory* for storing brail records, e.g. `docs/brail`
- Add a `.brailconf` configuration file in the repository root, e.g:
```
{
  "record_dir": "docs/brail"
}
```

## Configuring an editor
- Add a `.brailconf` configuration file in your home directory
- Specify the editor in `.brailconf`, e.g:
```
{
  "record_dir": "docs/brail"
}
```

## Command-line usage
```
  brail config                Show config

  brail feat                  Create a feature record
  brail feat -m <message>     Create a feature record with a message
  brail fix                   Create a bugfix record
  brail manual                Create a manual step record

  brail diff                  Compare HEAD to the default comparison directory
  brail diff <base>           Compare HEAD to the <base> branch
  brail diff <target> <base>  Compare <target> to the <base> branch
```

# For developers
## Running unit tests
```
python3 -m unittest discover
```
# Whispers <img src="whispers.png" width="40px" alt="Whispers" style=""> 

[![](https://img.shields.io/pypi/v/whispers.svg)](https://pypi.python.org/pypi/whispers/)
[![](https://github.com/Skyscanner/whispers/workflows/build/badge.svg)](https://github.com/Skyscanner/whispers/actions)
![](coverage.svg)
[![](https://img.shields.io/github/issues/Skyscanner/whispers)](https://github.com/Skyscanner/whispers/issues)
[![](https://img.shields.io/github/issues-pr/Skyscanner/whispers)](https://github.com/Skyscanner/whispers/pulls)
[![](https://img.shields.io/pypi/dm/whispers)](https://img.shields.io/pypi/dm/whispers)

> "My little birds are everywhere, even in the North, they whisper to me the strangest stories." - _Varys_

Whispers is a static text analysis tool designed for parsing various common software config formats in search of hardcoded secrets. Whispers can run in the CLI or be integrated in a CI/CD pipeline.

Whispers is a **static structured text** parser, not dynamic code parser.

## Supported Formats
* YAML
* JSON
* XML
* .npmrc
* .pypirc
* .htpasswd
* .properties
* pip.conf
* conf / ini
* Dockerfile
* Shell scripts
* Python3 (parsed as AST due to native language support)
* AWS credentials files
* JDBC connection strings
* Jenkins config files
* SpringFramework Beans config files
* Java Properties files
* Dockercfg private registry auth files

## Detects
* Passwords
* API tokens
* AWS keys
* Private keys
* Hashed credentials
* Authentication tokens
* Dangerous functions
* Sensitive files

## Installation

### From PyPI
```
pip3 install whispers
```

### From GitHub
```
git clone https://github.com/Skyscanner/whispers
cd whispers
make install
```

## Usage
### CLI
```
whispers --help
whispers --version
whispers --info
whispers --config config.yml target/file/or/dir
whispers --output /tmp/secrets.out target/file/or/dir
whispers --rules aws-id,aws-secret target/file/or/dir
whispers --severity BLOCKER,CRITICAL target/file/or/dir
whispers --exitcode 7 target/file/or/dir
whispers target/file/or/dir
```

### Python
```python
from whispers.core.args import parse_args
from whispers.main import run

args = parse_args([
  "-c", "whispers/config.yml",
  "-r", "apikey,aws-secret,password",
  "-s", "BLOCKER,CRITICAL,MAJOR",
  "tests/fixtures"
])

for secret in run(args):
  print(f"[{secret.file}:{secret.line}] {secret.key} = {secret.value}")
```

## Config
There are several configuration options available in Whispers. It’s possible to include/exclude results based on file path, key, or value. File path specifications are interpreted as globs. Keys and values accept regular expressions and several other parameters. There is a default configuration file built-in that will be used if you don't provide a custom one.

`config.yml` should have the following structure:
```yaml
include:
  files:
    - "**/*.yml"  # glob

exclude:
  files:
    - .*/tests?/  # regex
  keys:
    - ^foo        # regex
  values:
    - bar$        # regex

rules:
  - password
  - privatekey
  - id: starks
    message: Whispers from the North
    severity: CRITICAL
    value:
      regex: (Aria|Ned) Stark
      ignorecase: True

severity:
  - CRITICAL
  - BLOCKER
  - MAJOR
```

The fastest way to tweak detection (ie: remove false positives and unwanted results) is to copy the default [config.yml](whispers/config.yml) into a new file, adapt it, and pass it as an argument to Whispers.

For example: `whispers -c config.yml -r starks target`


## Custom Rules
Rules specify the actual things that should be pulled out from key-value pairs. There are several common ones that come built-in, such as AWS keys and passwords, but the tool is made to be easily expandable with new rules.

- Custom rules can be defined in the main config file under `rules:`
- Custom rules can be added to [whispers/rules](whispers/rules/)

```yaml
- id: rule-id                 # unique rule name
  description: Values formatted like AWS Session Token
  message: AWS Session Token  # report will show this message
  severity: BLOCKER           # one of BLOCKER, CRITICAL, MAJOR, MINOR, INFO

  key:                        # specify key format
    regex: (aws.?session.?token)?
    ignorecase: True          # case-insensitive matching

  value:                      # specify value format
    regex: ^(?=.*[a-z])(?=.*[A-Z])[A-Za-z0-9\+\/]{270,450}$
    ignorecase: False         # case-sensitive matching
    minlen: 270               # value is at least this long
    isBase64: True            # value is base64-encoded
    isAscii: False            # value is binary data when decoded
    isUri: False              # value is not formatted like a URI

  similar: 0.35               # maximum allowed similarity between key and value 
                              # (1.0 being exactly the same)
```


## Plugins
All parsing functionality is implemented via plugins. Each plugin implements a class with the `pairs()` method that runs through files and returns a `KeyValuePair` object to be checked with rules.

```py
from whispers.core.utils import KeyValuePair

class PluginName:
  def pairs(self, filepath: Path):
    yield KeyValuePair(
      "key",
      "value",
      keypath=["node", "path", "to", "key"],
      file=filepath.as_posix()
    )
```

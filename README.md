# Whispers <img src="whispers.png" width="40px" alt="Whispers" style=""> 

[![](https://img.shields.io/pypi/v/whispers.svg)](https://pypi.python.org/pypi/whispers/)
[![](https://github.com/Skyscanner/whispers/workflows/build/badge.svg)](https://github.com/Skyscanner/whispers/actions)
![](coverage.svg)
[![](https://img.shields.io/github/issues/Skyscanner/whispers)](https://github.com/Skyscanner/whispers/issues)
[![](https://img.shields.io/github/issues-pr/Skyscanner/whispers)](https://github.com/Skyscanner/whispers/pulls)
[![](https://img.shields.io/pypi/dm/whispers)](https://img.shields.io/pypi/dm/whispers)

# Archive Notice - October 11 2023
This project has been unmaintained by Skyscanner but the project is still being maintained by the original creator in [https://github.com/adeptex/whispers](https://github.com/adeptex/whispers). This project will remain archived for referencing purposes.

Please head over to [https://github.com/adeptex/whispers](https://github.com/adeptex/whispers) for the latest version of `whispers`.

 > "My little birds are everywhere, even in the North, they whisper to me the strangest stories." - _Lord Varys_

Whispers is a static code analysis tool designed for parsing various common data formats in search of hardcoded credentials and dangerous functions. Whispers can run in the CLI or you can integrate it in your CI/CD pipeline.


## Detects
* Passwords
* API tokens
* AWS keys
* Private keys
* Hashed credentials
* Authentication tokens
* Dangerous functions
* Sensitive files

## Supported Formats
Whispers is intended to be a **structured text** parser, not a code parser.

The following commonly used formats are currently supported:
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
* Dockercfg
* Shell scripts
* Python3

Python3 files are parsed as ASTs because of native language support.

## Declaration & Assignment Formats
The following language files are parsed as text, and checked for common variable declaration and assignment patterns:
* JavaScript
* Java
* Go
* PHP

## Special Formats
* AWS credentials files
* JDBC connection strings
* Jenkins config files
* SpringFramework Beans config files
* Java Properties files
* Dockercfg private registry auth files
* Github tokens

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
whispers --info
whispers source/code/fileOrDir
whispers --config config.yml source/code/fileOrDir
whispers --output /tmp/secrets.yml source/code/fileOrDir
whispers --rules aws-id,aws-secret source/code/fileOrDir
whispers --severity BLOCKER,CRITICAL source/code/fileOrDir
whispers --exitcode 7 source/code/fileOrDir
```
### Python
```python
from whispers.cli import parse_args
from whispers.core import run

src = "tests/fixtures"
configfile = "whispers/config.yml"
args = parse_args(["-c", configfile, src])
for secret in run(args):
  print(secret)
```

## Config
There are several configuration options available in Whispers. It’s possible to include/exclude results based on file path, key, or value. File path specifications are interpreted as globs. Keys and values accept regular expressions and several other parameters. There is a default configuration file built-in that will be used if you don't provide a custom one.

`config.yml` should have the following structure:
```yaml
include:
  files:
    - "**/*.yml"

exclude:
  files:
    - "**/test/**/*"
    - "**/tests/**/*"
  keys:
    - ^foo
  values:
    - bar$

rules:
  starks:
    message: Whispers from the North
    severity: CRITICAL
    value:
      regex: (Aria|Ned) Stark
      ignorecase: True
```

The fastest way to tweak detection (ie: remove false positives and unwanted results) is to copy the default [config.yml](whispers/config.yml) into a new file, adapt it, and pass it as an argument to Whispers.

`whispers --config config.yml --rules starks src/file/or/dir`


## Custom Rules
Rules specify the actual things that should be pulled out from key-value pairs. There are several common ones that come built-in, such as AWS keys and passwords, but the tool is made to be easily expandable with new rules.

- Custom rules can be defined in the main config file under `rules:`
- Custom rules can be added to [whispers/rules](whispers/rules/)

```yaml
rule-id:  # unique rule name
  description: Values formatted like AWS Session Token
  message: AWS Session Token  # report will show this message
  severity: BLOCKER           # one of BLOCKER, CRITICAL, MAJOR, MINOR, INFO

  key:        # specify key format
    regex: (aws.?session.?token)?
    ignorecase: True   # case-insensitive matching

  value:      # specify value format
    regex: ^(?=.*[a-z])(?=.*[A-Z])[A-Za-z0-9\+\/]{270,450}$
    ignorecase: False  # case-sensitive matching
    minlen: 270        # value is at least this long
    isBase64: True     # value is base64-encoded
    isAscii: False     # value is binary data when decoded
    isUri: False       # value is not formatted like a URI

  similar: 0.35        # maximum allowed similarity between key and value 
                       # (1.0 being exactly the same)
```


## Plugins
All parsing functionality is implemented via plugins. Each plugin implements a class with the `pairs()` method that runs through files and returns the key-value pairs to be checked with rules. 

```py
class PluginName:
    def pairs(self, file):
        yield "key", "value"
```

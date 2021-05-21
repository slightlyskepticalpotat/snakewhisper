# snakewhisper
![GitHub release (latest by date)](https://img.shields.io/github/v/release/slightlyskepticalpotat/snakewhisper?style=flat-square)
![PyPI](https://img.shields.io/pypi/v/snakewhisper?style=flat-square)
![GitHub](https://img.shields.io/github/license/slightlyskepticalpotat/snakewhisper?style=flat-square)
![Python Version](https://img.shields.io/badge/python-%3E%3D%203.6-blue?style=flat-square)

snakewhisper is a simple [end-to-end encrypted](https://en.wikipedia.org/wiki/End-to-end_encryption) chat program written in Python. It's functional (it currently supports two-way communication with a pre-shared key), but snakewhisper is primarily a proof-of-concept that showcases how regular computer users can easily access—or even create—chat programs with end-to-end encryption.

## Installation

### Pip
```bash
$ pip3 install snakewhisper
```

### Git
```bash
$ git clone https://github.com/slightlyskepticalpotat/snakewhisper.git
$ cd snakewhisper
$ pip3 install -r requirements.txt
```

## Usage
The below commands show the basic features of snakewhisper.  

### Generate Key

### Pip
```bash
$ python3 -m snakewhisper_key
```

### Git
```bash
$ python3 snakewhisper_key.py
```

### Output
```
Key: VJM5wFYxuM1oi5VD3WBRMv4NpTnnVQA8wVNV1x4KSig=
Save? (y/n): y # type here
Save As: snakewhisper.key # type here
Saved As: snakewhisper.key
```

### Connect/Chat

### Pip
```bash
$ python3 -m snakewhisper_chat
```

### Git
```bash
$ python3 snakewhisper_chat.py
```

### Output
```
Log? (y/n): y # type here
KEY: VJM5wFYxuM1oi5VD3WBRMv4NpTnnVQA8wVNV1x4KSig= # type here
INFO: Listening on port 2048
INFO: /help to list commands
HOST: 1.1.1.1 # type here
INFO: Connected to 1.1.1.1
INFO: New connection 1.1.1.1
# now you type messages or commands
alice to bob # your message
1.1.1.1: bob to alice # their message
/help # list all commands
INFO: /alias /clear /help /ip /quit /remote /time
/help quit # describe quit command
INFO: Quits the program
/quit # quits the program
INFO: Quit successfully
```

## Cryptography
For easy implementation, snakewhisper uses the [Fernet](https://cryptography.io/en/latest/fernet/) encryption scheme from the [cryptography](https://github.com/pyca/cryptography) Python package. Fernet is just AES-128 encryption with a SHA-256 hash-based message authentication code, and the full specification can be viewed [here](https://github.com/fernet/spec/blob/master/Spec.md). It also adds a timestamp to the message, but snakewhisper does not use that functionality.

## To-do List
- Secure multi-user conversations

## Contributing
Pull requests are welcome, but please open an issue to discuss major changes.

## License
snakewhisper is licenced under version 3.0 of the [GNU Affero General Public License](https://github.com/slightlyskepticalpotat/snakewhisper/blob/main/LICENSE).

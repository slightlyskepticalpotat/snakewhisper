# snakewhisper
![GitHub release (latest by date)](https://img.shields.io/github/v/release/slightlyskepticalpotat/snakewhisper?style=flat-square)
![PyPI](https://img.shields.io/pypi/v/snakewhisper?style=flat-square)
![GitHub](https://img.shields.io/github/license/slightlyskepticalpotat/snakewhisper?style=flat-square)
![Python Version](https://img.shields.io/badge/python-%3E%3D%203.6-blue?style=flat-square)

snakewhisper is a simple [end-to-end encrypted](https://en.wikipedia.org/wiki/End-to-end_encryption) chat program written in Python. It's functional (it currently supports two-way communication with elliptic curve key exchange), but snakewhisper is primarily a proof-of-concept that showcases how regular computer users can easily access—or even create—chat programs with end-to-end encryption.

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
The below commands demonstrate the basic features of snakewhisper.  
```bash
$ python3 -m snakewhisper # installed with pip
$ python3 snakewhisper.py # installed with git
Log? (y/n): y # type here
INFO: Generating private key
INFO: Listening on port 2048
INFO: /help to list commands
HOST: 1.1.1.1 # type here
INFO: Connecting to 1.1.1.1
INFO: Connected to 1.1.1.1
# now you type messages or commands
alice to bob # your message
1.1.1.1: bob to alice # their message
/help # list all commands
INFO: /alias /clear /help /ip /privkey /quit /remote /time
/help quit # describe quit command
INFO: Quits the program
/quit # quits the program
INFO: Quit successfully
```

## Cryptography
Every time snakewhisper starts, it generates an elliptic curve private key using [Curve25519](https://en.wikipedia.org/wiki/Curve25519) (offering 128 bits of NSA-free security). When it connects to a peer, they exchange public keys and use [Elliptic-curve Diffie–Hellman](https://en.wikipedia.org/wiki/Elliptic-curve_Diffie%E2%80%93Hellman) to agree on a shared secret key. After that, the unsalted secret key is passed through [HKDF](https://en.wikipedia.org/wiki/HKDF) to obtain a 128-bit encryption key.

For ease of implementation, snakewhisper encrypts messages using the [Fernet](https://cryptography.io/en/latest/fernet/) encryption scheme from the [cryptography](https://github.com/pyca/cryptography) Python package. Fernet is just [AES-128](https://en.wikipedia.org/wiki/Advanced_Encryption_Standard) with a [SHA-256](https://en.wikipedia.org/wiki/SHA-2) hash-based message authentication code under the hood, and the full specification can be viewed [here](https://github.com/fernet/spec/blob/master/Spec.md). Fernet also includes a timestamp, but it is in cleartext and can be spoofed.

I am confident that the encryption scheme is secure in theory (barring any secret algorithm backdoors) because it is based on well-known cryptographic algorithms and primitives, but less confident that I've implemented everything correctly. Please review the code beforehand if you intend on sending sensitive data with this (at your own risk, of course).

## To-do List
- Support for timestamps
- Support for sending files
- Multi-user conversations

## Contributing
Pull requests are welcome, but please open an issue to discuss major changes.

## License
snakewhisper is licenced under version 3.0 of the [GNU Affero General Public License](https://github.com/slightlyskepticalpotat/snakewhisper/blob/main/LICENSE).

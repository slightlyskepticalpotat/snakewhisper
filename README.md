# snakewhisper
![GitHub release (latest by date)](https://img.shields.io/github/v/release/slightlyskepticalpotat/snakewhisper?style=flat-square)
![PyPI](https://img.shields.io/pypi/v/snakewhisper?style=flat-square)
![GitHub](https://img.shields.io/github/license/slightlyskepticalpotat/snakewhisper?style=flat-square)
![Python Version](https://img.shields.io/badge/python-%3E%3D%203.6-blue?style=flat-square)

snakewhisper is a simple [end-to-end encrypted](https://en.wikipedia.org/wiki/End-to-end_encryption) chat program written in Python. It's functional (it currently supports two-way communication with a pre-shared key), but snakewhisper is primarily a proof-of-concept that showcases how regular computer users can easily access—or even create—chat programs with end-to-end encryption.

## Installation

### Pip
A pip package for snakewhisper is in development.

### Git
```bash
git clone https://github.com/slightlyskepticalpotat/snakewhisper.git
cd snakewhisper
```

## Usage

## Cryptography
For easy implementation, snakewhisper uses the [Fernet](https://cryptography.io/en/latest/fernet/) encryption scheme from the [cryptography](https://github.com/pyca/cryptography) Python package. Fernet is just AES-128 encryption with a SHA-256 hash-based message authentication code, and the full specification can be viewed [here](https://github.com/fernet/spec/blob/master/Spec.md). It also adds a timestamp to the message, but snakewhisper does not use that functionality.

## To-do List
- Proper key exchange algorithm
- More than two people chatting
- Register and upload pip package

## Contributing
Pull requests are welcome, but please open an issue to discuss major changes.

## License
snakewhisper is licenced under version 3.0 of the [GNU Affero General Public License](LICENSE).

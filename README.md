# snakewhisper
Proof of concept of an end-to-end encrypted peer-to-peer chat program written in Python. Currently, snakewhisper supports two-way encrypted communication between two instances with a pre-shared key. For ease of implementation, it uses the [Fernet](https://cryptography.io/en/latest/fernet/) symmetric encryption scheme (AES-128 with a SHA-256 HMAC).

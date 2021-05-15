import secrets


def keygen(n):
    """Generates n random bits encoded in url-safe base 64."""
    return secrets.token_urlsafe(n // 8)


save_file = input("Save As (Space Skips): ")
key_generated = keygen(256)
print(f"Key: {key_generated}")

if save_file:
    with open(save_file, "w") as file:
        file.write(key_generated)
    print(f"Saved As: {save_file}")

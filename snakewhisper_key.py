import base64
import os


def keygen(n):
    """Generates n random bytes encoded in url-safe base 64."""
    return base64.urlsafe_b64encode(os.urandom(n))


key = keygen(32).decode()
print(f"Key: {key}")
if input("Save? (y/n): ").lower() == "y":
    save_as = input("Save As: ")
    with open(save_as, "w") as file:
        file.write(key)
    print(f"Saved As: {save_as}")

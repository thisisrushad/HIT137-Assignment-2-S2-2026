"""
Cipher module for HIT137 Assignment 2 - Question 1.
Provides encryption and decryption functions based on character position rules.
"""


def encrypt_char(char: str, shift1: int, shift2: int) -> str:
    """
    Encrypts a single character according to assignment rules:
    - Lowercase (a-n): shift forward by shift1 * shift2
    - Lowercase (o-z): shift backward by shift1 + shift2
    - Uppercase (A-M): shift backward by shift1
    - Uppercase (N-Z): shift forward by shift2**2
    - Digits (0-9): shift forward by shift1 - shift2
    - Other characters: unchanged
    """
    if 'a' <= char <= 'n':
        shift = shift1 * shift2
        return chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
    elif 'o' <= char <= 'z':
        shift = shift1 + shift2
        return chr((ord(char) - ord('a') - shift) % 26 + ord('a'))
    elif 'A' <= char <= 'M':
        shift = shift1
        return chr((ord(char) - ord('A') - shift) % 26 + ord('A'))
    elif 'N' <= char <= 'Z':
        shift = shift2 ** 2
        return chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
    elif '0' <= char <= '9':
        shift = shift1 - shift2
        return chr((ord(char) - ord('0') + shift) % 10 + ord('0'))
    else:
        return char


def decrypt_char(char: str, shift1: int, shift2: int) -> str:
    """
    Decrypts a single character by inverting the encryption shift rules.
    """
    if 'a' <= char <= 'z':
        # Candidate 1: Original char was in 'a'-'n' (shifted forward by shift1 * shift2)
        cand1 = chr((ord(char) - ord('a') - shift1 * shift2) % 26 + ord('a'))
        # Candidate 2: Original char was in 'o'-'z' (shifted backward by shift1 + shift2)
        cand2 = chr((ord(char) - ord('a') + shift1 + shift2) % 26 + ord('a'))

        if 'a' <= cand1 <= 'n':
            return cand1
        elif 'o' <= cand2 <= 'z':
            return cand2
        return cand1

    elif 'A' <= char <= 'Z':
        # Candidate 1: Original char was in 'A'-'M' (shifted backward by shift1)
        cand1 = chr((ord(char) - ord('A') + shift1) % 26 + ord('A'))
        # Candidate 2: Original char was in 'N'-'Z' (shifted forward by shift2 ** 2)
        cand2 = chr((ord(char) - ord('A') - shift2 ** 2) % 26 + ord('A'))

        if 'A' <= cand1 <= 'M':
            return cand1
        elif 'N' <= cand2 <= 'Z':
            return cand2
        return cand1

    elif '0' <= char <= '9':
        # Digits were shifted forward by (shift1 - shift2)
        shift = shift1 - shift2
        return chr((ord(char) - ord('0') - shift) % 10 + ord('0'))

    else:
        return char


def encrypt_file(shift1: int, shift2: int, input_path: str = "raw_text.txt", output_path: str = "encrypted_text.txt") -> None:
    """
    Reads from input_path and writes encrypted content to output_path.
    """
    with open(input_path, 'r', encoding='utf-8') as infile:
        text = infile.read()

    encrypted_text = "".join(encrypt_char(c, shift1, shift2) for c in text)

    with open(output_path, 'w', encoding='utf-8') as outfile:
        outfile.write(encrypted_text)


def decrypt_file(shift1: int, shift2: int, input_path: str = "encrypted_text.txt", output_path: str = "decrypted_text.txt") -> None:
    """
    Reads from input_path and writes decrypted content to output_path.
    """
    with open(input_path, 'r', encoding='utf-8') as infile:
        text = infile.read()

    decrypted_text = "".join(decrypt_char(c, shift1, shift2) for c in text)

    with open(output_path, 'w', encoding='utf-8') as outfile:
        outfile.write(decrypted_text)

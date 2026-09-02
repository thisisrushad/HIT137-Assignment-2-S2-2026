"""
Cipher module for HIT137 Assignment 2 - Question 1.
Provides encryption, decryption, and verification functions based on character position rules.
"""

import os


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


def verify_files(original_path: str = "raw_text.txt", decrypted_path: str = "decrypted_text.txt") -> bool:
    """
    Compares original_path and decrypted_path files.
    Prints whether decryption was successful and returns boolean status.
    """
    try:
        with open(original_path, 'r', encoding='utf-8') as f_orig:
            orig_text = f_orig.read()
        with open(decrypted_path, 'r', encoding='utf-8') as f_dec:
            dec_text = f_dec.read()

        is_success = orig_text == dec_text
        if is_success:
            print("Decryption Successful: The decrypted file matches the original raw text exactly.")
        else:
            print("Decryption Failed: The decrypted file content does NOT match the original text.")
        return is_success

    except FileNotFoundError as error:
        print(f"Error reading files for verification: {error}")
        return False


def get_shift_input(prompt_text: str) -> int:
    """
    Prompts the user for a non-negative integer input.
    Repeats until a valid non-negative integer is entered.
    """
    while True:
        try:
            value = int(input(prompt_text))
            if value < 0:
                print("Invalid input: shift values must be non-negative integers (0 or greater).")
                continue
            return value
        except ValueError:
            print("Invalid input: please enter a valid integer.")


def main() -> None:
    """
    Main program workflow:
    1. Prompt user for shift1 and shift2
    2. Encrypt raw_text.txt -> encrypted_text.txt
    3. Decrypt encrypted_text.txt -> decrypted_text.txt
    4. Verify decryption matches raw_text.txt
    """
    print("=== HIT137 Assignment 2: Question 1 Cipher Program ===")
    shift1 = get_shift_input("Enter shift1 (non-negative integer): ")
    shift2 = get_shift_input("Enter shift2 (non-negative integer): ")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    raw_path = os.path.join(base_dir, "raw_text.txt")
    enc_path = os.path.join(base_dir, "encrypted_text.txt")
    dec_path = os.path.join(base_dir, "decrypted_text.txt")

    print("\n[Step 1] Encrypting 'raw_text.txt'...")
    encrypt_file(shift1, shift2, input_path=raw_path, output_path=enc_path)
    print(f"Content encrypted and written to '{enc_path}'.")

    print("\n[Step 2] Decrypting 'encrypted_text.txt'...")
    decrypt_file(shift1, shift2, input_path=enc_path, output_path=dec_path)
    print(f"Content decrypted and written to '{dec_path}'.")

    print("\n[Step 3] Verifying decryption matches original...")
    success = verify_files(original_path=raw_path, decrypted_path=dec_path)

    if success:
        print("\nProcess completed successfully!")
    else:
        print("\nProcess completed with verification warnings.")


if __name__ == "__main__":
    main()

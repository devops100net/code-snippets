import random
import string

def generate_password(length: int = 12) -> str:
    """
    Generates a unique and secure password of specified length.

    Args:
        length (int, optional): The length of the password. Defaults to 12.

    Returns:
        str: A unique and secure password.
    """
    # Define the character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    numbers = string.digits
    special_chars = string.punctuation

    # Combine all character sets
    all_chars = lowercase + uppercase + numbers + special_chars

    # Ensure the password includes at least one of each character type
    password = [random.choice(lowercase), random.choice(uppercase), random.choice(numbers), random.choice(special_chars)]

    # Fill the rest of the password with random characters
    for _ in range(length - 4):
        password.append(random.choice(all_chars))

    # Shuffle the list to avoid the first four characters always being in the same character type
    random.shuffle(password)

    # Join the list into a string
    password = ''.join(password)

    return password

# Example usage:
print(generate_password())  # Generates a password of default length (12)
print(generate_password(16))  # Generates a password of length 16

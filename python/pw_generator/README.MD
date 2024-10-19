## Unique Password Generator in Python

### Features
- Generates passwords with a combination of uppercase and lowercase letters, numbers, and special characters.
- Ensures that at least one of each character type is included in the password.
- Shuffles the character categories to prevent them from always appearing in the same position in the password.
- Supports customizing the password length.

### Usage
To generate a password with default length (12 characters), simply run the following command:

```
python gen_pw.py
```

Alternatively, you can specify a desired password length by passing an integer to the function, like this:

password = generate_password(16)
print(password)

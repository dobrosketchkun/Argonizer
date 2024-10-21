# Argonizer

Welcome to the **Argonizer**! 🚀 A secure, flexible, and user-friendly tool to create robust passwords tailored to your needs. Ish.

## 🌟 Features

- **Secure Hashing with Argon2**: Leverages the power of Argon2 for hashing, ensuring top-notch security.
- **Customizable Character Sets**: Include lowercase, uppercase, digits, and special characters as per your requirements.
- **Interactive and Configurable**: Choose to input salts interactively or load them from a configuration file.
- **Progress Tracking**: Real-time progress bars to keep you informed during password generation.
- **Detailed Summaries**: Get a comprehensive overview of your password generation parameters.
- **Debug Modes**: Multiple debug levels for in-depth insights or minimal feedback.

## 🛠 Installation

Before diving in, ensure you have Python 3.6 or later installed. Then, clone this repository and install the necessary dependencies:

```bash
git clone https://github.com/yourusername/argon2-password-generator.git
cd argon2-password-generator
pip install -r requirements.txt
```

*Alternatively, you can install the required packages directly:*

```bash
pip install argon2-cffi rich
```

## 🚀 Usage

Run the script using Python with various command-line arguments to customize your password generation:

```bash
python argonizer.py -n 1000 --uppercase --special -l 16
```

### 🔍 Example Commands

1. **Basic Usage with Interactive Salts:**

    ```bash
    python argonizer.py -n 500
    ```

    You'll be prompted to enter the number of salts and input them securely.

2. **Using a Configuration File for Salts:**

    ```bash
    python argonizer.py -n 1000 -c salts_config.txt
    ```

    Ensure `salts_config.txt` contains one salt per line.

3. **Customizing Character Sets and Length:**

    ```bash
    python argonizer.py -n 2000 --uppercase --special -l 20 --summary
    ```

    Generates a 20-character password including uppercase and special characters, and displays a summary.

## 📋 Command-Line Arguments

| Argument           | Description                                                   | Default     |
|--------------------|---------------------------------------------------------------|-------------|
| `-i`, `--initial`  | Initial string for password generation.                      | *None*      |
| `-n`, `--iterations` | Number of iterations/loops.                                 | **Required**|
| `-s`, `--salts`    | List of salts to use.                                         | *None*      |
| `-c`, `--config`   | Path to a config file containing salts (one per line).        | *None*      |
| `-u`, `--uppercase`| Include uppercase characters in the password.                | `False`     |
| `-sp`, `--special` | Include special characters in the password.                  | `False`     |
| `-l`, `--length`   | Desired length of the generated password.                    | `12`        |
| `--summary`        | Display a summary of the password generation parameters.     | `False`     |
| `--debug-level`    | Set debug level: 0 (no debug), 1 (detailed), 2 (minimal).    | `0`         |
| `--time_cost`      | Argon2 time cost (number of iterations).                     | `20`        |
| `--memory_cost`    | Argon2 memory cost in KiB.                                    | `1024000`   |
| `--parallelism`    | Argon2 parallelism (number of threads).                       | `1`         |
| `--min_lower`      | Minimum number of lowercase characters.                       | `1`         |
| `--min_digits`     | Minimum number of digit characters.                           | `1`         |
| `--min_upper`      | Minimum number of uppercase characters.                       | `1`         |
| `--min_special`    | Minimum number of special characters.                         | `1`         |

## 📝 Configuration File

If you prefer loading salts from a file, create a plain text file with one salt per line. Example `salts_config.txt`:

```
saltOne123
anotherSalt456
secureSalt789
```

Use the `-c` or `--config` flag to specify the path:

```bash
python argonizer.py -n 1000 -c salts_config.txt
```

## 🐞 Debugging

Adjust the verbosity of the script using the `--debug-level` flag:

- `0`: No debug output (default).
- `1`: Detailed debug information.
- `2`: Minimal debug information.

Example:

```bash
python argonizer.py -n 10 -u -sp -l 32 --summary --debug-level 2 -i my111nitial$$$tring -s saltOne123 anotherSalt456 secureSalt789
```

Example Output:

```bash
Initial string provided via argument.
3 salts provided via command-line arguments.

Starting password generation with 10 iterations...

Generated Password 01/10: _mnxik:RcCi_0EDt3B~uC]QI=72Uj(7v
Generated Password 02/10: w|9C99c])1r6mtH4eiBW<gVm=#q<@BlW
Generated Password 03/10: mN{a,KK69HQEsa3x9YqTVpkhgg6;6@@6
Generated Password 04/10: r`4mcIf;H#Lx`JA+?pDr6X7ssNWvZtFb
Generated Password 05/10: )#;W/pCGvn<GM{YV}:v=~GHm5$|5Mx|6
Generated Password 06/10: <I{ms^Y=T*KXXWnm8%!?Yf7g^qOcZ+UT
Generated Password 07/10: /O60ng51ZqEo^xF&M28F>w7|a)&Fw@Ko
Generated Password 08/10: <DyoFqV6j!PB2,=RrHj+Nph)F|jvCo48
Generated Password 09/10: B^Z>I.SJel=(c*JzV8XK[OesC!_sPH4+
Generated Password 10/10: u8lZiY(M]*vSiiAYH*!;|Np#0++q{KF&
Generating password... ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100% 0:02:03 0:00:00

                       Password Generation Summary
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Parameter                  ┃ Value                                     ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Initial String             │ my111nitial$$$tring                       │
├────────────────────────────┼───────────────────────────────────────────┤
│ Iterations                 │ 10                                        │
├────────────────────────────┼───────────────────────────────────────────┤
│ Number of Salts            │ 3                                         │
├────────────────────────────┼───────────────────────────────────────────┤
│ Salts                      │ saltOne123, anotherSalt456, secureSalt789 │
├────────────────────────────┼───────────────────────────────────────────┤
│ Include Uppercase          │ Yes                                       │
├────────────────────────────┼───────────────────────────────────────────┤
│ Include Special Characters │ Yes                                       │
├────────────────────────────┼───────────────────────────────────────────┤
│ Password Length            │ 32                                        │
├────────────────────────────┼───────────────────────────────────────────┤
│ Final Password             │ u8lZiY(M]*vSiiAYH*!;|Np#0++q{KF&          │
└────────────────────────────┴───────────────────────────────────────────┘
```


## ⚠️ Disclaimer and Security Considerations

While this **Argonizer** is designed to help generate strong, secure passwords, it's important to keep a few critical points in mind:

### 🔒 Security Considerations

- **Salts and Secrets**: Ensure the salts you use are unique and unpredictable. Avoid reusing salts across different passwords.
- **Initial String**: The initial string used in the generation process should be kept secure, as it's part of the password generation chain. Treat it like a password itself.
- **Argon2 Parameters**: The script uses default Argon2 settings, but you can modify the time cost, memory cost, and parallelism. Adjust these values to balance between security and performance based on your use case.
  
  - **Time Cost**: Increasing this makes brute force attacks slower, but also increases the time required to generate the password.
  - **Memory Cost**: Increasing this parameter makes attacks that require hardware (like GPUs) more difficult, as it consumes more memory.
  - **Parallelism**: Increasing the number of parallel threads can help balance the time-memory trade-off, but this should be carefully tuned based on your system's resources.

- **Generated Passwords**: Once passwords are generated, store them securely in a password manager. Avoid saving them in plain text or insecure locations.

### ⚠️ Disclaimer

- **No Warranty**: This script is provided "as is", without warranty of any kind. Use it at your own risk. The developers assume no responsibility for any loss of data, security breaches, or damages resulting from the use of this tool.
- **Best Practices**: Always follow best security practices when handling passwords and sensitive data. Use strong encryption to store any credentials securely.

In short, this tool helps generate strong passwords, but ultimate responsibility for how it's used—and ensuring secure practices—rests with you.

import argparse
import sys
from getpass import getpass
import hashlib
from argon2.low_level import hash_secret_raw, Type
from rich.console import Console
from rich.prompt import Prompt
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
from rich.table import Table
from rich.text import Text
from typing import List

# Define the character sets
LOWERCASE = 'abcdefghijklmnopqrstuvwxyz'
UPPERCASE = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
DIGITS = '0123456789'
SPECIAL = '!@#$%^&*()-_=+[]{}|;:,.<>?/`~'

def get_user_salts(console: Console) -> List[str]:
    """
    Prompt the user to input salts interactively.
    Each salt must be entered twice for confirmation.
    """
    while True:
        try:
            num_salts = int(Prompt.ask("Enter the number of salts you want to use", default="1"))
            if num_salts <= 0:
                console.print("[red]Number of salts must be a positive integer.[/red]")
                continue
            break
        except ValueError:
            console.print("[red]Please enter a valid integer.[/red]")

    salts = []
    for i in range(1, num_salts + 1):
        while True:
            salt1 = getpass(f"Enter salt {i} of {num_salts}: ")
            salt2 = getpass(f"Confirm salt {i}: ")
            if salt1 != salt2:
                console.print("[red]Salts do not match. Please try again.[/red]")
            elif not salt1:
                console.print("[red]Salt cannot be empty. Please try again.[/red]")
            else:
                salts.append(salt1)
                console.print(f"[green]Salt {i} confirmed.[/green]")
                break
    return salts

def load_salts_from_config(config_path: str, console: Console) -> List[str]:
    """
    Load salts from a configuration file.
    Each line in the file should contain one salt.
    """
    try:
        with open(config_path, 'r') as file:
            salts = [line.strip() for line in file if line.strip()]
            if not salts:
                console.print("[red]Config file is empty. Exiting.[/red]")
                sys.exit(1)
            console.print(f"[green]{len(salts)} salts loaded from config file.[/green]")
            return salts
    except FileNotFoundError:
        console.print(f"[red]Config file '{config_path}' not found. Exiting.[/red]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Error reading config file: {e}[/red]")
        sys.exit(1)

def map_hash_to_password(
    hash_str: str,
    charset: str,
    length: int,
    required_charsets: List[str],
    console: Console,
    debug_level: int = 0
) -> str:
    """
    Map the hash string to a password using the provided character set.
    Ensures that each required character set is represented at least once.
    """
    # Convert the hex string back to bytes for consistent mapping
    hash_bytes = bytes.fromhex(hash_str)

    # Step 1: Generate Base Password
    base_password = []
    for i in range(length):
        char = charset[hash_bytes[i % len(hash_bytes)] % len(charset)]
        base_password.append(char)
    base_password_str = ''.join(base_password)

    # Step 2: Apply Required Character Sets
    final_password = list(base_password_str)
    changed_indices = []  # To track which indices are changed

    for req_charset in required_charsets:
        # Determine position to replace
        pos = hash_bytes[len(changed_indices) % len(hash_bytes)] % length
        # Ensure we don't replace the same position multiple times
        while pos in changed_indices:
            pos = (pos + 1) % length
        # Replace character at pos with a character from req_charset
        new_char = req_charset[hash_bytes[(len(changed_indices) + len(required_charsets)) % len(hash_bytes)] % len(req_charset)]
        final_password[pos] = new_char
        changed_indices.append(pos)

    final_password_str = ''.join(final_password)

    if debug_level == 1:
        # Create Text objects for before and after
        before_text = Text(base_password_str, style="bold cyan")
        after_text = Text()

        for idx, char in enumerate(final_password_str):
            if idx in changed_indices:
                after_text.append(char, style="bold green")
            else:
                after_text.append(char, style="bold cyan")

        # Display the summary
        console.print("\n[bold magenta]Password Before Mapping:[/bold magenta]")
        console.print(before_text)
        console.print("[bold magenta]Password After Mapping:[/bold magenta]")
        console.print(after_text)

    return final_password_str

def generate_password(
    initial_string: str,
    salts: List[str],
    iterations: int,
    charset: str,
    length: int,
    required_charsets: List[str],
    console: Console,
    time_cost: int,
    memory_cost: int,
    parallelism: int,
    debug_level: int = 0
) -> str:
    """
    Generate a password by iteratively hashing the input string with salts.
    Ensures inclusion of required character types.
    """
    current_string = initial_string

    password = ""
    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Generating password...", total=iterations)
        for i in range(iterations):
            salt = salts[i % len(salts)]
            concatenated = current_string + salt
            if debug_level == 1:
                console.print(f"\n[bold yellow]Iteration {i+1}/{iterations}[/bold yellow]")
                console.print(f"[yellow]Concatenated String: {concatenated}[/yellow]")
                console.print(f"[yellow]Using Salt: {salt}[/yellow]\n")

            try:
                # Derive a fixed salt from the concatenated string using SHA-256
                # This ensures the salt is consistent for the same concatenated input
                fixed_salt = hashlib.sha256(concatenated.encode('utf-8')).digest()[:16]  # 16 bytes salt

                # Hash using Argon2 with fixed salt
                hash_bytes = hash_secret_raw(
                    secret=concatenated.encode('utf-8'),
                    salt=fixed_salt,
                    time_cost=time_cost,
                    memory_cost=memory_cost,
                    parallelism=parallelism,
                    hash_len=32,
                    type=Type.ID  # Using Argon2id for better security
                )

                # Convert hash bytes to a hex string for consistency
                hash_hex = hash_bytes.hex()

                if debug_level == 1:
                    console.print(f"[yellow]Argon2 Hash (hex): {hash_hex}[/yellow]\n")

                # Map the hash to the password with required character types
                password = map_hash_to_password(hash_hex, charset, length, required_charsets, console, debug_level)
                if debug_level == 1:
                    console.print(f"\n[bold green]Generated Password: {password}[/bold green]\n")
                # Update current_string for the next iteration
                current_string = password
            except Exception as e:
                console.print(f"[red]Error during hashing: {e}[/red]")
                sys.exit(1)
            progress.advance(task)
            if debug_level == 2:
                # For minimal debug, show the generated password per iteration
                console.print(f"[bold green]Generated Password {str(i+1).zfill(2)}/{iterations}: {password}[/bold green]")

    return password

def display_summary(
    initial_string: str,
    iterations: int,
    salts: List[str],
    include_upper: bool,
    include_special: bool,
    length: int,
    final_password: str,
    console: Console
):
    """
    Display a summary table of the generation parameters and the final password.
    """
    table = Table(title="Password Generation Summary", show_lines=True)

    table.add_column("Parameter", style="cyan", no_wrap=True)
    table.add_column("Value", style="magenta")

    table.add_row("Initial String", initial_string)
    table.add_row("Iterations", str(iterations))
    table.add_row("Number of Salts", str(len(salts)))
    table.add_row("Salts", ', '.join(salts))
    table.add_row("Include Uppercase", "Yes" if include_upper else "No")
    table.add_row("Include Special Characters", "Yes" if include_special else "No")
    table.add_row("Password Length", str(length))
    table.add_row("Final Password", final_password)

    console.print()  # Print a new line
    console.print(table)  # Directly print the table

def main():
    console = Console()

    parser = argparse.ArgumentParser(
        description="Argon2-based Password Generator",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '-i', '--initial', type=str, help='Initial string for password generation.'
    )
    parser.add_argument(
        '-n', '--iterations', type=int, required=True, help='Number of iterations/loops.'
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        '-s', '--salts', nargs='+', help='List of salts to use.'
    )
    group.add_argument(
        '-c', '--config', type=str, help='Path to a config file containing salts (one per line).'
    )
    parser.add_argument(
        '-u', '--uppercase', action='store_true', help='Include uppercase characters in the password.'
    )
    parser.add_argument(
        '-sp', '--special', action='store_true', help='Include special characters in the password.'
    )
    parser.add_argument(
        '-l', '--length', type=int, default=12, help='Desired length of the generated password.'
    )
    parser.add_argument(
        '--summary', action='store_true', help='Display a summary of the password generation parameters.'
    )
    parser.add_argument(
        '--debug-level', type=int, choices=[0, 1, 2], default=0, help='Set debug level: 0 (no debug), 1 (detailed), 2 (minimal).'
    )
    # New arguments for Argon2 parameters
    parser.add_argument(
        '--time_cost', type=int, default=20, help='Argon2 time cost (number of iterations).'
    )
    parser.add_argument(
        '--memory_cost', type=int, default=1024000, help='Argon2 memory cost in KiB.'
    )
    parser.add_argument(
        '--parallelism', type=int, default=1, help='Argon2 parallelism (number of threads).'
    )
    # Optional arguments for minimum character counts
    parser.add_argument(
        '--min_lower', type=int, default=1, help='Minimum number of lowercase characters.'
    )
    parser.add_argument(
        '--min_digits', type=int, default=1, help='Minimum number of digit characters.'
    )
    parser.add_argument(
        '--min_upper', type=int, default=1, help='Minimum number of uppercase characters.'
    )
    parser.add_argument(
        '--min_special', type=int, default=1, help='Minimum number of special characters.'
    )

    args = parser.parse_args()

    # Validate password length
    if args.length <= 0:
        console.print("[red]Password length must be a positive integer.[/red]")
        sys.exit(1)

    # Validate minimum counts and total length
    total_min = args.min_lower + args.min_digits
    if args.uppercase:
        total_min += args.min_upper
    if args.special:
        total_min += args.min_special

    if total_min > args.length:
        console.print("[red]The sum of minimum required characters exceeds the total password length.[/red]")
        sys.exit(1)

    # Get initial string
    if args.initial:
        initial_string = args.initial
        console.print("[green]Initial string provided via argument.[/green]")
    else:
        while True:
            initial1 = getpass("Enter the initial string: ")
            initial2 = getpass("Confirm the initial string: ")
            if initial1 != initial2:
                console.print("[red]Initial strings do not match. Please try again.[/red]")
            elif not initial1:
                console.print("[red]Initial string cannot be empty. Please try again.[/red]")
            else:
                initial_string = initial1
                console.print(f"[green]Initial string confirmed.[/green]")
                break

    # Get salts
    if args.salts:
        salts = args.salts
        console.print(f"[green]{len(salts)} salts provided via command-line arguments.[/green]")
    elif args.config:
        salts = load_salts_from_config(args.config, console)
    else:
        salts = get_user_salts(console)

    # Build the character set based on flags
    charset = LOWERCASE + DIGITS
    required_charsets = []
    # Add lowercase
    for _ in range(args.min_lower):
        required_charsets.append(LOWERCASE)
    # Add digits
    for _ in range(args.min_digits):
        required_charsets.append(DIGITS)
    # Add uppercase if requested
    if args.uppercase:
        for _ in range(args.min_upper):
            required_charsets.append(UPPERCASE)
        charset += UPPERCASE
    # Add special characters if requested
    if args.special:
        for _ in range(args.min_special):
            required_charsets.append(SPECIAL)
        charset += SPECIAL

    if not charset:
        console.print("[red]Character set is empty. At least one character type must be selected.[/red]")
        sys.exit(1)

    # Generate password
    console.print(f"\n[bold]Starting password generation with {args.iterations} iterations...[/bold]\n")
    final_password = generate_password(
        initial_string=initial_string,
        salts=salts,
        iterations=args.iterations,
        charset=charset,
        length=args.length,
        required_charsets=required_charsets,
        console=console,
        time_cost=args.time_cost,
        memory_cost=args.memory_cost,
        parallelism=args.parallelism,
        debug_level=args.debug_level
    )

    # Display summary if the flag is set
    if args.summary:
        display_summary(
            initial_string=initial_string,
            iterations=args.iterations,
            salts=salts,
            include_upper=args.uppercase,
            include_special=args.special,
            length=args.length,
            final_password=final_password,
            console=console
        )
    else:
        console.print(f"\n[bold green]Final Generated Password: {final_password}[/bold green]")

if __name__ == "__main__":
    main()

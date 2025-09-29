#!/usr/bin/env python3

import sys
import urllib.parse
import subprocess
import argparse


def blast_sequence(sequence, window_number=None):
    """Open NCBI BLAST in Safari with the provided sequence.

    Args:
        sequence: DNA/RNA sequence to BLAST
        window_number: Safari window number (1, 2, 3, etc.) to open URL in
    """

    # Clean up the sequence - remove whitespace and newlines
    sequence = "".join(sequence.split())

    if not sequence:
        print("Error: No sequence provided")
        return False

    # Validate sequence contains only valid nucleotide characters
    valid_chars = set("ATCGNatcgn")
    if not all(c in valid_chars for c in sequence):
        print("Warning: Sequence contains non-standard nucleotide characters")

    # Use the simple BLAST URL format you provided
    base_url = "https://blast.ncbi.nlm.nih.gov/Blast.cgi"

    # Simple parameters that work reliably
    params = {
        "PROGRAM": "blastn",
        "PAGE_TYPE": "BlastSearch",
        "LINK_LOC": "blasthome",
        "QUERY": sequence,
    }

    # Construct the URL
    url = f"{base_url}?" + urllib.parse.urlencode(params)

    # Open in Safari with optional window specification
    if window_number is not None:
        # Use AppleScript to open URL in specific Safari window
        applescript = f"""
        tell application "Safari"
            activate
            set windowCount to count of windows
            if windowCount < {window_number} then
                error "Window {window_number} does not exist. Safari has " & windowCount & " window(s)."
            end if
            tell window {window_number}
                set current tab to (make new tab with properties {{URL:"{url}"}})
            end tell
        end tell
        """

        try:
            subprocess.run(
                ["osascript", "-e", applescript],
                check=True,
                capture_output=True,
                text=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error: {e.stderr.strip()}")
            return False
    else:
        # Open in Safari (default behavior - opens in current/new window)
        subprocess.run(
            ["open", "-a", "Safari", url],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    return True


def cut_sequence(sequence, until_pos=None, from_pos=None):
    """Cut sequence based on until/from parameters."""
    if until_pos is not None and from_pos is not None:
        raise ValueError("Cannot specify both --until and --from")

    if until_pos is not None:
        if until_pos <= 0 or until_pos > len(sequence):
            raise ValueError(
                f"--until position {until_pos} is out of range (1-{len(sequence)})"
            )
        return sequence[:until_pos]

    if from_pos is not None:
        if from_pos < 1 or from_pos > len(sequence):
            raise ValueError(
                f"--from position {from_pos} is out of range (1-{len(sequence)})"
            )
        return sequence[from_pos - 1 :]

    return sequence


def main():
    parser = argparse.ArgumentParser(
        description="Open NCBI BLAST in Safari with auto-execution. Currently defaults to blastn.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ATCGATCGATCG                    # Provide sequence as argument
  %(prog)s --window 2 ATCGATCGATCG         # Open in Safari window 2
  %(prog)s -j 50 ATCGATCGATCG...           # Junction mode: full (win 1), up to pos 50 (win 2), from pos 51 (win 3)
  %(prog)s --until-pos 10 ATCGATCGATCG     # Use first 10 bp
  %(prog)s --from 5 ATCGATCGATCG           # Use bp from position 5 onwards
  %(prog)s --window 1 --from 5 ATCGATCG    # Open in window 1, use bp from position 5

        """,
    )

    parser.add_argument(
        "sequence", nargs="?", help="DNA/RNA sequence to BLAST"
    )

    parser.add_argument(
        "--window",
        "-w",
        type=int,
        dest="window_number",
        help="Safari window number to open URL in (1, 2, 3, etc.)",
    )

    parser.add_argument(
        "--junction",
        "-j",
        type=int,
        dest="junction_pos",
        help="Junction position: opens 3 BLASTs (full sequence in window 1, up to position in window 2, from position onwards in window 3)",
    )

    parser.add_argument(
        "--until",
        "-u",
        type=int,
        dest="until_pos",
        help="Cut sequence to include all bp up to and including position X",
    )
    parser.add_argument(
        "--from",
        "-f",
        type=int,
        dest="from_pos",
        help="Cut sequence to include all bp from position X onwards",
    )

    args = parser.parse_args()

    # Get sequence from argument
    if not args.sequence:
        print("Error: No sequence provided")
        parser.print_help()
        return 1

    sequence = args.sequence

    # Check for conflicting options
    if args.junction_pos and (args.until_pos or args.from_pos):
        print("Error: Cannot use --junction with --until or --from")
        return 1

    if args.junction_pos and args.window_number:
        print(
            "Error: Cannot use --junction with --window (junction automatically uses windows 1, 2, and 3)"
        )
        return 1

    # Handle junction mode - opens 3 BLASTs
    if args.junction_pos:
        j = args.junction_pos
        if j < 1 or j > len(sequence):
            print(
                f"Error: Junction position {j} is out of range (1-{len(sequence)})"
            )
            return 1

        print(f"Opening 3 BLASTs at junction position {j}:")
        print(f"  Window 1: Full sequence ({len(sequence)} bp)")
        print(f"  Window 2: Up to position {j} ({j} bp)")
        print(
            f"  Window 3: From position {j+1} onwards ({len(sequence) - j} bp)"
        )

        # Full sequence in window 1
        success1 = blast_sequence(sequence, window_number=1)
        if not success1:
            print("Error: Failed to open BLAST in window 1")
            return 1

        # Up to junction in window 2
        seq_until = sequence[:j]
        success2 = blast_sequence(seq_until, window_number=2)
        if not success2:
            print("Error: Failed to open BLAST in window 2")
            return 1

        # From junction onwards in window 3
        seq_from = sequence[j:]
        success3 = blast_sequence(seq_from, window_number=3)
        if not success3:
            print("Error: Failed to open BLAST in window 3")
            return 1

        return 0

    # Cut sequence if requested
    try:
        sequence = cut_sequence(sequence, args.until_pos, args.from_pos)
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    success = blast_sequence(sequence, args.window_number)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

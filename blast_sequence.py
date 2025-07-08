#!/usr/bin/env python3

import sys
import urllib.parse
import subprocess
import argparse


def blast_sequence(sequence):
    """Open NCBI BLAST in Safari with the provided sequence."""

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

    # Open in Safari (macOS)
    subprocess.run(
        ["open", "-a", "Safari", url],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return True


def cut_sequence(sequence, until=None, from_pos=None):
    """Cut sequence based on until/from parameters."""
    if until is not None and from_pos is not None:
        raise ValueError("Cannot specify both --until and --from")

    if until is not None:
        if until <= 0 or until > len(sequence):
            raise ValueError(
                f"--until position {until} is out of range (1-{len(sequence)})"
            )
        return sequence[:until]

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
  %(prog)s ATCGATCGATCG               # Provide sequence as argument
  %(prog)s --until 10 ATCGATCGATCG    # Use first 10 bp
  %(prog)s --from 5 ATCGATCGATCG      # Use bp from position 5 onwards
  %(prog)s --until 10 --from 5 ATCGATCGATCG    # Use first 10 bp and bp from position 5 onwards

        """,
    )

    parser.add_argument("sequence", nargs="?", help="DNA/RNA sequence to BLAST")

    parser.add_argument(
        "--until",
        "-u",
        type=int,
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

    # Get sequence from argument or stdin
    if args.sequence:
        sequence = args.sequence
    if not sequence:
        print("No sequence provided")
        return 1

    # Cut sequence if requested
    try:
        sequence = cut_sequence(sequence, args.until, args.from_pos)
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    success = blast_sequence(sequence)
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python
import os
import sys  # Required for command-line arguments
import json


def find_hv_entry(entry):
    directory_path = "hvreads"
    file_id, _ = entry.split(".")
    filename = file_id + ".hvreads.json"

    file_path = os.path.join(directory_path, filename)
    print(file_path)
    try:
        with open(file_path, "r") as file:
            data = json.load(file)
            print("hello")

            # Check if the entry is in the data
            if entry in data:
                read_data = data[entry]
                quality_scores = read_data[0]
                print(entry, quality_scores)

            else:
                print(f"Entry {entry} not found in the data.")
    except FileNotFoundError:
        return "JSON file not found."
    except json.JSONDecodeError:
        return "Error decoding JSON."
    except Exception as e:
        return f"An error occurred: {str(e)}"


def main():
    if len(sys.argv) < 2:
        print("Usage: python return_full_sam_record.py <entry>")
        sys.exit(1)

    entry = sys.argv[1]
    find_hv_entry(entry)


if __name__ == "__main__":
    main()

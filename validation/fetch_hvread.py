#!/usr/bin/env python
import os
import sys  # Required for command-line arguments
import json


def find_hv_entry(entry):
    directory_path = "hvreads"
    if entry.startswith("M"):
        file_id = entry.split("_")[1].split(".")[0]
    else:
        file_id, _ = entry.split(".")
    filename = file_id + ".hvreads.json"

    file_path = os.path.join(directory_path, filename)
    print(file_path)
    try:
        with open(file_path, "r") as file:
            data = json.load(file)

            # Check if the entry is in the data
            if entry in data:
                read_data = data[entry]
                print(entry, read_data)
                print("\n")

            else:
                print(f"Entry {entry} not found in the data.")
                print("\n")
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

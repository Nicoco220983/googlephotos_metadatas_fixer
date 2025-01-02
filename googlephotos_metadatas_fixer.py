import os
import sys
import json
from datetime import datetime
import argparse


class GooglephotosMetatadasFixer:

    def __init__(self, quiet=False):
        self.nb_processed = 0
        self.warnings = []
        self.quiet = quiet

    def process_metadata_file(self, metadata_fpath: str):
        media_fpath = os.path.splitext(metadata_fpath)[0]
        if not os.path.exists(media_fpath):
            self.log_warn(f'Media file not found for "{metadata_fpath}"')
            return

        with open(metadata_fpath, 'r', encoding='utf-8') as metadata_file:
            metadata = json.load(metadata_file)

        time_s = metadata.get("photoTakenTime",{}).get("timestamp")
        if not isinstance(time_s, str) or not time_s.isnumeric():
            self.log_warn(f'No valid date in "{metadata_file}"')
            return

        self.set_file_dates(media_fpath, int(time_s))

    def process_directory(self, dirpath: str):
        for root, _, fnames in os.walk(dirpath):
            for fname in fnames:
                if fname.endswith(".json"):
                    metadata_fpath = os.path.join(root, fname)
                    self.process_metadata_file(metadata_fpath)


    def set_file_dates(self, fpath: str, time_s: int):
        os.utime(fpath, (time_s, time_s))  # Modification (atime, mtime)
        self.log_info(f'File processed "{fpath}"')
        self.nb_processed += 1
    

    def log_info(self, msg: str):
        if not self.quiet:
            print(msg)
    

    def log_warn(self, msg: str):
        if not self.quiet:
            print("WARNING: " + msg, file=sys.stderr)
        self.warnings.append(msg)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('paths', nargs='*')
    parser.add_argument('--quiet', action='store_true')
    args = parser.parse_args()
    input_paths = args.paths or []
    if len(input_paths) == 0:
        res = input('Write path of (or simply drag and drop) directory to process:\n')
        input_paths.append(res.strip('"'))
    for input_path in input_paths:
        if not os.path.exists(input_path):
            print(f"File (or directory) does not exist: {input_path}", file=sys.stderr)
            sys.exit(1)
    fixer = GooglephotosMetatadasFixer(
        quiet=args.quiet,
    )
    for input_path in input_paths:
        if os.path.isdir(input_path):
            fixer.process_directory(input_path)
        else:
            fixer.process_metadata_file(
                input_path
                if input_path.endswith(".json")
                else input_path + ".json"
            )
    if not args.quiet:
        print("Nb files processed:", fixer.nb_processed)
        if len(fixer.warnings) > 0:
            print("Nb warnings:", len(fixer.warnings))

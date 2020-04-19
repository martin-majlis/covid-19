#!/usr/bin/env python3

# This scripts converts data from https://onemocneni-aktualne.mzcr.cz_covid-19 into time series based on
# the commit history.

import csv
import json
import sys
from collections import defaultdict
from datetime import datetime
from typing import Dict
from datetime import date

from pydriller import GitRepository
from pydriller import RepositoryMining

POMUCKY_FILE_NAME='pomucky.json'

def transform(root_dir: str, source_dir: str, target_dir: str) -> None:
    print(f"Root: {root_dir}, Source: {source_dir}, Target: {target_dir}")
    gr = GitRepository(root_dir)

    commits = gr.get_commits_modified_file(f"{source_dir}/{POMUCKY_FILE_NAME}")

    stats = defaultdict(
        lambda: defaultdict(
            lambda: defaultdict(int)
        )
    )  # type: Dict[date, Dict[str, Dict[str, int]]]
    dates = set()
    pomucky = set()
    kraje = set()

    for commit in RepositoryMining(root_dir, only_commits=commits).traverse_commits():
        print(f"{commit.msg}: {commit}")
        for m in commit.modifications:
            if m.filename == POMUCKY_FILE_NAME:
                payload = json.loads(m.source_code)
                d = datetime.fromisoformat(payload['modified'])
                dates.add(d.date())
                for rec in payload['data']:
                    pomucky.add(rec['pomucka'])
                    kraje.add(rec['kraj'])
                    if rec['pocet']:
                        stats[d.date()][rec['kraj']][rec['pomucka']] = int(rec['pocet'])

    previous = defaultdict(
        lambda: defaultdict(int)
    )  # type: Dict[str, Dict[str, int]]
    with open(f"{target_dir}/pomucky-simple.csv", mode="w") as fh:
        writer = csv.writer(fh)
        writer.writerow(["datum", "kraj", "pomucka", "pocet", "zmena"])
        for d in sorted(dates):
            for kraj in sorted(kraje):
                for pomucka in sorted(pomucky):
                    writer.writerow([
                        d,
                        kraj,
                        pomucka,
                        stats[d][kraj][pomucka],
                        stats[d][kraj][pomucka] - previous[kraj][pomucka],
                    ])
                    previous[kraj][pomucka] = stats[d][kraj][pomucka]

    with open(f"{target_dir}/pomucky-dates.csv", mode="w") as fh:
        writer = csv.writer(fh)
        writer.writerow(["pomucka", "kraj"] + [str(d) for d in sorted(dates)])
        for kraj in sorted(kraje):
            for pomucka in sorted(pomucky):
                writer.writerow(
                    [pomucka, kraj] +
                    [stats[d][kraj][pomucka] for d in sorted(dates)]
                )

    with open(f"{target_dir}/pomucky-kraje.csv", mode="w") as fh:
        writer = csv.writer(fh)
        writer.writerow(["datum", "pomucka"] + list(sorted(kraje)))
        for d in sorted(dates):
            for pomucka in sorted(pomucky):
                writer.writerow(
                    [d, pomucka] +
                    [stats[d][kraj][pomucka] for kraj in sorted(kraje)]
                )



if __name__ == "__main__":
    transform(sys.argv[1], sys.argv[2], sys.argv[3])
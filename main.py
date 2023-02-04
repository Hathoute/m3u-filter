import sys
from pathlib import Path
from typing import TextIO
import regex

cur_line = 0

names_matcher = {
    "bein-sports-hevc": r"BEIN SPORTS (.+) HEVC",
    "bein-premium-hevc": r"BEIN PREMIUM (.+) HEVC",
    "ssc-4k": r"VIP - SSC (.+) 4K",
    "arryadia": r"MA - ARRYADIA LIVE UHD ◉"
}


class M3UFile:
    def __init__(self, entries):
        self.entries = entries

    def __str__(self):
        output = "#EXTM3U\n"
        for entry in self.entries:
            output += str(entry)

        return output

    def write(self, f: TextIO):
        f.write("#EXTM3U\n")
        for entry in self.entries:
            f.write(str(entry))

    @staticmethod
    def parse(f: TextIO):
        global cur_line

        assert f.readline() == "#EXTM3U\n"
        cur_line += 1

        entries = []
        while 1:
            try:
                entry = M3UEntry.parse(f)
            except Exception as e:
                print(str(e))
                continue

            if entry is None:
                break

            entries.append(entry)

        return M3UFile(entries)


class M3UEntry:
    def __init__(self, eid, tags: dict, name, url):
        self.id = eid
        self.tags = tags
        self.name = name
        self.url = url

    def __str__(self):
        output = "#EXTINF:" + str(self.id)
        for tag in self.tags.keys():
            output += f' {tag}="{self.tags[tag]}"'

        output += f",{self.name}\n"
        output += f"{self.url}\n"
        return output

    @staticmethod
    def parse(f: TextIO):
        global cur_line

        line1 = f.readline()
        cur_line += 1
        if not line1:
            return None

        m = regex.match(r'#EXTINF:(-?\d+)( ([\w\-]+)="([^"]*)")*,([^"]+)\n', line1)
        if not m:
            raise Exception(f"Line {cur_line} - Could not match {line1}")

        eid = m.captures(1)[0]
        tags = {}
        for i in range(len(m.captures(3))):
            tags[m.captures(3)[i]] = m.captures(4)[i]

        name = m.captures(5)[0]
        url = f.readline()[:-1]
        cur_line += 1
        return M3UEntry(eid, tags, name, url)


def filter_m3u(m3u: M3UFile):
    stats = {k: 0 for k in names_matcher.keys()}
    filtered = []
    for entry in m3u.entries:
        for match in names_matcher.keys():
            if regex.match(names_matcher[match], entry.name):
                stats[match] += 1
                filtered.append(entry)
                break

    print("Statistics: ")
    for stat in stats.keys():
        print(f"\t{stat}: {stats[stat]}")

    return M3UFile(filtered)


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 main.py input.m3u output.m3u")
        exit(1)

    path = Path(sys.argv[1])
    out = Path(sys.argv[2])
    if not path.exists():
        print(f"File {path} does not exist.")
        exit(1)

    with open(path, mode="r", encoding="utf-8") as file:
        m3u = M3UFile.parse(file)

    filtered_m3u = filter_m3u(m3u)
    with open(out, mode="w", encoding="utf-8") as file:
        filtered_m3u.write(file)

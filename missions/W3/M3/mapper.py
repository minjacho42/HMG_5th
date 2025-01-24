import sys

try:
    for line in sys.stdin:
        line = line.strip()
        words = line.split()
        for word in words:
            print(f"{word}\t1")
except Exception as e:
    sys.stderr.write(f"Mapper error: {e}\n")
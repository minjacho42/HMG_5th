import sys
from collections import defaultdict

try:
    word_count = defaultdict(int)

    # 입력 데이터를 처리
    for line in sys.stdin:
        line = line.strip()
        word, count = line.split("\t")
        word_count[word] += int(count)

    # 키를 기준으로 정렬하여 출력
    for word, count in sorted(word_count.items(), key=lambda x: x[1], reverse=True):
        print(f"{word}\t{count}")

except Exception as e:
    sys.stderr.write(f"Reducer error: {e}\n")

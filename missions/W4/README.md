# M1: Spark Standalone Cluster with Docker

이 프로젝트는 **Apache Spark Standalone Cluster**를 **Docker + Docker Compose**를 사용하여 구축하고,  
`wordcount.py` 스크립트를 실행하여 **텍스트 파일 내 단어 개수를 세는 Spark 애플리케이션**을 수행합니다.

---

## 프로젝트 구성

```
M1/
├── share/                    # 공유 디렉토리 (Spark 클러스터에서 접근 가능)
│   ├── output/               # Spark 작업 결과 저장 폴더
│   ├── demian.txt            # 입력 텍스트 파일
│   ├── wordcount.py          # WordCount Spark Job (PySpark)
├── src/                      # 설치 관련 파일
│   ├── spark-3.5.4-bin-hadoop3.tgz  # Spark 설치 파일
├── .gitignore
├── docker-compose.yml        # Spark 클러스터 환경 구성
├── Dockerfile                # Spark 컨테이너 빌드 설정
```

---

## 1. 프로젝트 실행 방법

### **1. Docker Compose로 Spark 클러스터 실행**
```
docker-compose up -d --build
```
- Spark Master와 2개의 Worker 컨테이너가 실행됩니다.
- **Spark UI 확인:** [http://localhost:8080](http://localhost:8080)

### **2. Spark WordCount Job 실행**
Spark 클러스터가 정상적으로 실행되면, `wordcount.py`를 실행하여 **demian.txt의 단어 개수 분석**을 수행합니다.

```
docker exec -it M1-spark-master-1 spark-submit \
  --master spark://spark-master:7077 \
  /opt/spark/work-dir/share/wordcount.py \
  /opt/spark/work-dir/share/demian.txt \
  /opt/spark/work-dir/share/output
```
- **입력:** `demian.txt` (텍스트 파일)
- **출력:** `output/` 디렉토리에 CSV 파일로 저장됨.

---

## 2. Spark WordCount 실행 결과

Spark Job이 완료되면 **출력 디렉토리 (`output/`)** 에 결과가 저장됩니다.  
출력 파일 예시:
```
output/
├── part-00000.csv
├── part-00001.csv
├── part-00002.csv
├── part-00003.csv
```
각 파일에는 단어와 출현 횟수가 포함됩니다.

출력 확인:
```
cat share/output/part-00000.csv
```

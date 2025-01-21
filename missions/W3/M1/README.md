# Single Node Cluster Hadoop

## Docker compose & container 실행 명령어

### Hadoop service 시작하기
```docker compose up -d --build```
### Hadoop service 종료하기
```docker compose down```

### Hadoop service volume 삭제와 함께 종료하기
```docker compose down --volumes```

### Hadoop service 이미지 삭제와 함께 종료하기
```docker compose down --rmi local```

### Docker container로 접속
```docker exec -it hadoop-container /bin/bash```

## Docker 내부에서 hdfs 명령
### hdfs에 디렉토리 만들기 (mkdir)
```hdfs dfs -mkdir <your_directory_name>```
### hdfs에 파일 추가하기 (put)
```hdfs dfs -put <your_file_name> <dest_path_name>```
### hdfs에 file list 확인하기 (ls)
```hdfs dfs -ls <target_path_name>```
### hdfs에서 file 가져오기. (get)
```hdfs dfs -get <hdfs_path> <local_path>```

## 웹 UI로 접근하기
* http://127.0.0.1:9870/explorer.html#/ 를 통해서 접근 가능하다.
* 이때, 우측 상단의 아이콘들을 통해, 디렉토리를 만들고 새로운 파일을 업로드 할 수 있다.
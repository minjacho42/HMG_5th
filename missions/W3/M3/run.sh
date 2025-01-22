hadoop jar $HADOOP_HOME/share/hadoop/tools/lib/hadoop-streaming-*.jar \
    -files /hadoop/mapper.py,/hadoop/reducer.py \
    -input /input/demian.txt \
    -output /output/wordcount \
    -mapper "python3 mapper.py" \
    -reducer "python3 reducer.py"
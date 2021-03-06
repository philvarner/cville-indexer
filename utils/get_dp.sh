#!/bin/bash

# March 16, 1893 2070291
# Dec 31 1964 2683350

# have starting at 2105622
start_id=2070000
end_id=2080000

retrieve(){
  url="http://fedoraproxy.lib.virginia.edu/fedora/objects/uva-lib:$1/methods/djatoka:StaticSDef/getStaticImage"
  echo "--> $url"
  filename=$1.jpg
  curl -s -f $url -o $filename
  size=$(du -h "$filename" | cut -f1)
  if [[ $? -eq 0 && $size > "0B" && $size < "3." ]]
  then
    aws s3 cp $filename s3://philvarner-sources/daily_progress/$filename
  fi
  rm $filename
  sleep 1
  return 0
}

echo "running for $start_id to $end_id"
. `which env_parallel.bash`
seq -f "%1.0f" $start_id $end_id | env_parallel -P 10 retrieve {}


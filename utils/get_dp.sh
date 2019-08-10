#!/bin/bash

# March 16, 1893 2070291
# Dec 31 1964 2683350

# have starting at 2105622
start_id=2109022
end_id=2683350

retrieve(){
  url="http://fedoraproxy.lib.virginia.edu/fedora/objects/uva-lib:$1/methods/djatoka:StaticSDef/getStaticImage"
  echo "--> $url"
  curl -s -f $url | aws s3 cp - s3://philvarner-sources/daily_progress/$1.jpg
  sleep 1
  return 0
}

echo "running for $start_id to $end_id"
. `which env_parallel.bash`
seq -f "%1.0f" $start_id $end_id | env_parallel -P 10 retrieve {}


echo $(grep -m 1 Length <(wget $1 -O - 2>&1); kill $!) | cut -d" " -f2

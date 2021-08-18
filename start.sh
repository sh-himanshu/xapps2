#!/usr/bin/env bash

# Fail fast
set -euo pipefail

# Run Python Script
echo -e "Running python script\n"
poetry run python3 -m xapps2
echo "SUCCESS"

# Download apps from URLS
while read line;
do  
    lineSplit=(${line//|/ })
    url=$(echo ${lineSplit[0]} | xargs) 
    pkg_name=$(echo ${lineSplit[1]} | xargs)

    if ! [[ $pkg_name =~ .+\.(apk|zip)$ ]]
    then
        pkg_name="$RANDOM.apk"
    fi

    echo $pkg_name
    curl -sL -o "$pkg_name" "$url"
done < apk_urls.txt

# Compress Output
mkdir -p pakages && mv *.apk pakages/
tar -czvf pakages.tar.gz pakages
mkdir release && mv pakages.tar.gz *.zip release/

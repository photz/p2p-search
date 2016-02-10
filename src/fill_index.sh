PORT=3128

while read url
do
    echo "indexing $url..."
    printf "GET %s\n\n" $url | netcat localhost $PORT
done < urls.txt


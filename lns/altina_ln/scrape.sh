IFS=$'\r\n'
for i in $(curl http://skythewood.blogspot.com/p/altina-sword-princess.html | tr '<' '\n' | grep ASP | sed -nE 's/.*"(http.*)ASP(.*)\.html">(.*)/\1ASP\2\.html|ASP-\2-\3\.htm/p'); do
  l=$(echo "$i" | awk -F '|' '{print $1}')
  o=$(echo "$i" | awk -F '|' '{print $2}' | sed 's/\:/_/g; s/ /_/g; s/&nbsp;/_/g; s/&amp;/_/g; s/&#8217;/_/g; s/\//_/g; s/__/_/g')
  curl -L "$l" | sed -n '/<h3/,/post-footer/p' > "$o"
 done

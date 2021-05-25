### Trim trailing spaces
```bash
var='   space test   '
echo $var | sed -n -e 'l'
echo "$var" | sed -n -e 'l'

printf "%s" "${var#"${var%%[![:space:]]*}"}" | sed -n -e 'l'
printf "%s" "${var%"${var##*[![:space:]]}"}" | sed -n -e 'l'


# Space characters include: tab, newline, vertical tab, form feed, carriage return, and space.
# cf. "POSIX character classes" at http://en.wikipedia.org/wiki/Regular_expression

var="${var#"${var%%[![:space:]]*}"}"   # remove leading whitespace characters
var="${var%"${var##*[![:space:]]}"}"   # remove trailing whitespace characters

echo "$var" | sed -n -e 'l'
```

#!/bin/bash

[ -z "$1" ] && {
    echo "no git repo path set"
    exit 1
}
path=$( readlink -f "$1" )
cd $path

from="01.01.2015 00:00"
to="01.09.2017 00:00"
file_filter="*.*"
git_filter=""

tmpf=$( mktemp )
python3 <<HERE > $tmpf
from bptbx import b_date
from dateutil.relativedelta import *
b_date.print_intervals('${from}', '${to}',
    relativedelta(months=+1), '%d.%m.%Y %H:%M', '%m/%d/%y %H:%M')
HERE
# cat $tmpf

echo "begin,end,ins,del,diff"
cat $tmpf | while read line;
do
    begin=$( awk '{print $1" "$2 }' <<< $line )
    end=$( awk '{print $3" "$4 }' <<< $line )
    git --no-pager log --numstat --pretty="%H" \
    --before="$end" --after="$begin" $git_filter "$file_filter" | awk \
    -v beg="$begin" -v end="$end" \
    'NF==3 {plus+=$1; minus+=$2; diff=diff+$1-$2} END { printf(beg","end",%d,%d,%d\n", plus, minus, diff)}'
done | sed -e "s/ 00:00//g"

rm -f $tmpf 

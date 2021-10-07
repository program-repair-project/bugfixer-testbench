for f in `find . -name "*.h" | xargs grep -l "__attribute__ ((visibility(\"default\")))"`; do
    echo $f
    sed "s/__attribute__ ((visibility(\"default\")))//" $f -i 
done
for f in `find . -name "*.h.in" | xargs grep -l "__attribute__ ((visibility(\"default\")))"`; do
    echo $f
    sed "s/__attribute__ ((visibility(\"default\")))//" $f -i 
done

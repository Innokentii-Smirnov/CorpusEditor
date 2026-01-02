test="$1"
expected="$test/expected"
rm -r $expected
cp -r "$test/output" $expected

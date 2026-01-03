test="$1"
expected="$test/expected"
if [ -d "$expected" ]; then
  rm -r "$expected"
fi
cp -r "$test/output" $expected

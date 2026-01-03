script_dir=$(dirname "$0")
test="$1"
output="$test/output"
if [ -d "$output" ]; then
  rm -r "$output"
fi
"$script_dir"/make_config.sh "$test" "input" "output" > config.json
~/environment2/bin/python ~/CorpusEditor/src/edit_corpus.py
rm config.json
diff -r "$test/expected" "$test/output"

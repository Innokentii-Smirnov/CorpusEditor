script_dir=$(dirname "$0")
test="$1"
"$script_dir"/make_config.sh "$test" > config.json
~/environment2/bin/python ~/CorpusEditor/src/edit_corpus.py
diff -r "$test/expected" "$test/output"

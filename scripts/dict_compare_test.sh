script_dir=$(dirname "$0")
test="$1"
# Prepare the data for in-place editing
corpus="$test/corpus"
if [ -d "$corpus" ]; then
  rm -r "$corpus"
fi
cp -r "$test/input" "$corpus"
# Apply the changes to the corpus
"$script_dir"/make_config.sh "$test" "corpus" "corpus" > config.json
~/environment2/bin/python ~/CorpusEditor/src/edit_corpus.py
rm config.json
# Generate a new dictionary
generated="$test/generated"
"$script_dir"/make_dict_gen_config.sh "$test/corpus" "$generated" > config.json
~/environment2/bin/python ~/DictionaryGenerator/src/generate_dictionary.py
rm config.json
# Preprocess the imported dictionary
exported="$test/exported"
jq -S --tab . "$exported/Dictionary.json" > "$exported/SortedDictionary.json"
# Compare the dictionaries
diff -s "$exported/SortedDictionary.json" "$generated/Dictionary.json" > diff.txt
kate diff.txt

script_dir=$(dirname "$0")
test="$1"
"$script_dir"/make_dict_gen_config.sh "$test" > config.json
~/environment2/bin/python ~/DictionaryGenerator/src/generate_dictionary.py
rm config.json

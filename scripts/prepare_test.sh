script_dir=$(dirname "$0")
test="$1"
"$script_dir"/copy_data.sh "$test"
"$script_dir"/generate_dictionary.sh "$test"

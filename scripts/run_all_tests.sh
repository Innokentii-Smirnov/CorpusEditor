script_dir=$(dirname "$0")
directory="$1"
"$script_dir"/clear.sh "$directory"
for name in $(ls "$directory"); do
  test="$directory/$name"
  if [ -d "$test" ]; then
    "$script_dir"/run_test.sh "$test"
  fi
done

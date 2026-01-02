directory="$1"
for name in $(ls "$directory"); do
  dir="$directory/$name"
  if [ -d "$dir" ]; then
    echo $dir
    output="$dir/output"
    if [ -d "$output" ]; then
      rm -r "$output"
    fi
    ls $dir
  fi
done

while read -r line; do
  kate "$line"
done < skipped_files.txt

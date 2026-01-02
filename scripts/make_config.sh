test="$1"
jq -n --arg changesFile "$test/exported/Changes.json" \
      --arg inputDirectory "$test/input" \
      --arg outputDirectory "$test/output" \
   '{$changesFile, $inputDirectory, $outputDirectory}'

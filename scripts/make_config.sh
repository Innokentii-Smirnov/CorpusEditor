test="$1"
input="$2"
output="$3"
jq -n --arg changesFile "$test/exported/Changes.json" \
      --arg inputDirectory "$test/$input" \
      --arg outputDirectory "$test/$output" \
   '{$changesFile, $inputDirectory, $outputDirectory}'

test="$1"
jq -n --arg inputDirectory "$test/input" \
      --arg outputDirectory "$test" \
   '{$inputDirectory, $outputDirectory}'

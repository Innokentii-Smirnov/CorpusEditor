input="$1"
output="$2"
jq -n --arg inputDirectory "$input" \
      --arg outputDirectory "$output" \
   '{$inputDirectory, $outputDirectory}'

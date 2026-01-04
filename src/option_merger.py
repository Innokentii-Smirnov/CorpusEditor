from morph import Morph, MultiMorph
from more_itertools import first_true

def merge_identical_options(index: str, morph: MultiMorph,
                            selections: list[str]) -> MultiMorph:
  """
  Unify identical analysis options and select the resulting option
  if either of the unified options is selected.
  """
  new_options = dict[str, str]()
  for letter, option in morph.morph_tags.items():
    if option in new_options.values():
      old_complete_index = index + letter
      if old_complete_index in selections:
        selections.remove(old_complete_index)
      identical_option_letter = first_true(
        morph.morph_tags,
        pred=lambda letter: morph.morph_tags[letter] == option
      )
      if identical_option_letter is not None:
        new_complete_index = index + identical_option_letter
        if new_complete_index not in selections:
          selections.append(new_complete_index)
    else:
      new_options[letter] = option
  return MultiMorph(morph.segmentation, morph.translation,
                    new_options, morph.pos, morph.det, None)

if __name__ == '__main__':
  print('Starting test.')
  data = [
    ['tav-ud-o @ u.B. @ { a → NEG-MOD.PAT} { b → NEG-MOD.PAT} @ verb @ ',
     'tav-ud-o @ u.B. @ { a  → NEG-MOD.PAT} @ verb @ ', '1', ' 1a 1b', ' 1a'],
    ['nav-an-ed-a @ weiden @ { a → CAUS-FUT-3A.SG} { b → CAUS-FUT-3A.SG} @ verb @ ',
     'nav-an-ed-a @ weiden @ { a  → CAUS-FUT-3A.SG} @ verb @ ',
     '2', ' 1a 2a 2b 3a', ' 1a 2a 3a'],
    ['tap-t-an-i @ u.B. @ { a → t-CAUS-ANTIP} { b → t-CAUS-TR.IMP} @ verb @ ',
     'tap-t-an-i @ u.B. @ { a  → t-CAUS-ANTIP}{ b  → t-CAUS-TR.IMP} @ verb @ ',
     '3', ' 1a 3b 3a 2b 2a', ' 1a 3b 3a 2b 2a'],
    # Hypothetical cases: only second selected
    ['tav-ud-o @ u.B. @ { a → NEG-MOD.PAT} { b → NEG-MOD.PAT} @ verb @ ',
     'tav-ud-o @ u.B. @ { a  → NEG-MOD.PAT} @ verb @ ', '1', ' 1b', ' 1a'],
    ['nav-an-ed-a @ weiden @ { a → CAUS-FUT-3A.SG} { b → CAUS-FUT-3A.SG} @ verb @ ',
     'nav-an-ed-a @ weiden @ { a  → CAUS-FUT-3A.SG} @ verb @ ',
     '2', ' 1a 2b 3a', ' 1a 3a 2a'],
  ]
  for origin, target, index, str_selections, expected_selections in data:
    print(origin)
    print(str_selections)
    morph = Morph.parse(origin)
    assert isinstance(morph, MultiMorph)
    selections = str_selections.split(' ')
    new_morph = merge_identical_options(index, morph, selections)
    print(new_morph)
    assert str(new_morph) == target
    new_str_selections = ' '.join(selections)
    print(new_str_selections)
    assert new_str_selections == expected_selections
    print()

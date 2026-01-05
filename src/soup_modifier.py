from bs4 import BeautifulSoup, Tag
from morph import Morph, MultiMorph
from typing import Callable
from logging import getLogger, INFO, FileHandler
from option_merger import merge_identical_options_if_multi
logger = getLogger(__name__)
logger.setLevel(INFO)
handler = FileHandler('Log.txt', 'w', encoding='utf-8')
logger.addHandler(handler)
morph_logger = getLogger('morphological_analysis')
morph_logger.addHandler(FileHandler('{0}.log'.format(morph_logger.name), 'w', encoding='utf-8'))

mrpNaN = 'mrpNaN'

def get_word_language(line_language: str, tag: Tag) -> str:
  if 'lg' in tag.attrs and isinstance(tag['lg'], str):
    return tag['lg']
  else:
    return line_language

def get_free_index(tag: Tag) -> int:
  """ For a given XML tag of a word (w),
  determine the morphological analysis with the highest number
  and return that number incremented by one.
  """
  free_index = 1
  for attr, value in tag.attrs.items():
      if attr.startswith('mrp') and attr != 'mrp0sel':
          index_str = attr.removeprefix('mrp')
          if index_str.isdigit():
              current_index = int(index_str)
              if current_index >= free_index:
                  free_index = current_index + 1
  return free_index

def get_current_index(attr: str) -> int | None:
  """ For a given morphological analysis attribute,
  return its index as number or None if it is not
  a number.
  """
  index_str = attr.removeprefix('mrp')
  if index_str.isdigit():
    return int(index_str)
  else:
    return None

def get_selections(tag: Tag) -> list[str]:
  """ For a given XML tag of a word (w),
  get a list of selected morphological analyses
  """
  if 'mrp0sel' in tag.attrs:
    mrp0sel = tag.attrs['mrp0sel']
    assert isinstance(mrp0sel, str)
    return mrp0sel.split()
  else:
    return []

def unselect_split_away_options(current_index: int, morph: Morph, replacement: Morph, selections: list[str]) -> set[str]:
  """ Assuming the morph. analysis morph has been
  replaced with the analysis replacement, unselect
  those morph. tags of morph which are not present
  in replacement.

  :param current_index: The index of the original morph. analysis.
  :param morph: The original morph. analysis.
  :param replacement: The replacing morph. analysis.
  :param selections: A list of selected analysis indices
  which will be modified in-place.
  :return: The set of morph. tag letter-indices
  which were selected in morph and are not present
  in replacement.
  """
  selected_letters = set[str]()
  if isinstance(morph, MultiMorph) and isinstance(replacement, MultiMorph):
    removed_letters = set(morph.morph_tags) - set(replacement.morph_tags)
    for removed_letter in removed_letters:
      complete_index = str(current_index) + removed_letter
      if complete_index in selections:
        selected_letters.add(removed_letter)
        selections.remove(complete_index)
  return selected_letters

def select_added_analysis_options(free_index: int, morph: Morph, replacement: Morph, selections: list[str], selected_letters: set[str]) -> None:
  """ Assuming the morph. analysis morph has been
  replaced with the analysis replacement (possibly among others),
  select those morph. tags of replacement were selected in morph.

  :param free_index: The index of the added morph. analysis.
  :param morph: The original morph. analysis.
  :param replacement: The replacing morph. analysis.
  :param selections: A list of selected analysis indices
  which will be modified in-place.
  :param selected_letters: The letter-indices of the morph. tags
  which were selected in morph and removed therefrom.
  """
  if isinstance(morph, MultiMorph) and isinstance(replacement, MultiMorph):
    current_letters = set(replacement.morph_tags)
    for letter in sorted(current_letters & selected_letters):
      complete_index = str(free_index) + letter
      selections.append(complete_index)

def update_mrp0sel_attr(tag: Tag, selections: list[str]) -> None:
  """ For a given XML tag of a word (w),
  set its mrp0sel attribute to a value
  representing the given list of selections.
  """
  if selections != get_selections(tag):
    new_mrp0sel = ' '.join(selections)
    if len(new_mrp0sel) > 0:
      new_mrp0sel = ' ' + new_mrp0sel
    tag.attrs['mrp0sel'] = new_mrp0sel

def perform_replacement(tag: Tag, attr: str, morph: Morph, replacements: list[Morph], free_index: int, modified: bool, rel_name: str, lnr: str, value: str) -> tuple[int, bool]:
  """ For a given XML tag of a word (w),
  replace the morphological analysis morph
  occurring under the attribute attr
  with a list of morphological analyses replacements.

  :param free_index: An index which can be used for the addition of a new morph. analysis.
  :param modified: Whether the current document has been modified.
  :return: Updated value for the free index and modified.
  """
  current_index = get_current_index(attr)
  if current_index is None:
    return free_index, modified
  replacement = replacements[0]
  if isinstance(morph, MultiMorph):
      index = next(iter(morph.morph_tags))
      replacement = replacement.to_multi(index)
  selections = get_selections(tag)
  repl_with_merged_options = merge_identical_options_if_multi(
    str(current_index), replacement, selections
  )
  repl_str = repl_with_merged_options.__str__()
  tag[attr] = repl_str
  if not modified:
      logger.info(rel_name)
  modified = True
  logger.info('\t{0}'.format(lnr))
  logger.info('\t\t{0} =>'.format(value))
  logger.info('\t\t{0}'.format(repl_str))
  selected_letters = unselect_split_away_options(
    current_index, morph, replacement, selections
  )
  for replacement in replacements[1:]:
    repl_with_merged_options = merge_identical_options_if_multi(str(free_index), replacement, selections)
    attr = 'mrp' + str(free_index)
    repl_str = repl_with_merged_options.__str__()
    tag[attr] = repl_str
    logger.info('\t\t{0}'.format(repl_str))
    select_added_analysis_options(
      free_index, morph, replacement, selections, selected_letters
    )
    free_index += 1
  update_mrp0sel_attr(tag, selections)
  return free_index, modified

class SoupModifier:
    
    def __init__(self, replacements: dict[str, list[str]]):
        changes = dict[Morph, list[Morph]]()
        for key, values in replacements.items():
            origin = Morph.parse(key)
            targets = list[Morph]()
            for value in values:
              target = Morph.parse(value)
              if target is not None:
                targets.append(target)
            if origin is not None and len(targets) > 0:
              changes[origin] = targets
        self.changes = changes

    def __call__(self, soup: BeautifulSoup, rel_name: str) -> bool:
        lang = 'hit'
        modified = False
        lnr = '[unknown]'
        for tag in soup(['lb', 'w']):
            if tag.name == 'lb':
                if 'lnr' in tag.attrs and isinstance(tag['lnr'], str):
                  lnr = tag['lnr']
                else:
                  raise ValueError('The next line after {0} in {1} is not numbered'.format(lnr, rel_name))
                if 'lg' in tag.attrs and isinstance(tag['lg'], str):
                    lang = tag['lg']
                else:
                    logger.warning('Line {0} in {1} is not marked for language.'.format(lnr, rel_name))
                    lang = 'Hur'
            elif tag.name == 'w' and get_word_language(lang, tag) == 'Hur':
                if mrpNaN in tag.attrs:
                    del tag.attrs[mrpNaN]
                free_index = get_free_index(tag)
                for attr, value in list(tag.attrs.items()):
                    if attr.startswith('mrp') and attr != 'mrp0sel':
                        try:
                          if isinstance(value, str):
                            morph = Morph.parse(value)
                          else:
                            raise ValueError('The mrp attribute should have a single value.')
                        except ValueError:
                          raise ValueError(
                            'Incorrect morphological analysis:\n{0}\non line {1} in {2}'.format(value, lnr, rel_name)
                          )
                        if morph is None:
                          morph_logger.error('The following morphological analysis could not be parsed:\n%s on line %s in %s', value, lnr, rel_name)
                        elif morph in self.changes:
                            replacements = self.changes[morph]
                            free_index, modified = perform_replacement(
                              tag, attr, morph, replacements, free_index, modified,
                              rel_name, lnr, value
                            )
        return modified

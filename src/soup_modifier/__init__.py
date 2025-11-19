from bs4 import BeautifulSoup, Tag
from morph import Morph, MultiMorph
from typing import Callable

class SoupModifier:
    
    def __init__(self, replacements: dict[str, str]):
        changes = dict[Morph, Morph]()
        for key, value in replacements.items():
            origin = Morph.parse(key)
            target = Morph.parse(value)
            if origin is not None and target is not None:
              changes[origin] = target
        self.changes = changes

    def __call__(self, soup: BeautifulSoup, logging_function: Callable[[str], None], rel_name: str) -> bool:
        lang = 'hit'
        modified = False
        lnr = '[unknown]'
        for tag in soup(['lb', 'w']):
            if tag.name == 'lb':
                if 'lnr' in tag.attrs:
                  lnr = tag['lnr']
                else:
                  raise ValueError('The next line after {0} in {1} is not numbered'.format(lnr, rel_name))
                if 'lg' in tag.attrs:
                    lang = tag['lg']
                else:
                    logging_function('Line {0} in {1} is not marked for language.\n'.format(lnr, rel_name))
                    lang = 'Hur'
            elif tag.name == 'w' and lang == 'Hur':
                if 'lg' in tag.attrs and tag['lg'] != 'Hur':
                    continue
                if 'mrpnan' in tag.attrs:
                    del tag.attrs['mrpnan']
                for attr, value in tag.attrs.items():
                    if attr.startswith('mrp') and attr != 'mrp0sel':
                        try:
                          morph = Morph.parse(value)
                        except ValueError:
                          raise ValueError(
                            'Incorrect morphological analysis:\n{0}\non line {1} in {2}'.format(value, lnr, rel_name)
                          )
                        if morph in self.changes:
                            replacement = self.changes[morph]
                            if isinstance(morph, MultiMorph):
                                index = next(iter(morph.morph_tags))
                                replacement = replacement.to_multi(index)
                            repl_str = replacement.__str__()
                            tag[attr] = repl_str
                            if not modified:
                                logging_function(rel_name + '\n')
                            modified = True
                            logging_function(
                                '\t{0:10} {1:45} {2}\n'.format(lnr, value, repl_str)
                            )
        return modified

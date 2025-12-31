from bs4 import BeautifulSoup, Tag
from morph import Morph, MultiMorph
from typing import Callable
from logging import getLogger, INFO, FileHandler
logger = getLogger(__name__)
logger.setLevel(INFO)
handler = FileHandler('Log.txt', 'w', encoding='utf-8')
logger.addHandler(handler)
morph_logger = getLogger('morphological_analysis')
morph_logger.addHandler(FileHandler('{0}.log'.format(morph_logger.name), 'w', encoding='utf-8'))

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
            elif tag.name == 'w' and lang == 'Hur':
                if 'lg' in tag.attrs and tag['lg'] != 'Hur':
                    continue
                if 'mrpnan' in tag.attrs:
                    del tag.attrs['mrpnan']
                for attr, value in tag.attrs.items():
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
                            replacement = self.changes[morph][0]
                            if isinstance(morph, MultiMorph):
                                index = next(iter(morph.morph_tags))
                                replacement = replacement.to_multi(index)
                            repl_str = replacement.__str__()
                            tag[attr] = repl_str
                            if not modified:
                                logger.info(rel_name)
                            modified = True
                            logger.info(
                                '\t{0:10} {1:45} {2}'.format(lnr, value, repl_str)
                            )
        return modified

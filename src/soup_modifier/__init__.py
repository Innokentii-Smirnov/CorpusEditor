from bs4 import BeautifulSoup
from morph import Morph, parseMorph
from typing import Callable

class SoupModifier:
    
    def __init__(self, replacements: dict[str, str]):
        changes = dict[Morph, Morph]()
        for key, value in replacements.items():
            origin = parseMorph(key)
            target = parseMorph(value)
            changes[origin] = target
        self.changes = changes

    def __call__(self, soup: BeautifulSoup, logging_function: Callable[[str], None]) -> bool:
        lang = 'hit'
        publ = soup.find('ao:txtpubl').text
        modified = False
        for tag in soup(['lb', 'w']):
            if tag.name == 'lb':
                lnr = tag['lnr']
                if 'lg' in tag.attrs:
                    lang = tag['lg']
                else:
                    logging_function('Line {0} in {1} is not marked for language.\n'.format(lnr, publ))
                    lang = 'Hur'
            elif tag.name == 'w' and lang == 'Hur':
                if 'mrpnan' in tag.attrs:
                    del tag.attrs['mrpnan']
                for attr, value in tag.attrs.items():
                    if attr.startswith('mrp') and attr != 'mrp0sel':
                        morph = parseMorph(value)
                        if morph in self.changes:
                            replacement = self.changes[morph].__str__()
                            tag[attr] = replacement
                            if not modified:
                                logging_function(publ + '\n')
                            modified = True
                            logging_function(
                                '\t{0:10} {1:45} {2}\n'.format(lnr, value, replacement)
                            )
        return modified

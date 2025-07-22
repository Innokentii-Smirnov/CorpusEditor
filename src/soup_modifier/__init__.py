from bs4 import BeautifulSoup

def modify_soup(soup: BeautifulSoup, changes: dict[str, str]) -> None:
    lang = 'hit'
    for tag in soup(['lb', 'w']):
        if tag.name == 'lb':
            lang = tag['lg']
        elif tag.name == 'w':
            for attr, value in tag.attrs.items():
                if attr.startswith('mrp') and attr != 'mrp0sel':
                    if value in changes:
                        tag[attr] = changes[value]

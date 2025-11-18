from bs4.formatter import XMLFormatter
from bs4 import Tag
from collections.abc import Iterable

class CustomFormatter(XMLFormatter):

  def attributes(self, tag: Tag) -> Iterable[tuple[str, str]]:
    """Return the attributes in the original order.

    :param tag: An object representing an XML tag.
    :return: An unsorted iterable of key, value pairs repsesenting the XML tag's attributes.
    """
    for key, value in tag.attrs.items():
      yield key, value

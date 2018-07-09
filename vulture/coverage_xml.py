import posixpath
from xml.etree import ElementTree as ET

from vulture import utils


def parse_coverage_xml(xml):
    with open(xml) as f:
        return ET.fromstring(f.read().lower())


def detect_used_funcs(v, xml):
    tree = parse_coverage_xml(xml)
    for item in v.unused_funcs:
        filename = posixpath.join(*utils.format_path(
            item.filename).lower().split('\\'))
        xpath = ('./packages/package/classes/class/[@filename="{}"]'
                 '/lines/line[@hits="1"]'.format(filename))
        lines_hit = [int(
            node.attrib['number']) for node in tree.findall(xpath)]
        span = item.first_lineno+1, item.last_lineno+1
        for lineno in range(*span):
            if lineno in lines_hit:
                yield item


def used_funcs(v, xml):
    return set(item for item in detect_used_funcs(v, xml))

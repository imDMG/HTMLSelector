# VERSION: 0.1
# AUTHORS: imDMG [imdmgg@gmail.com]

# html selector for default python HTMLParser

import time
# import re
# import logging

from html.parser import HTMLParser

start_time = time.time()


class HTMLSelector(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.tag_data = []
        self.data = {}
        self.mark = False
        self.index = None
        self.name = None
        self.attrs = None
        self.container_tag = None
        self.container_group = False
        self.grouping = []
        self.index_count = 0
        self.count = 0

    def handle_starttag(self, tag, attrs):
        if self.tag_data:
            for item in self.tag_data:
                if tag == item['tag'] and self._filter(item['attrs'], attrs):
                    self.mark = True
                    self.attrs = attrs
                    if item['container']:
                        self.mark = False
                        self.attrs = None
                        self.container_tag = tag
                        return

                    if not self.container_tag and item['content']:
                        self.mark = False
                        self.attrs = None
                        return

                    if item['index']:
                        self.mark = False
                        if type(item['index']) is int:
                            if self.index_count == item['index']:
                                self.mark = True
                        else:
                            start, end = item['index'].split(":")
                            if self.index_count in range(int(start), int(end)):
                                self.mark = True

                    self.index_count += 1

    def handle_endtag(self, tag):
        if tag == self.container_tag:
            if self.container_group:
                self.data[self.name].append(self.grouping)
                self.index_count = 0
            self.container_tag = None

    def handle_data(self, data):
        if self.mark:
            # if container and content in container
            if not self.data.get(self.name):
                self.data[self.name] = []
            if self.container_group:
                self.grouping.append({"attrs": dict(self.attrs), "data": data})
            else:
                self.data[self.name].append({"attrs": dict(self.attrs), "data": data})
            self.mark = False
            self.attrs = None

    def error(self, message):
        pass

    def find(self, tag, storage_name, attrs=None, index=None, container=None):
        # selector.find(tag, attrs, index)
        # TODO do checking
        # container
        if not storage_name:
            container = tag

        self.tag_data.append({"tag": tag,
                              "storage_name": storage_name,
                              "attrs": attrs,
                              "index": index,
                              "container": container})
        return self

    def where(self, method, *args):
        getattr(self, method)(*args)
        pass

    def container(self, *args):
        pass

    def content(self, *args):
        pass

    def group(self, trigger=True):
        self.container_group = trigger
        return self

    def selector(self, cond: str, storage="latest"):
        container = False
        elems = cond.split(" ")
        for n, elem in enumerate(elems):
            tag = elem
            index = ""
            dictattrs = {}
            if "(" in elem:
                index = elem[elem.index("(") + 1:elem.index(")")]
                tag = elem[0:elem.index("(")]
            if "[" in elem:
                tag = elem[0:elem.index("[")]
                attrs = elem[elem.index("[") + 1:elem.index("]")].split(";")
                for attr in attrs:
                    name, value = attr.split("=")
                    if name == "class":
                        # or
                        if "|" in value:
                            value = tuple(value.split("|"))
                        # and
                        if "." in value:
                            value = value.split(".")
                    dictattrs.update({name: value})

            if len(elems) > 1 and n < len(elems)-1:
                container = True
            content = True if len(elems) > 1 and n == len(elems)-1 else False
            self.tag_data.append({"tag": tag,
                                  "attrs": dictattrs,
                                  "container": container,
                                  "content": content,
                                  "index": index})
            container = False
            # container = tag
        self.name = storage

        return self

    def _data_pass(self, tag, attrs):
        pass

    def _filter(self, what, where):
        """

        :type what: dict
        :param where:
        :return:
        """
        if not what:
            return True
        cond = []
        # find the attr and value match
        for name, value in dict(where).items():
            if name in what.keys():
                # attr class with multiple values
                if type(what[name]) == tuple:
                    cond.append(any([x in value for x in what[name]]))
                    continue
                if type(what[name]) == list:
                    cond.append(all([x in value for x in what[name]]))
                    continue
                cond.append(what[name] in value)
        return all(cond if len(cond) else [False])


if __name__ == "__main__":
    f = open("result.html", "r")
    parser = HTMLSelector()
    # None: we not store the data, just mark position
    # find(tr.bg  td.s|sl_s|slp)
    # parser.selector("tr[class=bg] td[class=s|sl_s|slp;id=me](3:5)")
    parser.selector("tr[class=bg] td(3:6)", "params").group()
    parser.selector("tr[class=bg] a[class=r0|r1]", "links").group()
    print(parser.tag_data)
    # line = "td[class=s|sl_s|slp;id=me](3:5)"
    # pair = re.findall(r"[\w]+=[\w|]+", line)
    # print(re.match(r"^.*(\w+)=([\w|]+)", line).groups())
    # parser.find('tr', None, {"class": "bg"}).\
    #     content('td', "td", {"class": "s"}).group("tr")
    # a.r0|r1
    # parser.find('img', "torrent_link", {"class": "block"})
    # print(parser.tag_data)
    parser.feed(f.read())
    print(parser.data)

    print("--- %s seconds ---" % (time.time() - start_time))

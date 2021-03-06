# VERSION: 0.3
# AUTHORS: imDMG [imdmgg@gmail.com]

# html selector for default python HTMLParser

import time
import re
# import logging

from html.parser import HTMLParser

start_time = time.time()


class HTMLSelector(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.pending = []
        self.data = {}
        self.mark = False
        self.index = None
        self.name = None
        self.attrs = None
        self.callback = None
        self.container_tag = None
        self.container_pair = None
        self.container_group = False
        self.grouping = []
        self.index_count = 0
        self.count = 0

    def handle_starttag(self, tag, attrs):
        if self.pending:
            for item in self.pending:
                if tag == item['tag'] and self._filter(item['attrs'], attrs):
                    if item['container']:
                        self.mark = False
                        self.attrs = None
                        self.container_tag = tag
                        self.container_pair = item["pair"]
                        return

                    if not self.container_tag and item['pair']:
                        self.mark = False
                        self.attrs = None
                        return

                    if self.container_tag and self.container_pair != item["pair"]:
                        self.mark = False
                        self.attrs = None
                        return

                    self.mark = True
                    self.attrs = attrs
                    self.name = item["name"]
                    self.callback = item["callback"]
                    self.container_group = item["group"]

                    if item['index']:
                        # TODO make checking for int
                        self.mark = False
                        if item['index'].find(":"):
                            start, end = item['index'].split(":")
                            if self.index_count in range(int(start), int(end) + 1):
                                self.mark = True
                        else:
                            if self.index_count == int(item['index']):
                                self.mark = True

                    self.index_count += 1

    def handle_endtag(self, tag):
        if tag == self.container_tag:
            if self.container_group:
                self.data[self.name].append(self.grouping)
                self.grouping = []
                self.index_count = 0
            self.container_tag = None
            self.container_pair = None

    def handle_data(self, data):
        if self.mark:
            if callable(self.callback):
                self.attrs, data = self.callback(self.attrs, data)
                self.callback = None
            # ---
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

    def find(self, *args):
        self._selector_re(*args)

        return self

    # def where(self, method, *args):
    #     getattr(self, method)(*args)
    #     pass
    #
    # def container(self, *args):
    #     pass
    #
    # def content(self, *args):
    #     pass
    #
    # def group(self, trigger=True):
    #     self.container_group = trigger
    #     return self

    def _selector(self, cond: str, storage="latest"):
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

            if len(elems) > 1 and n < len(elems) - 1:
                container = True
            content = True if len(elems) > 1 and n == len(elems) - 1 else False
            self.pending.append({"tag": tag,
                                 "attrs": dictattrs,
                                 "container": container,
                                 "content": content,
                                 "index": index})
            container = False
            # container = tag
        self.name = storage

        return self

    def _selector_re(self, expression: str, store_name="latest", group=False, callback=None):
        pair = None
        elems = expression.split(" ")
        for n, elem in enumerate(elems):
            # TODO make link with container and content
            tag = re.search(r'(\w+)[\[(]?', elem)[1]
            attrs = dict(re.findall(r'(\w+)=([\w|.]+)', elem))
            index = re.search(r'\(([\d:]+)\)', elem)

            if attrs.get("class"):
                # or
                if "|" in attrs["class"]:
                    attrs["class"] = tuple(attrs["class"].split("|"))
                # and
                elif "." in attrs["class"]:
                    attrs["class"] = attrs["class"].split(".")

            container = None
            if len(elems) > 1:
                container = False if n > 0 else True

            if n == 0:
                pair = elem
            # content = True if len(elems) > 1 and n == len(elems) - 1 else False
            self.pending.append({"tag": tag,
                                 "name": store_name,
                                 "attrs": attrs,
                                 "container": container,
                                 "pair": pair,
                                 "group": group,
                                 "index": index[1] if index else "",
                                 "callback": callback})

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
        # TODO rebuild loop up side down
        for name, value in dict(where).items():
            if name in what.keys():
                # TODO make direct match
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
    # parser.find("div[class=bx1_0] td[colspan=5]", "amount", None, lambda atr, dt: [atr, dt.split(" ")[1]])
    parser.find("tr[class=bg] a[class=r0|r1]", "torrents", True)
    parser.find("tr[class=bg] td(3:5)", "torrents", True)
    # parser._selector_re("select[class=w190]")
    # parser._selector("tr[class=bg] td(3:6)", "params").group()
    print(parser.pending)
    # line = "td[class=s|sl_s|slp;id=me](3:5)"
    # pair = re.findall(r"[\w]+=[\w|]+", line)
    # print(re.match(r"^.*(\w+)=([\w|]+)", line).groups())
    # parser.find('tr', None, {"class": "bg"}).\
    #     content('td', "td", {"class": "s"}).group("tr")
    # a.r0|r1
    # parser.find('img', "torrent_link", {"class": "block"})
    # print(parser.pending)
    parser.feed(f.read())
    print(parser.data)
    # print(len(parser.data["kaka"]))

    print("--- %s seconds ---" % (time.time() - start_time))

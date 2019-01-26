# HTMLSelector
HTML selector for default python HTMLParser

## Usage
    from htmlselector import HTMLSelector
    
    ..............
    
    parser = HTMLSelector()

    parser.find("div[class=header|container;title=title] a[class=name.width;href=example.com](10:25)", "storage_name", True, lambda atr, dt: [atr, dt])
    parser.find("...")
    parser.feed(HTML_DATA)
    parser.data["storage_name"]
    parser.close()

In that example we search tag `a` where classes `name` AND `width` AND `href=example.com` AND sort `10-25` items IN CONTAINER `div` where classes `header` OR `container` AND `title=title`.

2nd parameter it's name of dict where store your collected data (for one find() call). It can be merged.

3rd parameter (bool) means grouping by container.

4rd parameter - callback function.
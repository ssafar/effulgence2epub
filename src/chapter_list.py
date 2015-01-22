#!/usr/bin/python
"""The first stage of the downloader. Already assumes the local presence of the
TOC (edgeofyourseat.dreamwidth.org/2121.html), parses it and outputs two things:

- chapters.pbtxt (with the chapter data that could be extracted from the TOC)
- first_flat_list.txt (a list of all the linked chapters, specifically their
  first flattened chapters)
"""


from bs4 import BeautifulSoup
import effulgence_pb2 as eproto

import re
import urllib
import urlparse


# To download the first pages: wget -i first_flat_list.txt --no-clobber -w 5
# --force-directories

def chapters_from_toc(toc_soup):
    """Given the parsed HTML object of the TOC page, returns a Chapters proto, with
all the info that can be extracted from the TOC."""
    
    # This seems to cover the interesting ones quite well.
    all_the_links = toc_soup.select("ol li a")

    all_the_nonthread_links = [l for l in all_the_links
                               if "thread" not in l["href"]]
    # And now let's go exploring parents for chapter numbers etc.
    # (oops we can't because it's numbered automatically... then we just don't.)

    chapters = eproto.Chapters()

    for link in all_the_nonthread_links:
        chapter = chapters.chapter.add()
        chapter.title = link.text

        if (link.previous_sibling and 
            len(link.previous_sibling.strip()) > 0):

            chapter.symbols = link.previous_sibling.strip().encode(
                "ascii", "xmlcharrefreplace")

        chapter.main_threaded_url = link["href"]
        chapter.by_user = re.search(r'http://([a-z-]*)\.', 
                                    chapter.main_threaded_url).groups()[0]

        chapter.first_flat_page_url = set_param_in_url(
            chapter.main_threaded_url, "view", "flat")

    return chapters


def set_param_in_url(url, name, value):
    """Sets the query param with the given name in the URL, returns the rest
unchanged."""
    splitted = urlparse.urlsplit(url)
    params_dict = urlparse.parse_qs(splitted.query)
    params_dict[name] = [value]
    new_splitted = splitted._replace(
        query=urllib.urlencode(params_dict, doseq=True))
    return urlparse.urlunsplit(new_splitted)


if __name__ == "__main__":

    # This is the TOC. We extract all the could-be-relevant links from it.
    soup = BeautifulSoup(open(
        "web_cache/edgeofyourseat.dreamwidth.org/2121.html"))
    chapters = chapters_from_toc(soup)
    

    with open("global_lists/chapters.pbtxt", mode="w") as f:
        f.write(str(chapters))

    with open("global_lists/first_flat_list.txt", mode="w") as f:
        for c in chapters.chapter:
            f.write("%s\n" % c.first_flat_page_url)

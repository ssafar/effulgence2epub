from bs4 import BeautifulSoup
import effulgence_pb2 as eproto

import common

import re
import sys


def extract_num_pages(soup):
    """Looks at the "Page 1 out of N" part and infers how many pages are
left. Returns and int. If the page contains no such part, returns 1 by
default."""
    # This is the div containing the page selector.
    page_part = soup.find("div", class_="comment-page-list")
    if page_part:
        r = re.match(r'Page 1 of ([0-9]+)', page_part.p.text)
        num_pages = int(r.groups()[0])
    else: # If the div doesn't exist, it's only one page.
        num_pages = 1
    return num_pages


def extract_intro_part(soup):
    """Locates the chapter intro (the long part before the comments)."""
    page_part = soup.find("div", class_="entry-content")
    return page_part.decode_contents(formatter="html")


if __name__== "__main__":
    chapters = common.get_chapters_from_stdin()

    all_the_flat_chapters = []

    for chapter in chapters.chapter:
        the_file_name = chapter.first_flat_page_url.replace("http://", "web_cache/")

        # Infer the eventual full chapter file name. (Could be done in the first
        # stage, too.)
        html_numeric_id = re.search(r"([0-9]+).html", the_file_name).groups()[0]
        chapter.full_chapter_file_name = "%s_%s.pbtxt" % (chapter.by_user,
                                                          html_numeric_id)

        with open(the_file_name) as first_flat_file:
            print chapter.title
            soup = BeautifulSoup(first_flat_file)

            chapter.num_pages = extract_num_pages(soup)
            chapter.intro = extract_intro_part(soup)

            chapter.flat_url.append(chapter.first_flat_page_url)
            for chapter_id in range(2, chapter.num_pages + 1):
                chapter.flat_url.append(chapter.first_flat_page_url + 
                                        "&page=%d" % chapter_id)
        all_the_flat_chapters.extend(chapter.flat_url)


    with open("global_lists/chapters_with_intros.pbtxt", mode="w") as f:
        f.write(str(chapters))

    with open("global_lists/all_chapters_list.txt", mode="w") as f:
        f.write("\n".join(all_the_flat_chapters))

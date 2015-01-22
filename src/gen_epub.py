#!/usr/bin/python
from string import Template

import sys
import re
import os

sys.path.append("ebooklib")
from ebooklib import epub

from bs4 import BeautifulSoup

import common
# Chapters from stdin, as usual.

import effulgence_pb2 as eproto
import google.protobuf

# For the templates.
import pkg_resources

chapter_template = Template(
    pkg_resources.resource_string(__name__, "chapter_template.xhtml"))

comment_template = Template(
    pkg_resources.resource_string(__name__, "comment_template.xhtml"))

# toc_template = Template(
#     pkg_resources.resource_string(__name__, "toc_template.xhtml"))


style = pkg_resources.resource_string(__name__, "style.css")


def img_url_to_internal(url):
    r = re.match(r"http://www.dreamwidth.org/userpic/([0-9]*)/([0-9]*)", url)
    return "img_%s_%s.jpg" % r.groups()

def chapter_to_internal_name(chapter):
    """Returns an epub-internal chapter name."""
    return chapter.full_chapter_file_name.replace("pbtxt", "xhtml")

def map_external_imgs(book, chapter, the_map):
    for thread in chapter.thread:
        for comment in thread.comment:
            img_file_name = comment.icon_url.replace("http://", "web_cache/")
            if img_file_name not in the_map:
                internal_url = img_url_to_internal(comment.icon_url)
                img = epub.EpubItem(uid=internal_url, file_name=internal_url)
                with open(img_file_name) as f:
                    img.content = f.read()
                book.add_item(img)
                the_map[img_file_name] = True # Should have been a set :P
                

def generate_comment_html(comment):
    internal_icon_url = img_url_to_internal(comment.icon_url)
    if not internal_icon_url:
        raise "Woops, we didn't map %s" % comment.icon_url
    comment_id = "cmt%d" % comment.cmt_id
    comment_html = comment_template.substitute(img_src=internal_icon_url,
                                               by_user=comment.by_user,
                                               date=comment.timestamp,
                                               text=comment.text,
                                               comment_id=comment_id)
    return comment_html


def generate_chapter_html(chapter):

    chapter_comments = [generate_comment_html(comment)
                        for thread in chapter.thread
                        for comment in thread.comment]

    chapter_html = chapter_template.substitute(intro_text=chapter.intro,
                                               title=chapter.title,
                                               by_user=chapter.by_user,
                                               title_header=chapter.title,
                                               comments="".join(chapter_comments))
    return chapter_html

# def generate_toc_html(chapters):
#     entry_template = Template(
#         '<li> ${symbols} <a href="${url}"> ${title} </a> </li>\n')
    
#     toc_entries = [entry_template.substitute(symbols=chapter.symbols,
#                                              url=chapter_to_internal_name(chapter),
#                                              title=chapter.title)
#                    for chapter in chapters.chapter]

#     toc_html = toc_template.substitute(toc_entries=("".join(toc_entries)))
#     return toc_html

if __name__ == "__main__":
    chapters = common.get_chapters_from_stdin()
    # chapters = common.get_some_chapters()

    book = epub.EpubBook()
    book.set_identifier("effulgence_mirror")
    book.set_title("Effulgence")
    book.set_language("en")
    book.add_author("Alicorn")
    book.add_author("Kappa")

    all_chapters = []

    img_urls_to_epub_map = {}

    css = epub.EpubItem(uid="style", file_name="style.css", media_type="text/css",
                        content=style)
    book.add_item(css)

    # Add Table of Contents.
    toc_epub = epub.EpubHtml(title="Table of Contents",
                             file_name="nav.xhtml")
    # toc_epub.set_content(generate_toc_html(chapters))
    with open("global_lists/toc.xhtml") as f:
        toc_epub.set_content(f.read())

    toc_epub.add_item(css)
    book.add_item(toc_epub)
    book.spine = [toc_epub]
    # book.toc = toc_epub

    for introonly_chapter in chapters.chapter:

        # Reload the actual, full thing.
        chapter = eproto.Chapter()

        try:
            with open(os.path.join("chapters_pbtxt", 
                                   introonly_chapter.full_chapter_file_name)) as f:
                google.protobuf.text_format.Merge(f.read(), chapter)

        except:
            print "Error processing chapter: %s" % introonly_chapter.title
            continue

        # This will put the relevant images into the epub, if they are not yet
        # already there. (The map is to keep track of whether they are there or
        # not.)
        map_external_imgs(book, chapter, img_urls_to_epub_map)

        chapter_html = generate_chapter_html(chapter)

        chapter_epub = epub.EpubHtml(title=chapter.title,
                                     file_name=chapter_to_internal_name(chapter))
        chapter_epub.set_content(chapter_html)
        chapter_epub.add_item(css)
        book.add_item(chapter_epub)
        book.spine.append(chapter_epub)

        all_chapters.append(chapter_epub)

    book.add_item(epub.EpubNcx())
    # book.add_item(epub.EpubNav())

    epub.write_epub("effulgence.epub", book, {})

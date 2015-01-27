#!/usr/bin/python
# from string import Template
import pyratemp

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

chapter_template = pyratemp.Template(
    string=pkg_resources.resource_string(__name__, "chapter_template.xhtml"))

style = pkg_resources.resource_string(__name__, "style.css")


def map_external_imgs(book, chapter, the_map):
    for thread in chapter.thread:
        for comment in thread.comment:
            if not comment.HasField("icon_url"):
                continue
            img_file_name = comment.icon_url.replace("http://", "web_cache/")
            if img_file_name not in the_map:
                internal_url = common.img_url_to_internal(comment.icon_url)
                img = epub.EpubItem(uid=internal_url, file_name=internal_url)
                with open(img_file_name) as f:
                    img.content = f.read()
                book.add_item(img)
                the_map[img_file_name] = True # Should have been a set :P
                

if __name__ == "__main__":
    chapters = common.get_chapters_from_stdin()
    # chapters = common.get_some_chapters()

    book = epub.EpubBook()
    book.set_identifier("effulgence_mirror")
    book.set_title("Effulgence")
    book.set_language("en")
    
    # Each author needs a UID, or ebooklib gives them the same one.
    book.add_author("Alicorn", uid="belltower")
    book.add_author("Kappa", uid="binary-heat")

    all_chapters = []

    img_urls_to_epub_map = {}

    css = epub.EpubItem(uid="style", file_name="style.css", media_type="text/css",
                        content=style)
    book.add_item(css)

    # Add Table of Contents.
    toc_epub = epub.EpubHtml(title="Table of Contents",
                             file_name="nav.xhtml")

    with open("global_lists/toc.xhtml") as f:
        toc_epub.set_content(f.read())

    toc_epub.add_item(css)
    book.add_item(toc_epub)
    book.spine = [toc_epub]

    for introonly_chapter in chapters.chapter:

        # Reload the actual, full thing.
        chapter = common.full_chapter_from_introonly(introonly_chapter)

        # This will put the relevant images into the epub, if they are not yet
        # already there. (The map is to keep track of whether they are there or
        # not.)
        map_external_imgs(book, chapter, img_urls_to_epub_map)

        # This does the entire template substitution.
        chapter_html = chapter_template(chapter=chapter)

        chapter_epub = epub.EpubHtml(title=chapter.title,
                                     file_name=common.chapter_to_internal_name(chapter))
        chapter_epub.set_content(chapter_html)
        chapter_epub.add_item(css)
        book.add_item(chapter_epub)
        book.spine.append(chapter_epub)

        all_chapters.append(chapter_epub)

    book.add_item(epub.EpubNcx())
    # book.add_item(epub.EpubNav())

    epub.write_epub("effulgence.epub", book, {})

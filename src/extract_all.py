#!/usr/bin/python

# This is the last stage of the extractor thingy. It gets all the info from the
# html and creates nice per-chapter protobuf files. It can also be run in
# parallel, hopefully.

from bs4 import BeautifulSoup
import effulgence_pb2 as eproto

import re
import sys
import os

import common

def process_chapter(chapter):
    flat_files = [s.replace("http://", "web_cache/") for s in chapter.flat_url]

    parent_threads = {} # Comment ID to LinearCommentThread ref, for all the
                        # comments seen so far.

    for flat_file in flat_files:
        with open(flat_file) as f:
            print flat_file
            soup = BeautifulSoup(f)
            
            extract_comment_soup(soup, chapter, parent_threads)

            
def extract_comment(c_div):
    """Given a comment div element obj, returns a Comment proto, with the values
filled in."""
    c = eproto.Comment()
    c.by_user = c_div.find(True, class_="poster").find("b").text
    c.moiety = user_to_moiety_dict.get(c.by_user, "")

    img_tag = c_div.find("div", class_="userpic").find("img")

    # Apparently, not all comments have images.
    if img_tag:
        c.icon_url = img_tag["src"]
        c.icon_text = img_tag["alt"]
        c.icon_image_name = common.img_url_to_internal(c.icon_url)

    c.timestamp = c_div.find("span", class_="datetime").text.strip()
    c.cmt_id = int(re.match(r"comment-cmt([0-9]+)", c_div["id"]).groups()[0])
    c.text = c_div.find("div", class_="comment-content").decode_contents(formatter="html")
    return c

def extract_comment_soup(soup, chapter, parent_threads):
    # Look at all the comments.
    all_comments = soup.find_all("div", class_="comment")
    for c_div in all_comments:
        comment = extract_comment(c_div)

        # Find relevant thread; if the comment doesn't have parents, create a
        # new one.
        parent_link_li = c_div.find(True, class_="commentparent")
        if parent_link_li:
            parent_link_href = parent_link_li.find("a")["href"]
            # This is something like
            # http://self-composed.dreamwidth.org/10014.html?thread=2066206&style=site#cmt2066206
            parent_id = int(re.search(r"cmt([0-9]+)$", parent_link_href).groups()[0])
            if parent_id in parent_threads:
                our_linear_comment_thread = parent_threads[parent_id]
            else:
                raise "Reference to unknown parent %d" % parent_id
        else:
            our_linear_comment_thread = chapter.thread.add()

        parent_threads[comment.cmt_id] = our_linear_comment_thread            
        our_linear_comment_thread.comment.extend([comment])


chapters = common.get_chapters_from_stdin()

# Mapping usernames to authors.
user_to_moiety_dict = common.load_profile_data()

for chapter in chapters.chapter:
    process_chapter(chapter)
    with open(os.path.join("chapters_pbtxt", 
                           chapter.full_chapter_file_name), mode="w") as f:
        f.write(str(chapter))

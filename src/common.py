import sys

import effulgence_pb2 as eproto

import google.protobuf
import re

def get_chapters_from_stdin():
    chapters = eproto.Chapters()
    google.protobuf.text_format.Merge(sys.stdin.read(), chapters)
    return chapters


# def get_some_chapters():
#     chapters = eproto.Chapters()
#     with open("global_lists/test_chapters_w_intros.pbtxt") as f:
#         google.protobuf.text_format.Merge(f.read(), chapters)
#     return chapters

def parse_dreamwidth_url(url):
    """Returns a dict with keys by_user, html_numeric_id, and optionally comment_id
(latter as an integer). Latter is useful for links into multithreaded chapters."""
    by_user = re.search(r"http://([a-z-]*)\.", url).groups()[0]
    html_numeric_id = re.search(r"([0-9]+).html", url).groups()[0]
    
    result = {
        "by_user": by_user,
        "html_numeric_id": html_numeric_id
    }
    
    thread_result = re.search(r"#cmt([0-9]*)", url)
    if thread_result:
        result["comment_id"] = int(thread_result.groups()[0])

    return result
    
    

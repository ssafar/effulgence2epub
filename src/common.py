import sys

import effulgence_pb2 as eproto

import google.protobuf
import re
import os

def get_chapters_from_stdin():
    chapters = eproto.Chapters()
    google.protobuf.text_format.Merge(sys.stdin.read(), chapters)
    return chapters

        
def load_profile_data():
    profiles = eproto.Profiles()
    with open("global_lists/profiles.pbtxt") as f:
        google.protobuf.text_format.Merge(f.read(), profiles)
    user_to_moiety_dict = {}
    for profile in profiles.profile:
        for user in profile.user:
            user_to_moiety_dict[user] = profile.name
    return user_to_moiety_dict


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
    
    
def full_chapter_from_introonly(introonly_chapter):
    """Given a chapter proto (without the comments), we load the full chapter."""
    chapter = eproto.Chapter()


    with open(os.path.join("chapters_pbtxt", 
                           introonly_chapter.full_chapter_file_name)) as f:
        google.protobuf.text_format.Merge(f.read(), chapter)

    return chapter


def chapter_to_internal_name(chapter):
    """Returns an epub-internal chapter name."""
    return chapter.full_chapter_file_name.replace("pbtxt", "xhtml")


def img_url_to_internal(url):
    """Will generate comment.icon_image_name."""
    r = re.match(r"http://www.dreamwidth.org/userpic/([0-9]*)/([0-9]*)", url)
    return "img_%s_%s.jpg" % r.groups()

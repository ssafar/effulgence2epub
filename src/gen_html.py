#!/usr/bin/python

"""As usual, we eat chapters from stdin and output xhtml files, this time with
nice CSS and no tables. We don't copy the images to the relevant places since
that's not really amenable to parallelization (which is too much fun)."""

import os
import pkg_resources
import pyratemp

import common


chapter_template = pyratemp.Template(
    string=pkg_resources.resource_string(__name__, "html_chapter_template.xhtml"))

if __name__ == "__main__":
    chapters = common.get_chapters_from_stdin()
    
    if not os.path.isdir("html_mirror"):
        os.mkdir("html_mirror")
    
    for introonly_chapter in chapters.chapter:
        chapter = common.full_chapter_from_introonly(introonly_chapter)
        
        chapter_html = chapter_template(chapter=chapter)
        
        output_file_name = os.path.join("html_mirror",
                                        common.chapter_to_internal_name(chapter))

        with open(output_file_name, mode="w") as xhtml_file:
            xhtml_file.write(chapter_html.encode('utf-8'))

        


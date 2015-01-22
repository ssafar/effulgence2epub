#!/bin/bash

# This is the main launcher thing that starts different stages of the
# downloader. Takes one parameter: the stage name. Look for the things below.

# Wait this much between dreamwidth.org downloads (in seconds). Longer is nicer.
WAIT_TIME=10

# Go to the dir where the script is. Useful to find all the other stuff.
cd `dirname $0`


case $1 in
    "") cat <<EOF
Please choose between the following operations: toc_download, toc_parse,
firstflat_download, firstflat_parse, all_flat_download, images_get, gen_ebook.

(Typically, this is a reasonable ordering for downloading everything.)
EOF
        exit;
        ;;

    toc_download)
        (cd web_cache; \
            wget --force-directories \
            http://edgeofyourseat.dreamwidth.org/2121.html)
        ;;

    toc_parse)
        python src/chapter_list.py
        ;;

    toc_xhtmlize)
        # Generate an xhtml from the TOC, directly. We swap out all the URL-s
        # for ebook versions. Writes the result to global_lists/toc.xhtml.
        python src/new_toc.py
        ;;
    
    firstflat_download)
        (cd web_cache; \
            wget -i ../global_lists/first_flat_list.txt --no-clobber -w $WAIT_TIME \
            --force-directories)
        ;;

    firstflat_parse)
        # Here we use GNU Parallel to launch the processing nicely. We could
        # pipe the entire thing to the parser instead but it wouldn't be as fast
        # / cool.
        #
        # The thing it does: it splits the input along chapters (record start is
        # at 'chapter {'), and applies extract_all.py on all the chapters
        # independently.
        cat global_lists/chapters_with_intros.pbtxt | \
            parallel -N1 --pipe --recstart 'chapter {' python src/extract_all.py 
        # We need -N1, otherwise the split wouldn't be potentially happening at
        # every line.
        ;;

    all_flat_download)
        (cd web_cache; \
            wget -i ../global_lists/all_the_image_urls.txt --no-clobber \
            -w $WAIT_TIME --force-directories)
        ;;

    images_get)
        # Extract all the icon URLs from the chapters. We get the relevant
        # lines, throw away everything but the URL, and download everything
        # unique in the list.
        cat chapters_pbtxt/*.pbtxt | grep icon_url | \
            cut -d\" -f 2 | sort -u \
            >global_lists/all_the_image_urls.txt

        (cd web_cache; \
            wget -i ../global_lists/all_the_image_urls.txt \
            --no-clobber -w $WAIT_TIME --force-directories)
        ;;

    gen_ebook)
        cat global_lists/chapters_with_intros.pbtxt | python src/gen_epub.py
        ;;

    gen_ebook_test)
        # Do the thing with a smaller list of chapters. It's faster. By the way,
        # this is an ugly hardcoded length but it's likely to stay the
        # same. (It's the first two chapters.)
        cat global_lists/chapters_with_intros.pbtxt | head -n 22 | python src/gen_epub.py
        ;;

    *) echo "Unknown stage; sorry."
esac

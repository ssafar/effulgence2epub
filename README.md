About Effulgence2Epub
=====================

[Effulgence](http://edgeofyourseat.dreamwidth.org/2121.html) is... well, it's complicated. You might want to read [Luminosity](http://luminous.elcenia.com/) by Alicorn first. It's awesome.

Anyway. This is a Thing that downloads it from dreamwidth.org (all of it!), and generates a nice ebook out of it. It's not the only Thing with the first property (I'm thinking of [effulgence-mirror](https://github.com/liammdalton/effulgence-mirror)), but most likely the only one (so far) with the second. It generates .epub files, which can then easily be converted to e.g. Kindle formats. (More on the exact meaning of "easily" coming up later.)

Since the actual ebooks are up already ([epub](http://luminous.elcenia.com/effulgence/effulgence.epub) and [mobi](http://luminous.elcenia.com/effulgence/effulgence.mobi)), if you'd only like to read Effulgence itself, just downloading those is your best bet. If you're interested in how to create ebooks or download lots of pages or something similar, read on.

Requirements
============
The code has been observed to work on a specific instance of Ubuntu 14.04. It uses:

  - [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/), to parse the html. It's really easy to use; also, the author has written a nice sci-fi book about alien video games, how cool is that? (apt-get install python-beautifulsoup)
  - [Google Protocol Buffers](https://code.google.com/p/protobuf/) to store the parsed data from the chapters. This also means that if you'd like to convert Effulgence into some other format, this project might have solved the "input" part for you. (apt-get install protobuf-compiler)
  - [EbookLib](https://github.com/aerkalov/ebooklib) to generate the EPUB file. (no Ubuntu package here; just clone their repo into the root of this one. Ping me if you have better ideas :))
  - [GNU Parallel](http://www.gnu.org/software/parallel/), to process chapters faster on multicore machines. It feels like xargs but it's more flexible and has parallelization awesomeness. Highly recommended for e.g. batch resizing images, too. (apt-get install parallel)
  - [pyratemp](http://www.simple-is-better.org/template/pyratemp.html), for templating. So that we can have for loops in html pages.


How it works
============

To minimize the load on dreamwidth.org, we're caching all the things we can
locally. Problem #1: in the beginning, we have a single link, to the TOC. Thus, we are alternating between a) parsing files that we already have
and b) downloading even more files.

This is reflected in the several distinct stages you can launch by running runner.sh <stage_name>:

  - we download the TOC. It's a single HTML file. (toc_download)
  - we parse it. It produces a preliminary chapter list along with a list of the URLs for the first pages of the chapters. We still don't know how many pages they have in total. (toc_parse)
  - we use wget to download the first pages of the chapters. We only get the files that don't exist locally, so relaunching this process continues where it left off. (firstflat_download)
  - we parse all of these. This produces an extended chapter list, complete with intros and all the flat chapter URLs. (firstflat_parse)
  - this time, we download everything. (all\_flat\_download)
  - and parse those too. (all\_flat\_parse)
  - also, the images. (images_get)
  - we convert the TOC to its ebook variant (toc_xhtmlize)
  - and finally, we create the epub file itself (gen_ebook).

You can use it...
==================

  - as an example of how to use Protocol Buffers to store complicated data (see effulgence.proto)
  - ... of how to generate ebooks (the code isn't as neat, but still)
  - ... of how to extract lots of data out of html pages
  - to get Effulgence chapters as a list of comments, as protocol buffer files (that you can use from Python, Java, C++, etc.)

About Kindle conversion
========================

This code generates EPUB files. These are easy to convert to .mobi ones, for Kindles. Theoretically. In practice, reading Effulgence is a Big Data problem, thus you'll need

  - either Calibre, a bit more than 4 gigs of free RAM, and lots of free time, or
  - the official KindleGen tool from Amazon, which seems to perform better at this task.


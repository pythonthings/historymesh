#!/usr/bin/env python

import re
import sys
import time
from lxml import etree

title_regex = re.compile(r"\<title\>([^\<]+)\</title\>")
link_regex = re.compile(r"\[\[([^\[\]\n]+)\]\]")
start_pattern = '<text xml:space="preserve">'
end_pattern = '</text>'
number_of_articles = 10500000.0


def main(filename, output_filename):

    start_time = time.time()

    with open(output_filename, "w") as fh:
        for i, (title, start, length, text) in enumerate(parse(filename)):
            # Do a time estimate
            if i % 1000 == 1:
                time_per_page = (time.time() - start_time) / i
                sys.stderr.write("%6.2f%% - %6.2fh - %s\n" % (
                    (i / number_of_articles) * 100,
                    (time_per_page * (number_of_articles - i)) / 3600.0,
                    title,
                ))
                sys.stderr.flush()
            # Output the line
            fh.write("%s\t%i\t%i\t%s\t%s\n" % (
                title,
                start,
                length,
                "true" if is_redirect(text) else "false",
                "|".join(set(extract_links(text))),
            ))
        sys.stderr.write("\nDone in %6.2fh\n" % (time.time() - start_time))


def parse(filename):
    with open(filename, "rb") as fh:
        offset = 0
        current_title = None
        text_start = None
        text = ""
        for line in fh:
            already_added_text = False

            # See if it is a title
            title_match = title_regex.search(line)
            if title_match:
                current_title = title_match.group(1)
                text_start = None
                text = ""

            # See if it is some text
            try:
                index_of_text_start = line.index(start_pattern)
            except ValueError:
                pass
            else:
                text_start = offset + index_of_text_start + len(start_pattern)
                text += line[text_start - offset:]
                already_added_text = True
            
            # See if it's the end of some text
            try:
                index_of_text_end = line.index(end_pattern)
            except ValueError:
                pass
            else:
                text_end = offset + index_of_text_end
                text += line[:index_of_text_end]
                yield current_title, text_start, text_end - text_start, text
                text_start = None
                already_added_text = True
            
            # See if we're in the middle of a text block
            if text_start and not already_added_text:
                text += line
            
            # Increment offset
            offset += len(line)

def extract_links(text):
    # Find all potential matches
    for match in link_regex.finditer(text):
        link_text = match.group(1)
        # Discard anything with a colon that isn't "Category:"
        if ":" in link_text and not link_text.startswith("Category:"):
            continue
        # Find any pipes and cut at them
        try:
            pipe_index = link_text.index("|")
        except ValueError:
            pass
        else:
            link_text = link_text[:pipe_index]
        # Find any hashes and cut at them
        try:
            hash_index = link_text.index("#")
        except ValueError:
            pass
        else:
            link_text = link_text[:hash_index]
        # Yield the valid link
        yield link_text

def is_redirect(text):
    return text.startswith("#REDIRECT")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

from bs4 import BeautifulSoup
import effulgence_pb2 as eproto

"""Eat a list of profile pages to eat from stdin. Parse them and write all the
results to global_lists/profiles.pbtxt (as a Profiles proto)."""

import sys

if __name__ == "__main__":
    profiles = eproto.Profiles()

    for url in sys.stdin.readlines():
        if "profile" not in url:
            raise "Oops, %s doesn't look like a profile page" % url
        
        profile = profiles.profile.add()
        
        soup = BeautifulSoup(open(url.replace("http://", "web_cache/").strip()))

        profile.name = soup.find(True, class_="username").text.strip()
        

        relevant_links_div = soup.find("div", id="members_people_body") #select(".members_people_body")
        users = [l.text for l in relevant_links_div.find_all("a")]
        for u in users:
            profile.user.append(u)
    print str(profiles)

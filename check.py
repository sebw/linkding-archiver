import asyncio
import os
import json
from aiolinkding import async_get_client
import subprocess
import apprise
import sys
from datetime import datetime
from urllib.parse import urlparse
import re

archive_url = os.environ.get('ARCHIVE_URL')
linkding_url = os.environ.get('LINKDING_URL')
linkding_token = os.environ.get('LINKDING_TOKEN')
linkding_tag = os.environ.get('LINKDING_TAG')
pushover_user = os.environ.get('PUSHOVER_USER')
pushover_token = os.environ.get('PUSHOVER_TOKEN')
tube_url = os.environ.get('TUBE_URL')
tube_token = os.environ.get('TUBE_TOKEN')

async def archive() -> None:
    client = await async_get_client(linkding_url, linkding_token)
    bookmark = await client.bookmarks.async_get_all(query="#" + linkding_tag)

    now = datetime.now()
    archive_date_readable = now.strftime("%Y-%m-%d %H:%M:%S")

    print(archive_date_readable + " Found " + str(bookmark['count']) + " bookmark(s) to archive...")
    result = bookmark['results']

    for link in result:
        link_id = link['id']
        link_url = link['url']
        link_notes = link['notes']
        link_title = link['title']
        link_tags = link['tag_names']

        now = datetime.now()
        archive_date = now.strftime("%Y%m%d_%H%M%S")
        archive_date_readable = now.strftime("%Y-%m-%d %H:%M:%S")

        def extract_domain(url):
            parsed_url = urlparse(url)
            domain = parsed_url.netloc
            return domain

        def contains_youtube_link(input_string):
            lower_input = input_string.lower()
            if "youtu.be" in lower_input or "youtube.com" in lower_input:
                print("Youtube link detected!")
                return True
            else:
                print("Youtube link not detected...")
                return False

        link_domain = extract_domain(link_url)

        # if URL is a youtube link and we have a Tube Archivist instance
        if contains_youtube_link(link_domain) and tube_url: 

            def extract_video_id(youtube_url):
                pattern = re.compile(r'(?:https?://)?(?:www\.)?(?:youtube\.com/.*(?:\?v=|/embed/|/v/|/watch\?v=|/videos/|/channel/|/user/|/c/)|youtu\.be/)([^"&?/\s]{11})')
                match = pattern.search(youtube_url)
                if match:
                    video_id = match.group(1)
                    return video_id
                else:
                    return None

            # extract video ID from full URL
            video_id = extract_video_id(link_url)
            
            import http.client
            conn = http.client.HTTPSConnection(tube_url)

            headers = {
                'Content-Type': "application/json",
                'Authorization': "Token " + tube_token + ""
                }

            # Put video in queue
            payload = "{\n \"data\": [\n {\"youtube_id\": \"" + video_id + "\", \"status\": \"pending\"}\n ]\n}"
            conn.request("POST", "/api/download/", payload, headers)

            res = conn.getresponse()
            data = res.read()
            data.decode("utf-8")

            import time
            time.sleep(3)

            # Download now..
            payload3 = "{ \"status\": \"priority\" }"
            conn3 = http.client.HTTPSConnection(tube_url)
            conn3.request("POST", "/api/download/" + video_id + "/", payload3, headers)
            res3 = conn3.getresponse()
            data3 = res3.read()
            data3.decode("utf-8")

            now = datetime.now()
            archive_date_readable = now.strftime("%Y-%m-%d %H:%M:%S")

            archive_url = "https://" + tube_url + "/video/" + video_id

            # Logging
            print(archive_date_readable + " [Bookmark ID " + str(link_id) + "] Archived video " + link_url + " at " + archive_url)

            # Update the bookmark:
            link_tags.remove(linkding_tag)
            link_tags.append("linkding-archiver") 
            updated_bookmark = await client.bookmarks.async_update(
                link_id,
                tag_names=link_tags,
                notes="[Video archived on " + archive_date_readable + "](" + archive_url + ")\n" + link_notes
            )

        # Process non Youtube links (or Youtube links if we don't have a Tube Archivist instance) with SingleFile
        else:

            output_file = "linkding_" + str(link_id) + "_" + archive_date + ".html"

            # Logging
            print(archive_date_readable + " [Bookmark ID " + str(link_id) + "] Processing " + link_url)

            try:
                process = subprocess.run(['/usr/local/bin/single-file','--browser-executable-path','/usr/bin/chromium-browser','--output-directory','/archives/','--filename-template',output_file,'--browser-args','["--no-sandbox"]', link_url], stdout=subprocess.PIPE, universal_newlines=True)

                if pushover_user:
                    apobj = apprise.Apprise()
                    apobj.add('pover://' + pushover_user + '@' + pushover_token)

                    apobj.notify(
                        body='URL ' + link_url + ' has been processed',
                        title='Linkding Archiver',
                    )
            except:
                sys.exit("Something failed when trying to process the link")

            now = datetime.now()
            archive_date_readable = now.strftime("%Y-%m-%d %H:%M:%S")

            # Logging
            print(archive_date_readable + " [Bookmark ID " + str(link_id) + "] Archived " + link_url + " at " + archive_url + "/" + output_file)

            # Update the bookmark:
            link_tags.remove(linkding_tag)
            link_tags.append("linkding-archiver") 
            updated_bookmark = await client.bookmarks.async_update(
                link_id,
                tag_names=link_tags,
                notes="[Archived on " + archive_date_readable + "](" + archive_url + "/" + output_file + ")\n" + link_notes
            )

asyncio.run(archive())

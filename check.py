import asyncio
import os
import json
from aiolinkding import async_get_client
import subprocess
import apprise
import sys
from datetime import datetime

archive_url = os.environ.get('ARCHIVE_URL')
linkding_url = os.environ.get('LINKDING_URL')
linkding_token = os.environ.get('LINKDING_TOKEN')
linkding_tag = os.environ.get('LINKDING_TAG')
pushover_user = os.environ.get('PUSHOVER_USER')
pushover_token = os.environ.get('PUSHOVER_TOKEN')

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
        link_description = link['description']
        link_title = link['title']
        link_tags = link['tag_names']

        now = datetime.now()
        archive_date = now.strftime("%Y%m%d_%H%M%S")
        archive_date_readable = now.strftime("%Y-%m-%d %H:%M:%S")
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
            description="[Archived " + archive_url + "/" + output_file + "] " + link_description
        )

asyncio.run(archive())

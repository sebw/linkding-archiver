# Linkding Archiver

[Linkding](https://github.com/sissbruecker/linkding) is a bookmark aggregator with neat browser integrations.

[SingleFile](https://github.com/gildas-lormeau/SingleFile) provides an easy way to archive web pages in a single portable HTML file (embedding pictures!).

[Tube Archivist](https://github.com/tubearchivist/tubearchivist) allows you to archive, organize, search and self host your Youtube collections.

Linkding provides archiving possibilities with the wayback machine (archive.org).

But what if you wanted to host your own archive collections?

This container image allows this.

## How does it work?

- this container will query your Linkding instance every hour
- it searches your Linkding for links with a "trigger tag" that you define (e.g. `archivethisplz`, I personally chose the very  simple `a` tag, unlikely to conflict with other tags)
- if bookmarks are found with your trigger tag, we will check if it's a Youtube link or any other link
- if it's a Youtube link and if you have a Tube Archivist (TA) instance, we will archive the video in TA.
- if the bookmark is not a Youtube link (or it's a Youtube link but you don't have a TA instance), SingleFile will process the link and save the HTML file under `/archives` on the container filesystem (configure as a persistent volume!)
- when processed bookmarks are edited
  - link to the archive (TA or SingleFile HTML) is added to the notes
  - the trigger tag is removed
  - the tag `linkding-archiver` is added
- an (optional) notification is sent to Pushover (it uses the [apprise](https://github.com/caronc/apprise) library)

## How a bookmark looks before processing

![](https://raw.githubusercontent.com/sebw/linkding-archiver/master/screenshots/before.png)

## How it looks after processing

![](https://raw.githubusercontent.com/sebw/linkding-archiver/master/screenshots/after.png)

## Run the container

`LINKDING_TAG` is the trigger tag.

`LINKDING_TOKEN` is the REST API token that can be found in your Linkding under Settings > Intgegrations > REST API

`ARCHIVE_URL` is where you will expose your archives (e.g. `file:///home/user/archives/`, `https://archive.example.com` or `https://archive.example.com/subfolder`)

`PUSHOVER_USER` (optional) is your Pushover user token, if you want to get notified when a link is processed

`PUSHOVER_TOKEN` (optional) is your Pushover application token, if you want to get notified when a link is processed

`TUBE_URL` (optional) is your Tube Archivist instance

`TUBE_TOKEN` (optional) is the token to your Tube Archivist instance

```bash
docker run -d \
    --name=linkding-archiver \
    -e LINKDING_URL=https://linkding.example.org \
    -e LINKDING_TOKEN=abc \
    -e LINKDING_TAG=to_archive \
    -e ARCHIVE_URL=https://archive.example.org \
    -e PUSHOVER_USER=abc \
    -e PUSHOVER_TOKEN=xyz \
    -e TUBE_URL=tube.example.org \
    -e TUBE_TOKEN=abcd \
    -v /some/local/folder/archives:/archives \
    ghcr.io/sebw/linkding-archiver:0.6
```

## Exposing your SingleFile archives

If you want to expose your archives, you can use the `nginx` container image mounted to the same local folder:

```bash
docker run -d --restart unless-stopped --name linkding-archiver-site -p 80:80 -v /some/local/folder/archives:/usr/share/nginx/html:ro -d nginx
```

## Build the container yourself

```bash
git clone https://github.com/sebw/linkding-archiver
cd linkding-archiver
docker build . -t linkding-archiver:0.6
```

## Troubleshooting

### Checking the logs

```bash
docker exec -it linkding-archiver tail -f /var/log/archiver.log
```

### Execute manually

```bash
docker exec -it linkding-archiver sh
/usr/bin/python3 /opt/check.py
```

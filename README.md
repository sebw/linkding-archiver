# Linkding Archiver

[Linkding](https://github.com/sissbruecker/linkding) is a bookmark aggregator.

[SingleFile](https://github.com/gildas-lormeau/SingleFile) provides an easy way to archive web pages in a single HTML file (embedding pictures!).

Linkding integrates with the wayback machine (archive.org) but what if you wanted to host your own archive collection?

This container image allows this.

## How does it work?

- this container will query your Linkding instance every hour
- it searches your Linkding for links with a "trigger tag" that you define (e.g. `to_archive`)
- if bookmarks are found with that tag, SingleFile processes the links and saves the single HTML under `/archives` on the container filesystem (configure as a persistent volume!)
- when processed bookmarks are edited
  - link to the archive is added to the notes (e.g.: `file:///home/user/archives/1234_20200101_120000.html` or `https://archive.example.com/1234_20200101_120000.html`)
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

```bash
sudo docker run -d \
    --name=linkding-archiver \
    -e LINKDING_URL=https://linkding.example.org \
    -e LINKDING_TOKEN=abc \
    -e LINKDING_TAG=to_archive \
    -e ARCHIVE_URL=https://archive.example.org \
    -e PUSHOVER_USER=abc \
    -e PUSHOVER_TOKEN=xyz \
    -v /some/local/folder/archives:/archives \
    ghcr.io/sebw/linkding-archiver:0.5
```

## Exposing your archives

If you want to expose your archives, you can use the `nginx` container image mounted to the same local folder:

```bash
docker run -d --restart unless-stopped --name linkding-archiver-site -p 80:80 -v /some/local/folder/archives:/usr/share/nginx/html:ro -d nginx
```

## Build the container yourself

```bash
git clone https://github.com/sebw/linkding-archiver
cd linkding-archiver
docker build . -t linkding-archiver:0.1
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

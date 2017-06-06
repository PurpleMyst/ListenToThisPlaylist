#!/usr/bin/env python3
import concurrent.futures
import json
import os
import random
import subprocess
import tempfile
import threading
import urllib.parse

import praw
import youtube_dl

ALLOWED_NETLOCS = {"youtube.com", "youtu.be"}

FETCH_LOCK = threading.Lock()
PLAY_LOCK = threading.Lock()


class ErrorOnlyLogger:
    def debug(self, msg):
        pass

    warning = debug

    def error(self, msg):
        print(msg)


def fetch_urls(reddit, subreddits):
    subreddit = reddit.subreddit("+".join(subreddits))
    urls = []

    for post in subreddit.top("week"):
        netloc = urllib.parse.urlparse(post.url).netloc
        netloc = netloc.replace("www.", "", 1)

        if netloc in ALLOWED_NETLOCS:
            urls.append(post.url)

    return urls


def play_file(filepath):
    # TODO: Support multiple OSes.
    subprocess.run(["play", filepath],
                   stdout=subprocess.DEVNULL,
                   stdin=subprocess.DEVNULL,
                   stderr=subprocess.DEVNULL)


def fetch_url(ydl, url):
    before = set(os.listdir())
    ydl.extract_info(url, download=True)
    after = set(os.listdir())
    new = after - before
    if len(new) == 1:
        return new.pop()
    else:
        raise RuntimeError("Had more than one new file!")


def play_url(ydl, url):
    with FETCH_LOCK:
        print(f"Fetching {url!r}...")
        filepath = fetch_url(ydl, url)
        print(f"Done fetching {url!r}")

    with PLAY_LOCK:
        print(f"Playing {url!r}")
        play_file(filepath)


def main():
    with open("config.json") as config_file:
        config = json.load(config_file)

    with open("app.json") as app_info_file:
        app_info = json.load(app_info_file)

    print("Connecting to Reddit and fetching URLs...")
    reddit = praw.Reddit(**app_info)
    urls = fetch_urls(reddit, config["subreddits"])
    random.shuffle(urls)
    print("Done fetching")

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "logger": ErrorOnlyLogger(),
    }

    with tempfile.TemporaryDirectory() as tempdir:
        print("Working in", tempdir)
        os.chdir(tempdir)

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            pool = concurrent.futures.ThreadPoolExecutor()

            for url in urls:
                pool.submit(play_url, ydl, url)

            # Sadly, you have to KeyboardInterrupt twice :/
            pool.shutdown(wait=True)


if __name__ == "__main__":
    main()

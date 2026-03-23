# News Monitor Discord Bot

Personal Python automation project for monitoring web search results delivered as an RSS feed and sending notifications to Discord. Includes state tracking and cron scheduling.

## What the script does

This script:

- fetches an RSS feed containing web search results
- parses the feed and extracts new items
- keeps track of previously seen results in a local JSON file
- sends new matches to a Discord channel via webhook
- is intended to run automatically on a schedule using cron

## Features

- RSS-based monitoring of search results
- Discord webhook notifications
- state tracking to avoid duplicate posts
- simple file-based storage
- cron-friendly setup for automation

## Project structure

```text
.
├── main.py
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── cron-example.txt
└── data/
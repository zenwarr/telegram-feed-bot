This bot posts rss feeds to telegram channels.
It can also collect top posts from a subreddit and post them to a telegram channel hourly.

## Feed configuration

Configuration is stored in `data/config.yaml` file.
Example configuration:

```yaml
feeds:
- url: https://xkcd.com/rss.xml # RSS feed url 
  filter: xkcd # Filter to convert a feed entry to a telegram message (optional)
  channel: "@xkcd" # Handle of a telegram channel to post to. You can reuse same channel for multiple feeds.
  
reddit:
- name: funny # Name of a subreddit
  channel: "@funny" # Handle of a telegram channel to post to. You can reuse same channel for multiple subreddits.
```

Filters are functions in `/src/filters.py` file.
If you specify `something` in `filter` field, a function named `something_content_filter` in `filters.py` is going to be used.
`generic` filter is used by default.
It tries its best to extract content from a feed entry and convert it to simple markdown Telegram understands.

Application does not need to be restarted to pick up a new configuration.
Updated config is going to be used on next update.

## Bot configuration

You have to set bot token in `data/.env` file.
For example:

```dotenv
TELEGRAM_BOT_TOKEN=my_telegram_bot_token
```

## Running it

After setting up feeds in config and configuring bot token, you can start the bot with docker-compose.
For example:

```sh
docker-compose up --build
```

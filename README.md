This bot posts rss feeds to telegram channels.
It can also collect top posts from a subreddit and post them to a telegram channel hourly.

## Feed configuration

Configuration is stored in `data/config.yaml` file.
Example configuration:

```yaml
feeds:
- url: https://xkcd.com/rss.xml # RSS feed url

  # Handle of a telegram channel to post to.
  # You can reuse same channel for multiple feeds.
  channel: "@xkcd"

  # Optional, `generic` by default
  # Filter to convert a feed entry to a telegram message
  filter: xkcd

  # Optional, none by default
  # Regexp to not post messages not matching it.
  # Matching is done against an already generated telegram message, not source html provided in a feed entry.
  should_match: "^xkcd"

  # Optional, none by default
  # Regexp to not post messages matching it. It can be an array of patterns.
  # Matching is done against an already generated telegram message, not source html provided in a feed entry.
  should_not_match: "^xkcd"
  
  # Optional, none by default
  # Prefix is added to the message title and can be useful if you post multiple feeds to the same telegram channel
  # Title with a prefix looks like this: `[XKCD] Original entry title`
  title_prefix: "XKCD"
  
  # Optional, true by default
  # If set to false, disables link previews for telegram messages 
  link_preview: true
  
  # Optional, true by default
  # If set to true, text in the title is going to be a clickable link to an original post.
  # Setting this to true automatically disables footer.
  title_link: true
  
  # Optional, false by default
  # If true, telegram messages will have footer with clickable link to an original post
  footer: true

reddit:
- name: funny # Name of a subreddit
  channel: "@funny" # Handle of a telegram channel to post to. You can reuse same channel for multiple subreddits.
```

Filters are functions that convert incoming rss feed entry to telegram message.
`generic` filter is used by default.
It tries its best to extract content from a feed entry and convert it to simple markdown Telegram understands.

There are two types of filters: built-in and custom.
Built-in filters are located in `src/builtin_filters` directory — each file here exports a function named `content_filter` and the name of the file is a name of the filter.
If a filter with given name is not found in `src/builtin_filter`, application tries to find it in `src/custom_filters` directory.
You can use it to create your custom filters (take a look at a filter in `src/builtin_filter` for example).

If you are using default `docker-compose.yml` config for deploy, you do not need to modify code in the repository.
`filters` directory is mounted into `src/custom_filters`, so you can just place your custom filters there.

Application does not need to be restarted to pick up a new configuration.
Updated config is going to be used on next update.

### Reusing config

You can reuse configuration for multiple feeds with YAML links:

```yaml
configs:
  feed: &feed
    channel: "-129837198239123"
    link_preview: no

feeds:
- url: https://example.com/rss.xml
  title_prefix: Example
  << : *feed
```

## Bot configuration

You have to set bot token in `data/.env` file.
For example:

```dotenv
TELEGRAM_BOT_TOKEN=my_telegram_bot_token
```

## Deployment

You can use an example provided in `prod.docker-compose.yml` file for deployment.
Create `docker-compose.yml` file and paste contents from `prod.docker-compose.yml` file into it.
You should also create `data` (for keeping `data/.env` and `data/config.yaml`) and `filters` (for keeping custom filters) directories. 

After setting up feeds in config and configuring bot token, you can start the bot with docker-compose.

```sh
docker-compose up --build
```

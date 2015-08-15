"""Workaround for Twitter's lack of a safe search option."""
import re


def safe_filter(unsafe_list):
    """Filter out inappropriate tweets."""
    safe_list = []
    for tweet in unsafe_list:
        if is_safe(tweet):
            safe_list.append(tweet)
    return safe_list


def is_safe(tweet):
    """
    Check tweet for 'safety', by comparing to a long list of
    regular expressions.
    """
    for regex in regexs:
        if re.search(regex, tweet['text']):
            return False
        if re.search(regex, tweet['user']['screen_name']):
            return False
        if 'urls' in tweet:
            for url in tweet['urls']:
                if re.search(regex, url['expanded_url']):
                    return False
        if 'media' in tweet:
            for media in tweet['media']:
                if re.search(regex, media['expanded_url']):
                    return False
    return True

patterns = [r"porn",
            r"sex",
            r"asian",
            r"ass",
            r"amateur",
            r"anal",
            r"boner",
            r"blowjob",
            r"booty",
            r"busty",
            r"cam",
            r"cock",
            r"cum",
            r"dating",
            r"dildo",
            r"erotic",
            r"facial",
            r"fuck",
            r"gangbang",
            r"hot",
            r"horny",
            r"jailbait",
            r"kink",
            r"masturbation",
            r"milf",
            r"naked",
            r"nsfw",
            r"orgy",
            r"pussy",
            r"rape",
            r"shemale",
            r"slut",
            r"teen",
            r"threesome",
            r"thong",
            r"tits",
            r"topless",
            r"vagina",
            r"whore",
            r"xxx",
            ]
regexs = [re.compile(pattern, flags=re.I) for pattern in patterns]

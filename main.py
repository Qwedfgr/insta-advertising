import os
import argparse
import re
from instabot import Bot
from dotenv import load_dotenv
import requests
from pprint import pprint


def main():
    load_dotenv()
    bot = init_bot()
    link = get_link_from_arg()
    post_id = bot.get_media_id_from_link(link=link)
    number_of_friends_needed = 2
    users_tagged_friends = get_users_tagged_friends(bot, post_id, number_of_friends_needed)
    post_likers = bot.get_media_likers(post_id)
    author_followers = get_users_author_followers(bot, link)
    users = get_users_to_giveaway(users_tagged_friends, post_likers, author_followers)
    pprint(users)


def get_users_to_giveaway(users_tagged_friends, post_likers, author_followers):
    users = []
    for user in users_tagged_friends:
        if post_likers.count(str(user['pk'])) and author_followers.count(str(user['pk'])):
            users.append((user['pk'], user['username']))
    return users


def get_users_author_followers(bot, link):
    author = get_author(link)
    author_id = bot.get_user_id_from_username(author)
    return bot.get_user_following(author_id)


def get_author(link):
    response = requests.get(url=link)
    return get_users_from_comment(response.text, False)


def init_bot():
    LOGIN = os.getenv("LOGIN")
    PASSWORD = os.getenv('PASSWORD')
    bot = Bot()
    bot.login(username=LOGIN, password=PASSWORD, use_cookie=False)
    return bot


def get_users_from_comment(comment, find_all=True):
    """
    The RegEx taken from article
    https://blog.jstassen.com/2016/03/code-regex-for-instagram-username-and-hashtags/
    """
    pattern = '(?:@)([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)'
    if find_all:
        return re.findall(pattern, comment)
    else:
        return re.search(pattern, comment).group(0)[1::]


def is_user_exist(bot, username):
    user_id = bot.get_user_id_from_username(username)
    return user_id is not None


def get_users_tagged_friends(bot, post_id, number_of_friends_needed=2):
    comments = bot.get_media_comments_all(media_id=post_id)
    list_of_users = []
    set_of_usernames = set()
    for comment in comments:
        if comment['user']['username'] in set_of_usernames:
            continue
        users = get_users_from_comment(comment['text'])
        users_exist = sum([is_user_exist(bot, user) for user in users])
        if users_exist < number_of_friends_needed:
            continue
        list_of_users.append(comment['user'])
        set_of_usernames.add(comment['user']['username'])
    return list_of_users


def get_link_from_arg():
    parser = argparse.ArgumentParser(
        description='Программа выводит список пользователей, выполнивших условия конкурса по ссылке.'
    )
    parser.add_argument('link', help='Ссылка')
    args = parser.parse_args()
    link = args.link
    return link


if __name__ == '__main__':
    main()


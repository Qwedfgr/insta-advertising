import os
import argparse
import re
from instabot import Bot
from dotenv import load_dotenv
import requests
from pprint import pprint


def main():
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
        if post_likers.count(str(user['pq'])) and author_followers.count(str(user['pq'])):
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
    load_dotenv()
    LOGIN = os.getenv("LOGIN")
    PASSWORD = os.getenv('PASSWORD')
    bot = Bot()
    bot.login(username=LOGIN, password=PASSWORD, use_cookie=False)
    return bot


def get_users_from_comment(comment, all=True):
    pattern = '(?:@)([A-Za-z0-9_](?:(?:[A-Za-z0-9_]|(?:\.(?!\.))){0,28}(?:[A-Za-z0-9_]))?)'
    if all:
        return re.findall(pattern, comment)
    else:
        return re.search(pattern, comment).group(0)[1::]


def is_user_exist(bot, username):
    user_id = bot.get_user_id_from_username(username)
    return user_id is not None


def get_users_tagged_friends(bot, post_id, number_of_friends_needed=2):
    comments = bot.get_media_comments_all(media_id=post_id)
    list_of_users = []
    set_of_username = set()
    users_exist = 0
    for comment in comments:
        if not comment['user']['username'] in set_of_username:
            users = get_users_from_comment(comment['text'])
            for user in users:
                if is_user_exist(bot, user):
                    users_exist += 1
            if users_exist >= number_of_friends_needed:
                list_of_users.append(comment['user'])
                set_of_username.add(comment['user']['username'])
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


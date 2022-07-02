from datetime import datetime
from multiprocessing import Queue
from random import choice
from time import sleep
from twitchAPI.twitch import Twitch, AuthScope
from twitchAPI.pubsub import PubSub
from twitchAPI.oauth import UserAuthenticator
from os import getenv

from . import config

_scope = [
    AuthScope.BITS_READ,
    AuthScope.CHANNEL_MANAGE_REDEMPTIONS,
    AuthScope.CHANNEL_READ_SUBSCRIPTIONS,
    AuthScope.CHAT_READ,
    AuthScope.CHANNEL_READ_REDEMPTIONS,
]

_client = Twitch(
    getenv("TWITCH_CLIENT_ID"), 
    getenv("TWITCH_CLIENT_SECRET"), 
    target_app_auth_scope=_scope
)

_speak_queue: Queue = None
_time_queue: Queue = None

class UserNotFoundError(Exception):
    """An error raised when attempting to set an animation state that does not exist."""
    def __init__(self, username, *args: object) -> None:
        super().__init__(f"User {username} was not found on Twitch. Did you spell the name correctly?", *args)

def _time_message(time: int):
    if not config.main.streamathon_settings.enabled:
        return
    minutes = time // 60
    hours = minutes // 60
    minutes = minutes % 60
    seconds = time % 60
    if hours:
        return f"{hours} hours, {minutes} minuts, and {seconds} seconda have been added to the clock. Hot damn!"
    elif minutes:
        return f"{minutes} minutes and {seconds} seconds have been added to the clock."
    else:
        return f"{seconds} have been added to the clock"


class Hooks:
    def channel_points(uuid, data):
        data = data["data"]["redemption"]
        for v in config.main.tts_rewards:
            if v.name == data["reward"]["title"]:
                _speak_queue.put((data["user_input"], v.animation))
        if data["reward"]["title"] in config.main.streamathon_settings.time.rewards:
            time = choice(config.main.streamathon_settings.time.rewards[data["reward"]["title"]])
            _time_queue.put(time)
            message = _time_message(time)
            _speak_queue.put((
                f"Reward Redeemed! {message}", 
                config.main.streamathon_settings.message_animation
            ))


    def bits(uuid, data):
        bits = data['bits_used']
        time = bits * choice(config.main.streamathon_settings.bits)
        _time_queue.put(time)
        message = _time_message(time)
        if data["user_name"]:
            _speak_queue.put((
                f"Thank you to {data['username']} for cheering {bits} bits! {message}", 
                config.main.streamathon_settings.message_animation
            ))
        else:
            _speak_queue.put((
                message, 
                config.main.streamathon_settings.message_animation
            ))

    def subscribe(uuid, data):
        time = choice(config.main.streamathon_settings.time.subscription)
        _time_queue.put(time)
        message = _time_message(time)
        if data["is_gift"]:
            _speak_queue.put((
                f"{data['recipient_user_name']} received a gift from {data['user_name']}! {message}", 
                config.main.streamathon_settings.message_animation
            ))
        else:
            _speak_queue.put((
                f"Thank you for subscribing, {data['user_name']}! {message}", 
                config.main.streamathon_settings.message_animation
            ))
            

def run(speak_queue: Queue, time_queue: Queue):
    global _speak_queue, _time_queue
    _speak_queue = speak_queue
    _time_queue = time_queue
    auth = UserAuthenticator(_client, _scope, force_verify=False)
    token, refresh = auth.authenticate()
    _client.set_user_authentication(token, _scope, refresh)
    _client.authenticate_app([])

    users = _client.get_users(logins=[config.main.twitch_username])["data"]
    if not users:
        raise UserNotFoundError(config.main.twitch_username)
    (user,) = users
    pubsub = PubSub(_client)
    pubsub.start()
    pubsub.listen_channel_points(user["id"], Hooks.channel_points)
    pubsub.listen_bits(user["id"], Hooks.bits)
    pubsub.listen_channel_subscriptions(user["id"], Hooks.subscribe)

    # Slightly hacky follow tracking, since this doesn't use EventSub
    # This bot is a great example of a bodge, I think
    last_page = None
    since = datetime.utcnow()
    followed_this_stream = {}
    while True:
        follows = _client.get_users_follows(after = last_page, to_id = user["id"], first = 20)
        last_page = follows["pagination"]["cursor"] if "cursor" in follows["pagination"] else None
        for follow in follows["data"]:
            if (
                follow['from_name'] not in followed_this_stream and 
                datetime.fromisoformat(follow["followed_at"][:-1]) > since
            ):
                followed_this_stream[follow['from_name']] = True
                time = choice(config.main.streamathon_settings.time.follow)
                message = _time_message(time)
                _time_queue.put(time)
                _speak_queue.put((
                    f"Thank you for the follow {follow['from_name']}! {message}",
                    config.main.streamathon_settings.message_animation
                ))

        if not last_page:
            sleep(15)

        sleep(.5)
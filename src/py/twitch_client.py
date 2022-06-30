from multiprocessing import Queue
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

class UserNotFoundError(Exception):
    """An error raised when attempting to set an animation state that does not exist."""
    def __init__(self, username, *args: object) -> None:
        super().__init__(f"User {username} was not found on Twitch. Did you spell the name correctly?", *args)

class Hooks:
    def channel_points(uuid, data):
        data = data["data"]["redemption"]
        for v in config.main.tts_rewards:
            if v.name == data["reward"]["title"]:
                _speak_queue.put([(data["user_input"], v.animation)])

def run(speak_queue: Queue):
    global _speak_queue
    _speak_queue = speak_queue
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
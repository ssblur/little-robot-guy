# Title
*A collection of Twitch stream utilities I use.*

## Token Generator
You can generate tokens with the necessary permissions for current and planned modules [here](https://twitchtokengenerator.com/quick/iJLc3zWOEZ).

## Configuration
Check example_config and .env.example, more details will be added here later.

Layers used for animations by the bot can be placed in src/js/public/layers

## Running
This app can be run with `python .` or `python __main__.py`

I included a geckodriver selenium app because my OBS likes to remove the eyes when I try to use this. You need geckodriver, which can be found [here](https://github.com/mozilla/geckodriver/releases). Recommend building with cargo (`cargo install geckodriver`). You can enable this with `"selenium": true` in `config/main.json` ~~or by using the command line option~~.

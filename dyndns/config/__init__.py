import toml

CONFIG = {}

with open('config.toml') as f:
    CONFIG = toml.load(f)

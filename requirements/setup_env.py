"""Creating .env file."""
env_consts = {
    'PG_HOST': '127.0.0.1',
    'PG_PORT': '5525',
    'PG_USER': 'app',
    'PG_PASSWORD': '242002',
    'PG_DBNAME': 'BeautySalon',
}


def setup_env():
    """Setting up .env file."""
    lines = [f'{const}={equiv}\n' for const, equiv in env_consts.items()]
    with open('./beauty_salon/.env', 'w') as env_file:
        env_file.writelines(lines)


if __name__ == '__main__':
    setup_env()
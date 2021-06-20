class Utils(object):
    def get_avatar_url(user, format="png", size="64"):
        if user:
            return f"https://cdn.discordapp.com/avatars/{user.id}/{user.avatar}.{format}?size={size}"
from media_command_base import MediaCommand
from media_youtube import MediaYoutubeCommand

__author__ = 'macbook'


def get_command(domain, domain_action, *args, **kwargs):
    if(domain == "youtube"):
        return MediaYoutubeCommand(domain, domain_action, *args, **kwargs)
    return MediaCommand(domain, domain_action, *args, **kwargs)

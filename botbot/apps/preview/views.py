from launchpad.views import Signup

from botbot.apps.bots.models import Channel


class LandingPage(Signup):
    def get_context_data(self, **kwargs):
        public_channels = (
            Channel.objects.active()
            .filter(is_public=True)
            .select_related('chatbot')
        )
        kwargs.update({
            'featured_channels': public_channels.filer(is_featured=True)
            'public_not_featured_channels': public_channels.filter(is_featured=False)
        })
        return kwargs

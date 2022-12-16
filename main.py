import subprocess

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import ItemEnterEvent, KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem

DJANGO_SERVERS = [
    ("django-test.di.unistra.fr",),
    ("django-test2.di.unistra.fr",),
    ("django-pprd-w1.u-strasbg.fr", "django-pprd-w2.u-strasbg.fr"),
    ("django-pprd-w3.di.unistra.fr", "django-pprd-w4.di.unistra.fr"),
    ("django-w3.u-strasbg.fr", "django-w4.u-strasbg.fr"),
    ("django-w7.di.unistra.fr", "django-w8.di.unistra.fr"),
]


class CircusCtlExtension(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        items = []
        for server in DJANGO_SERVERS:
            items.append(
                ExtensionResultItem(
                    icon="images/icon.png",
                    name=", ".join(server),
                    description=f"Restart {' and '.join(server)}",
                    on_enver=ExtensionCustomAction(
                        data={"server": server},
                        keep_app_open=True,
                    ),
                )
            )
        return RenderResultListAction(items)


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        data = event.get_data()
        result = []
        for server in data["server"]:
            process_result = subprocess.run(["ssh", f"root@{server}", "circusctl restart"], capture_output=True)
            result.append(f"{server}: {process_result.stdout.decode()}")
        subprocess.run(["zenity", "--info", "--no-wrap", "--text", "\n".join(result)])
        return HideWindowAction()


if __name__ == "__main__":
    CircusCtlExtension().run()

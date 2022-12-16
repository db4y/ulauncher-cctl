import subprocess

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import ItemEnterEvent, KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.utils.desktop.notification import show_notification

DJANGO_SERVERS = [
    ("django-test.di.unistra.fr",),
    ("django-test2.di.unistra.fr",),
    ("django-pprd-w1.u-strasbg.fr", "django-pprd-w2.u-strasbg.fr"),
    ("django-pprd-w3.di.unistra.fr", "django-pprd-w4.di.unistra.fr"),
    ("django-w3.u-strasbg.fr", "django-w4.u-strasbg.fr"),
    ("django-w7.di.unistra.fr", "django-w8.di.unistra.fr"),
]


class CircusReloaderExtension(Extension):
    def __init__(self) -> None:
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener(servers=DJANGO_SERVERS))
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class KeywordQueryEventListener(EventListener):
    def __init__(self, servers: list[tuple[str, ...]]) -> None:
        self.servers = servers

    def on_event(self, event, extension) -> RenderResultListAction:
        items = []
        for server in self.servers:
            items.append(
                ExtensionResultItem(
                    icon="images/icon.png",
                    name=", ".join(server),
                    description=f"Restart {', '.join(server)}",
                    on_enter=ExtensionCustomAction(
                        data={"servers": server},
                        keep_app_open=True,
                    ),
                )
            )
        return RenderResultListAction(items)


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        data = event.get_data()
        servers: tuple[str] = data["servers"]
        result = []
        for server in servers:
            pr = subprocess.run(
                ["ssh", f"root@{server}", "circusctl restart"],
                capture_output=True,
            )
            result.append(f"{server}: {pr.stdout.decode()}")
        show_notification("Circusd restart", f"Circusd restarted: {', '.join(result)}")
        return HideWindowAction()


if __name__ == "__main__":
    CircusReloaderExtension().run()

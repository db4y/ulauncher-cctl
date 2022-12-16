import subprocess

from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.client.Extension import Extension
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.HideWindowAction import HideWindowAction
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.event import ItemEnterEvent, KeywordQueryEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.utils.desktop.notification import show_notification


class CircusReloaderExtension(Extension):
    def __init__(self, django_servers: list[tuple[str, ...]]) -> None:
        self.django_servers = django_servers
        super().__init__()
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener(servers=self.django_servers))
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

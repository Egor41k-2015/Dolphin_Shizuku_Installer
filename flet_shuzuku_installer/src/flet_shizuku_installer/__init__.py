import flet as ft


@ft.control("ShizukuInstaller")
class ShizukuInstaller(ft.Service):
    """Сервис установки APK через Shizuku или Dhizuku."""

    async def set_mode(self, mode: str):
        """mode: 'shizuku' или 'dhizuku'."""
        await self._invoke_method("set_mode", {"mode": mode})

    async def check_permission(self) -> bool:
        return await self._invoke_method("check_permission")

    async def install(self, path: str):
        await self._invoke_method("install", {"path": path})

    async def uninstall(self, package: str):
        await self._invoke_method("uninstall", {"package": package})

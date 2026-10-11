import flet as ft


@ft.control("ShizukuInstaller")
class ShizukuInstaller(ft.Service):
    """
    Сервис установки APK через Shizuku или Dhizuku.
    Использует Flutter-плагин shizuku_apk_installer.
    """

    async def set_mode(self, mode: str):
        """Устанавливает режим: 'shizuku' или 'dhizuku'."""
        await self._invoke_method("set_mode", {"mode": mode})

    async def check_permission(self) -> bool:
        """Проверяет, выданы ли разрешения в выбранном режиме."""
        return await self._invoke_method("check_permission")

    async def install(self, path: str):
        """Устанавливает APK по указанному пути."""
        await self._invoke_method("install", {"path": path})

    async def uninstall(self, package: str):
        """Удаляет приложение по имени пакета."""
        await self._invoke_method("uninstall", {"package": package})

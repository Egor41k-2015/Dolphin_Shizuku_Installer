import os
from pathlib import Path

import flet as ft
from flet_shizuku_installer import ShizukuInstaller


# ────────────────────────────────────────────────────────────
#  Вспомогательные функции
# ────────────────────────────────────────────────────────────

INSTALLER_EXT = {".apk", ".apks", ".xapk", ".apkm"}


def scan_folder(folder: str) -> list[dict]:
    """Ищет установщики в папке."""
    if not folder or not os.path.isdir(folder):
        return []
    result = []
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        if os.path.isfile(path) and Path(name).suffix.lower() in INSTALLER_EXT:
            result.append({
                "path": path,
                "name": name,
                "ext": Path(name).suffix.lower(),
                "size": os.path.getsize(path),
            })
    return result


def human_size(n: int) -> str:
    for unit in ("Б", "КБ", "МБ", "ГБ"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} ТБ"


# ────────────────────────────────────────────────────────────
#  Палитра акцентов
# ────────────────────────────────────────────────────────────

ACCENTS = {
    "Синий":      ft.Colors.BLUE,
    "Индиго":     ft.Colors.INDIGO,
    "Фиолетовый": ft.Colors.PURPLE,
    "Розовый":    ft.Colors.PINK,
    "Красный":    ft.Colors.RED,
    "Оранжевый":  ft.Colors.ORANGE,
    "Янтарный":   ft.Colors.AMBER,
    "Зелёный":    ft.Colors.GREEN,
    "Бирюзовый":  ft.Colors.TEAL,
    "Голубой":    ft.Colors.CYAN,
}


# ────────────────────────────────────────────────────────────
#  Приложение
# ────────────────────────────────────────────────────────────

class InstallerApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.prefs = ft.SharedPreferences()
        self.work_dir = ""
        self.scanned: list[dict] = []
        self.installer_mode = "shizuku"
        self._accent = "Синий"

        self._setup_page()
        self._build_ui()
        self.page.run_task(self._init_settings)

    async def _init_settings(self):
        # Тема
        mode = await self.prefs.get("theme_mode") or "system"
        self.theme_radio.value = mode
        self._accent = await self.prefs.get("accent") or "Синий"
        self._apply_theme()

        # Рабочая папка
        saved_dir = await self.prefs.get("work_dir")
        if saved_dir and os.path.isdir(saved_dir):
            self.work_dir = saved_dir
        else:
            self.work_dir = "/sdcard/Download"
        self.work_dir_text.value = self.work_dir

        # Режим
        self.installer_mode = await self.prefs.get("installer_mode") or "shizuku"
        self.mode_radio.value = self.installer_mode
        try:
            await self.installer.set_mode(self.installer_mode)
        except Exception as ex:
            self.status_text.value = f"⚠️ Не удалось задать режим: {ex}"

        await self._check_permission()
        self._scan_work_dir()
        self.page.update()

    async def _check_permission(self):
        try:
            granted = await self.installer.check_permission()
            if granted:
                self.status_text.value = f"✅ Разрешения {self.installer_mode} выданы"
                self.status_text.color = ft.Colors.GREEN_700
            else:
                self.status_text.value = f"❌ Нет разрешений {self.installer_mode}"
                self.status_text.color = ft.Colors.RED_700
        except Exception as ex:
            self.status_text.value = f"❌ Ошибка: {ex}"
            self.status_text.color = ft.Colors.RED_700
        self.page.update()

    def _apply_theme(self):
        seed = ACCENTS.get(self._accent, ft.Colors.GREEN)
        self.page.theme = ft.Theme(color_scheme_seed=seed)
        self.page.dark_theme = ft.Theme(color_scheme_seed=seed)
        self.page.theme_mode = {
            "light":  ft.ThemeMode.LIGHT,
            "dark":   ft.ThemeMode.DARK,
            "system": ft.ThemeMode.SYSTEM,
        }.get(self.theme_radio.value or "system", ft.ThemeMode.SYSTEM)
        self.page.update()

    def _setup_page(self):
        self.page.title = "APK Installer (Shizuku/Dhizuku)"
        self.page.padding = 0
        self.page.window.width = 460
        self.page.window.height = 820

    def _build_ui(self):
        # ──── Главная ────
        self.status_text = ft.Text("Проверка разрешений…", size=13,
                                   color=ft.Colors.GREY_600)
        self.apk_list = ft.ListView(spacing=4, padding=4, expand=True)
        self.apk_counter = ft.Text("", size=12, color=ft.Colors.GREY_600)
        self.refresh_btn = ft.OutlinedButton(
            "Обновить список",
            icon=ft.Icons.REFRESH,
            on_click=lambda e: self._scan_work_dir(),
        )

        home_screen = ft.Column(
            [
                ft.Row([
                    ft.Icon(ft.Icons.ANDROID, size=30,
                            color=ft.Colors.PRIMARY),
                    ft.Text("APK Installer", size=22,
                            weight=ft.FontWeight.BOLD),
                ], spacing=10),
                self.status_text,
                ft.Divider(),
                ft.Row([
                    ft.Text("Установщики в папке", size=14,
                            weight=ft.FontWeight.W_600),
                    ft.Container(expand=True),
                    self.apk_counter,
                ]),
                self.refresh_btn,
                ft.Container(self.apk_list, expand=True),
            ],
            spacing=10, expand=True, scroll=ft.ScrollMode.AUTO,
        )

        # ──── Настройки ────
        self.theme_radio = ft.RadioGroup(
            value="system",
            content=ft.Column([
                ft.Radio(value="light", label="Светлая"),
                ft.Radio(value="dark", label="Тёмная"),
                ft.Radio(value="system", label="Системная"),
            ]),
            on_change=self._on_theme_mode_change,
        )
        self.mode_radio = ft.RadioGroup(
            value="shizuku",
            content=ft.Column([
                ft.Radio(value="shizuku", label="Shizuku"),
                ft.Radio(value="dhizuku", label="Dhizuku"),
            ]),
            on_change=self._on_mode_change,
        )
        self.work_dir_text = ft.Text("", size=13, selectable=True)
        self.pick_dir_btn = ft.OutlinedButton(
            "Выбрать папку",
            icon=ft.Icons.FOLDER_OPEN,
            on_click=self._on_pick_dir,
        )

        settings_screen = ft.Column(
            [
                ft.Text("⚙️ Настройки", size=22, weight=ft.FontWeight.BOLD),
                ft.Divider(),
                ft.Text("Тема", size=14, weight=ft.FontWeight.W_600),
                self.theme_radio,
                ft.Divider(),
                ft.Text("Режим установки", size=14,
                        weight=ft.FontWeight.W_600),
                ft.Text(
                    "Shizuku: требует запущенного сервиса.\n"
                    "Dhizuku: требует прав Device Owner.",
                    size=11, color=ft.Colors.GREY_600,
                ),
                self.mode_radio,
                ft.Divider(),
                ft.Text("Рабочая папка", size=14,
                        weight=ft.FontWeight.W_600),
                self.work_dir_text,
                ft.Row([self.pick_dir_btn], spacing=8),
            ],
            spacing=10, expand=True, scroll=ft.ScrollMode.AUTO,
        )

        # ──── Навигация ────
        self.nav = ft.NavigationBar(
            selected_index=0,
            destinations=[
                ft.NavigationBarDestination(
                    icon=ft.Icons.HOME_OUTLINED,
                    selected_icon=ft.Icons.HOME,
                    label="Главная"),
                ft.NavigationBarDestination(
                    icon=ft.Icons.SETTINGS_OUTLINED,
                    selected_icon=ft.Icons.SETTINGS,
                    label="Настройки"),
            ],
            on_change=lambda e: self._navigate(e.control.selected_index),
        )

        self.stage = ft.Container(
            content=ft.Column([home_screen, settings_screen], expand=True),
            expand=True, padding=16,
        )
        self._screens = [home_screen, settings_screen]

        self.page.navigation_bar = self.nav
        self.page.add(self.stage)

        # Сервис установщика
        self.installer = ShizukuInstaller()
        self.page.services.append(self.installer)

    def _navigate(self, index: int):
        for i, s in enumerate(self._screens):
            s.visible = (i == index)
        self.page.update()

    # ─── Настройки ───

    async def _on_theme_mode_change(self, e):
        await self.prefs.set("theme_mode", e.control.value)
        self._apply_theme()

    async def _on_mode_change(self, e):
        new_mode = e.control.value
        self.installer_mode = new_mode
        await self.prefs.set("installer_mode", new_mode)
        try:
            await self.installer.set_mode(new_mode)
            await self._check_permission()
        except Exception as ex:
            self.status_text.value = f"❌ {ex}"
            self.status_text.color = ft.Colors.RED_700
        self.page.show_dialog(
            ft.SnackBar(ft.Text(f"Режим: {new_mode}")))

    async def _on_pick_dir(self, e):
        picker = ft.FilePicker()
        self.page.services.append(picker)
        try:
            path = await picker.get_directory_path(
                dialog_title="Выберите папку")
        except Exception as ex:
            self.page.show_dialog(ft.SnackBar(ft.Text(f"Ошибка: {ex}")))
            return
        if not path:
            return
        self.work_dir = path
        self.work_dir_text.value = path
        await self.prefs.set("work_dir", path)
        self._scan_work_dir()
        self.page.update()

    # ─── Сканирование и установка ───

    def _scan_work_dir(self):
        self.scanned = scan_folder(self.work_dir)
        self.apk_list.controls.clear()
        if not self.scanned:
            self.apk_list.controls.append(
                ft.Container(
                    ft.Text(
                        f"В папке {self.work_dir} нет установщиков.",
                        size=12, color=ft.Colors.GREY_500),
                    padding=20, alignment=ft.alignment.center,
                )
            )
        else:
            for item in self.scanned:
                self.apk_list.controls.append(self._build_apk_row(item))
        self.apk_counter.value = f"{len(self.scanned)}"
        self.page.update()

    def _build_apk_row(self, item: dict) -> ft.Control:
        return ft.Container(
            content=ft.Column([
                ft.Text(item["name"], size=13,
                        weight=ft.FontWeight.W_500, selectable=True),
                ft.Text(f"{item['ext']} · {human_size(item['size'])}",
                        size=11, color=ft.Colors.GREY_600),
                ft.Row([
                    ft.FilledButton(
                        "Установить",
                        icon=ft.Icons.INSTALL_MOBILE,
                        on_click=lambda e, it=item:
                            self.page.run_task(self._install_item, it),
                    )
                ], alignment=ft.MainAxisAlignment.END),
            ], spacing=4),
            padding=10, border_radius=8,
            bgcolor=ft.Colors.SURFACE_CONTAINER_HIGHEST,
        )

    async def _install_item(self, item: dict):
        self.page.show_dialog(ft.SnackBar(
            ft.Text(f"Установка {item['name']}…"), duration=2000))
        try:
            await self.installer.install(item["path"])
            self.page.show_dialog(ft.SnackBar(
                ft.Text(f"✅ {item['name']} установлено"),
                bgcolor=ft.Colors.GREEN_700))
        except Exception as ex:
            self.page.show_dialog(ft.SnackBar(
                ft.Text(f"❌ Ошибка: {ex}"),
                bgcolor=ft.Colors.RED_700))


def main(page: ft.Page):
    InstallerApp(page)


if __name__ == "__main__":
    ft.run(main)

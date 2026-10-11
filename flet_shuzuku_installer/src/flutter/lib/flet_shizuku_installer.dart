import 'package:flet/flet.dart';
import 'package:flutter/widgets.dart';
import 'src/shizuku_installer_service.dart';

/// Точка входа для Flet-расширения.
/// Регистрирует сервис ShizukuInstaller.
class Extension extends FletExtension {
  @override
  void ensureInitialized() {}

  @override
  FletService? createService(Control control) {
    switch (control.type) {
      case "ShizukuInstaller":
        return ShizukuInstallerService(control: control);
      default:
        return null;
    }
  }

  @override
  Widget? createWidget(Key? key, Control control) {
    return null; // сервис, не виджет
  }
}

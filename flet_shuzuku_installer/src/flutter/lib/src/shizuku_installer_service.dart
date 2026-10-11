import 'package:flet/flet.dart';
import 'package:flutter/services.dart';
import 'package:shizuku_apk_installer/shizuku_apk_installer.dart';

/// Сервис, который связывает Python-код с Flutter-плагином
/// shizuku_apk_installer.
class ShizukuInstallerService extends FletService {
  final ShizukuApkInstaller _installer = ShizukuApkInstaller();

  ShizukuInstallerService({required super.control});

  @override
  void init() {
    super.init();
    debugPrint("[flet-shizuku] init()");
    control.addInvokeMethodListener(_invokeMethod);
  }

  Future<dynamic> _invokeMethod(String name, dynamic args) async {
    debugPrint("[flet-shizuku] invoke: $name ($args)");

    switch (name) {
      case 'set_mode':
        final mode = args['mode'] == 'dhizuku'
            ? InstallerMode.dhizuku
            : InstallerMode.shizuku;
        await _installer.setInstallerMode(mode);
        return true;

      case 'check_permission':
        final granted = await _installer.checkPermission();
        return granted;

      case 'install':
        try {
          await _installer.install(args['path']);
          return true;
        } on PlatformException catch (e) {
          throw Exception('Ошибка установки: ${e.message}');
        } catch (e) {
          throw Exception('Ошибка: $e');
        }

      case 'uninstall':
        await _installer.uninstall(args['package']);
        return true;

      default:
        throw Exception('Неизвестный метод: $name');
    }
  }

  @override
  void dispose() {
    debugPrint("[flet-shizuku] dispose()");
    control.removeInvokeMethodListener(_invokeMethod);
    super.dispose();
  }
}

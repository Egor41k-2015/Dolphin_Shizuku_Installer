import 'package:flet/flet.dart';
import 'package:flutter/services.dart';
import 'package:shizuku_apk_installer/shizuku_apk_installer.dart';

class FletShizukuInstaller extends FletService {
  final ShizukuApkInstaller _installer = ShizukuApkInstaller();

  FletShizukuInstaller({required super.control});

  @override
  void init() {
    super.init();
    control.addInvokeMethodListener(_invokeMethod);
  }

  Future<dynamic> _invokeMethod(String name, dynamic args) async {
    switch (name) {
      case 'set_mode':
        final mode = args['mode'] == 'dhizuku'
            ? InstallerMode.dhizuku
            : InstallerMode.shizuku;
        await _installer.setInstallerMode(mode);
        return true;

      case 'check_permission':
        return await _installer.checkPermission();

      case 'install':
        try {
          await _installer.install(args['path']);
          return true;
        } on PlatformException catch (e) {
          throw Exception('Ошибка установки: ${e.message}');
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
    control.removeInvokeMethodListener(_invokeMethod);
    super.dispose();
  }
}

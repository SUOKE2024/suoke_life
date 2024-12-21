import 'package:get/get.dart';
import '../../core/base/base_controller.dart';
import '../../core/services/storage_service.dart';

class LoginNotificationController extends BaseController {
  final _storage = Get.find<StorageService>();

  final notificationEnabled = false.obs;
  final inAppNotification = false.obs;
  final emailNotification = false.obs;
  final smsNotification = false.obs;
  final newDeviceNotification = false.obs;
  final unusualLocationNotification = false.obs;
  final unusualTimeNotification = false.obs;

  @override
  void onInit() {
    super.onInit();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    notificationEnabled.value = await _storage.getBool('login_notification') ?? false;
    inAppNotification.value = await _storage.getBool('login_notification_in_app') ?? false;
    emailNotification.value = await _storage.getBool('login_notification_email') ?? false;
    smsNotification.value = await _storage.getBool('login_notification_sms') ?? false;
    newDeviceNotification.value = await _storage.getBool('login_notification_new_device') ?? false;
    unusualLocationNotification.value = await _storage.getBool('login_notification_unusual_location') ?? false;
    unusualTimeNotification.value = await _storage.getBool('login_notification_unusual_time') ?? false;
  }

  Future<void> toggleNotification(bool value) async {
    await _storage.setBool('login_notification', value);
    notificationEnabled.value = value;
  }

  Future<void> toggleInAppNotification(bool value) async {
    await _storage.setBool('login_notification_in_app', value);
    inAppNotification.value = value;
  }

  Future<void> toggleEmailNotification(bool value) async {
    await _storage.setBool('login_notification_email', value);
    emailNotification.value = value;
  }

  Future<void> toggleSmsNotification(bool value) async {
    await _storage.setBool('login_notification_sms', value);
    smsNotification.value = value;
  }

  Future<void> toggleNewDeviceNotification(bool value) async {
    await _storage.setBool('login_notification_new_device', value);
    newDeviceNotification.value = value;
  }

  Future<void> toggleUnusualLocationNotification(bool value) async {
    await _storage.setBool('login_notification_unusual_location', value);
    unusualLocationNotification.value = value;
  }

  Future<void> toggleUnusualTimeNotification(bool value) async {
    await _storage.setBool('login_notification_unusual_time', value);
    unusualTimeNotification.value = value;
  }
} 
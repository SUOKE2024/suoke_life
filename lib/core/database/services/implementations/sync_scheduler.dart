import 'dart:async';
import 'package:get/get.dart';
import 'sync_service.dart';
import 'connectivity_service.dart';
import '../models/sync_settings.dart';

class SyncScheduler extends GetxService {
  final _syncService = Get.find<SyncService>();
  final _connectivityService = Get.find<ConnectivityService>();
  Timer? _syncTimer;

  @override
  void onInit() {
    super.onInit();
    _setupAutoSync();
  }

  @override
  void onClose() {
    _syncTimer?.cancel();
    super.onClose();
  }

  Future<void> _setupAutoSync() async {
    try {
      final settings = await _syncService.getSettings();
      if (settings.autoSync) {
        _scheduleSyncTask(settings.interval);
      }
    } catch (e) {
      print('Failed to setup auto sync: $e');
    }
  }

  void _scheduleSyncTask(String interval) {
    _syncTimer?.cancel();

    final duration = _getIntervalDuration(interval);
    if (duration != null) {
      _syncTimer = Timer.periodic(duration, (_) => _performSync());
    }
  }

  Duration? _getIntervalDuration(String interval) {
    switch (interval) {
      case '每小时':
        return const Duration(hours: 1);
      case '每天':
        return const Duration(days: 1);
      case '每周':
        return const Duration(days: 7);
      case '每月':
        return const Duration(days: 30);
      default:
        return null;
    }
  }

  Future<void> _performSync() async {
    if (!_connectivityService.hasConnection) {
      print('No network connection, skipping sync');
      return;
    }

    try {
      await _syncService.sync();
      print('Auto sync completed successfully');
    } catch (e) {
      print('Auto sync failed: $e');
    }
  }

  void updateSchedule(SyncSettings settings) {
    if (settings.autoSync) {
      _scheduleSyncTask(settings.interval);
    } else {
      _syncTimer?.cancel();
    }
  }
} 
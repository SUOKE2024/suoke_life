import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../core/base/base_controller.dart';
import '../../data/services/sync_service.dart';

class SyncRangeController extends BaseController {
  final _syncService = Get.find<SyncService>();
  final selectedRange = '最近7天'.obs;
  final customStartDate = Rx<DateTime?>(null);
  final customEndDate = Rx<DateTime?>(null);

  @override
  void onInit() {
    super.onInit();
    loadRange();
  }

  Future<void> loadRange() async {
    try {
      showLoading();
      final settings = await _syncService.getSettings();
      selectedRange.value = settings.range;
      if (settings.range.contains('至')) {
        final dates = settings.range.split('至');
        customStartDate.value = DateTime.parse(dates[0].trim());
        customEndDate.value = DateTime.parse(dates[1].trim());
      }
      hideLoading();
    } catch (e) {
      showError(e.toString());
    }
  }

  Future<void> updateRange(String range) async {
    try {
      showLoading();
      await _syncService.saveSettings(
        autoSync: true, // 从其他控制器获取
        interval: '每天', // 从其他控制器获取
        range: range,
        conflictStrategy: '手动处理', // 从其他控制器获取
      );
      selectedRange.value = range;
      hideLoading();
      Get.back();
    } catch (e) {
      showError(e.toString());
    }
  }

  Future<void> updateCustomRange(DateTime? start, DateTime? end) async {
    if (start != null && end != null) {
      if (end.isBefore(start)) {
        showError('结束日期不能早于开始日期');
        return;
      }
      
      try {
        showLoading();
        final range = '${_formatDate(start)} 至 ${_formatDate(end)}';
        await _syncService.saveSettings(
          autoSync: true, // 从其他控制器获取
          interval: '每天', // 从其他控制器获取
          range: range,
          conflictStrategy: '手动处理', // 从其他控制器获取
        );
        customStartDate.value = start;
        customEndDate.value = end;
        selectedRange.value = range;
        hideLoading();
        Get.back();
      } catch (e) {
        showError(e.toString());
      }
    }
  }

  String _formatDate(DateTime date) {
    return '${date.year}-${date.month.toString().padLeft(2, '0')}-${date.day.toString().padLeft(2, '0')}';
  }
} 
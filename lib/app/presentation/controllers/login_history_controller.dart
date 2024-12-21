import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../services/login_record_service.dart';
import '../../data/models/login_record.dart';
import '../../core/base/base_controller.dart';

class LoginHistoryController extends BaseController {
  final _loginRecordService = Get.find<LoginRecordService>();
  
  final records = <LoginRecord>[].obs;
  final currentFilter = '全部'.obs;

  @override
  void onInit() {
    super.onInit();
    loadRecords();
  }

  Future<void> loadRecords() async {
    try {
      showLoading();
      records.value = await _loginRecordService.getLoginRecords(
        limit: 50,
      );
      hideLoading();
    } catch (e) {
      hideLoading();
      showError(e.toString());
    }
  }

  Future<void> refreshRecords() => loadRecords();

  void showFilterOptions() {
    Get.bottomSheet(
      Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Get.theme.scaffoldBackgroundColor,
          borderRadius: const BorderRadius.vertical(
            top: Radius.circular(20),
          ),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '筛选条件',
              style: TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Wrap(
              spacing: 8,
              children: [
                '全部',
                '密码登录',
                '生物识别',
                '微信登录',
                'Google登录',
                'Apple登录',
                '登录成功',
                '登录失败',
              ].map((filter) => FilterChip(
                label: Text(filter),
                selected: currentFilter.value == filter,
                onSelected: (selected) {
                  if (selected) {
                    currentFilter.value = filter;
                    _applyFilter(filter);
                    Get.back();
                  }
                },
              )).toList(),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _applyFilter(String filter) async {
    try {
      showLoading();
      records.value = await _loginRecordService.getLoginRecords(
        success: filter == '登录成功' ? true : (filter == '登录失败' ? false : null),
        limit: 50,
      );
      hideLoading();
    } catch (e) {
      hideLoading();
      showError(e.toString());
    }
  }

  void showRecordDetail(LoginRecord record) {
    Get.dialog(
      AlertDialog(
        title: const Text('登录详情'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('登录类型: ${_getLoginTypeText(record.loginType)}'),
            const SizedBox(height: 8),
            Text('状态: ${record.success ? "成功" : "失败"}'),
            if (record.errorMessage != null) ...[
              const SizedBox(height: 8),
              Text('错误信息: ${record.errorMessage}'),
            ],
            const SizedBox(height: 8),
            Text('设备信息: ${record.deviceInfo}'),
            const SizedBox(height: 8),
            Text('IP地址: ${record.ipAddress}'),
            const SizedBox(height: 8),
            Text('时间: ${record.timestamp}'),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: const Text('关闭'),
          ),
        ],
      ),
    );
  }

  String _getLoginTypeText(String type) {
    switch (type) {
      case 'password':
        return '密码登录';
      case 'biometric':
        return '生物识别';
      case 'wechat':
        return '微信登录';
      case 'google':
        return 'Google登录';
      case 'apple':
        return 'Apple登录';
      default:
        return type;
    }
  }
} 
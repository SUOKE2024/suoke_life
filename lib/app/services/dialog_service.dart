import 'package:get/get.dart';
import 'package:flutter/material.dart';
import '../core/storage/storage_service.dart';
import 'logging_service.dart';

class DialogService extends GetxService {
  final StorageService _storageService = Get.find();
  final LoggingService _loggingService = Get.find();

  final dialogHistory = <Map<String, dynamic>>[].obs;
  final isDialogVisible = false.obs;

  // 显示提示对话框
  Future<bool?> showAlert({
    required String title,
    required String message,
    String? confirmText,
    String? cancelText,
    bool barrierDismissible = true,
  }) async {
    try {
      isDialogVisible.value = true;

      final result = await Get.dialog<bool>(
        AlertDialog(
          title: Text(title),
          content: Text(message),
          actions: [
            if (cancelText != null)
              TextButton(
                onPressed: () => Get.back(result: false),
                child: Text(cancelText),
              ),
            TextButton(
              onPressed: () => Get.back(result: true),
              child: Text(confirmText ?? '确定'),
            ),
          ],
        ),
        barrierDismissible: barrierDismissible,
      );

      await _recordDialog({
        'type': 'alert',
        'title': title,
        'message': message,
        'result': result,
      });

      return result;
    } catch (e) {
      await _loggingService.log('error', 'Failed to show alert dialog', data: {'title': title, 'error': e.toString()});
      return null;
    } finally {
      isDialogVisible.value = false;
    }
  }

  // 显示输入对话框
  Future<String?> showPrompt({
    required String title,
    String? message,
    String? initialValue,
    String? confirmText,
    String? cancelText,
    bool barrierDismissible = true,
  }) async {
    try {
      isDialogVisible.value = true;
      final controller = TextEditingController(text: initialValue);

      final result = await Get.dialog<String>(
        AlertDialog(
          title: Text(title),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              if (message != null) Text(message),
              TextField(controller: controller),
            ],
          ),
          actions: [
            if (cancelText != null)
              TextButton(
                onPressed: () => Get.back(),
                child: Text(cancelText),
              ),
            TextButton(
              onPressed: () => Get.back(result: controller.text),
              child: Text(confirmText ?? '确定'),
            ),
          ],
        ),
        barrierDismissible: barrierDismissible,
      );

      await _recordDialog({
        'type': 'prompt',
        'title': title,
        'message': message,
        'initial_value': initialValue,
        'result': result,
      });

      return result;
    } catch (e) {
      await _loggingService.log('error', 'Failed to show prompt dialog', data: {'title': title, 'error': e.toString()});
      return null;
    } finally {
      isDialogVisible.value = false;
    }
  }

  // 显示自定义对话框
  Future<T?> showCustomDialog<T>({
    required Widget child,
    bool barrierDismissible = true,
    String? name,
  }) async {
    try {
      isDialogVisible.value = true;

      final result = await Get.dialog<T>(
        Dialog(child: child),
        barrierDismissible: barrierDismissible,
      );

      await _recordDialog({
        'type': 'custom',
        'name': name,
        'result': result?.toString(),
      });

      return result;
    } catch (e) {
      await _loggingService.log('error', 'Failed to show custom dialog', data: {'name': name, 'error': e.toString()});
      return null;
    } finally {
      isDialogVisible.value = false;
    }
  }

  // 显示底部菜单
  Future<T?> showBottomSheet<T>({
    required Widget child,
    bool isDismissible = true,
    bool enableDrag = true,
    String? name,
  }) async {
    try {
      isDialogVisible.value = true;

      final result = await Get.bottomSheet<T>(
        child,
        isDismissible: isDismissible,
        enableDrag: enableDrag,
      );

      await _recordDialog({
        'type': 'bottom_sheet',
        'name': name,
        'result': result?.toString(),
      });

      return result;
    } catch (e) {
      await _loggingService.log('error', 'Failed to show bottom sheet', data: {'name': name, 'error': e.toString()});
      return null;
    } finally {
      isDialogVisible.value = false;
    }
  }

  // 获取对话框历史
  Future<List<Map<String, dynamic>>> getDialogHistory({
    String? type,
    DateTime? startDate,
    DateTime? endDate,
  }) async {
    try {
      var history = dialogHistory.toList();

      if (type != null) {
        history = history.where((record) => record['type'] == type).toList();
      }

      if (startDate != null || endDate != null) {
        history = history.where((record) {
          final timestamp = DateTime.parse(record['timestamp']);
          if (startDate != null && timestamp.isBefore(startDate)) return false;
          if (endDate != null && timestamp.isAfter(endDate)) return false;
          return true;
        }).toList();
      }

      return history;
    } catch (e) {
      await _loggingService.log('error', 'Failed to get dialog history', data: {'error': e.toString()});
      return [];
    }
  }

  Future<void> _loadDialogHistory() async {
    try {
      final history = await _storageService.getLocal('dialog_history');
      if (history != null) {
        dialogHistory.value = List<Map<String, dynamic>>.from(history);
      }
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _saveDialogHistory() async {
    try {
      await _storageService.saveLocal('dialog_history', dialogHistory);
    } catch (e) {
      rethrow;
    }
  }

  Future<void> _recordDialog(Map<String, dynamic> dialog) async {
    try {
      final record = {
        ...dialog,
        'timestamp': DateTime.now().toIso8601String(),
      };

      dialogHistory.insert(0, record);
      
      // 只保留最近1000条记录
      if (dialogHistory.length > 1000) {
        dialogHistory.removeRange(1000, dialogHistory.length);
      }
      
      await _saveDialogHistory();
    } catch (e) {
      rethrow;
    }
  }
} 
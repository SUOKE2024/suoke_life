import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:intl/intl.dart';
import '../../../models/message.dart';
import '../../../services/storage/chat_storage_service.dart';

class AIChatHistoryController extends GetxController {
  final ChatStorageService _storageService;
  
  final messages = <Message>[].obs;
  final isLoading = false.obs;
  final selectedDate = Rx<DateTime?>(null);

  AIChatHistoryController(this._storageService);

  @override
  void onInit() {
    super.onInit();
    loadMessages();
  }

  Future<void> loadMessages() async {
    try {
      isLoading.value = true;
      final history = await _storageService.getMessages(
        date: selectedDate.value,
      );
      messages.value = history;
    } catch (e) {
      Get.snackbar('错误', '加载历史记录失败: $e');
    } finally {
      isLoading.value = false;
    }
  }

  Future<void> deleteMessage(String messageId) async {
    try {
      await _storageService.deleteMessage(messageId);
      messages.removeWhere((m) => m.id == messageId);
      Get.snackbar('成功', '已删除消息');
    } catch (e) {
      Get.snackbar('错误', '删除消息失败: $e');
    }
  }

  Future<void> showDatePicker() async {
    final date = await Get.dialog<DateTime>(
      DatePickerDialog(
        initialDate: selectedDate.value ?? DateTime.now(),
        firstDate: DateTime(2020),
        lastDate: DateTime.now(),
      ),
    );

    if (date != null) {
      selectedDate.value = date;
      await loadMessages();
    }
  }

  void clearDateFilter() {
    selectedDate.value = null;
    loadMessages();
  }

  String formatDate(DateTime date) {
    return DateFormat('yyyy年MM月dd日').format(date);
  }

  void showClearHistoryDialog() {
    Get.dialog(
      AlertDialog(
        title: Text('清空历史记录'),
        content: Text('确定要清空所有对话历史记录吗？此操作不可恢复。'),
        actions: [
          TextButton(
            child: Text('取消'),
            onPressed: () => Get.back(),
          ),
          TextButton(
            child: Text('确定'),
            onPressed: () async {
              Get.back();
              try {
                await _storageService.clearMessages();
                messages.clear();
                Get.snackbar('成功', '已清空历史记录');
              } catch (e) {
                Get.snackbar('错误', '清空历史记录失败: $e');
              }
            },
          ),
        ],
      ),
    );
  }
} 
import 'package:get/get.dart';
import 'package:flutter/material.dart';
import 'package:suoke_life/models/message.dart';
import 'package:suoke_life/services/storage/chat_storage_service.dart';

class ChatHistoryController extends GetxController {
  final ChatStorageService _storageService;
  final messages = <Message>[].obs;
  final isLoading = false.obs;
  final selectedDate = Rx<DateTime?>(null);

  String get chatAvatar => Get.parameters['avatar'] ?? 'default_avatar.png';

  ChatHistoryController(this._storageService);

  @override
  void onInit() {
    super.onInit();
    loadMessages();
  }

  Future<void> loadMessages() async {
    try {
      isLoading.value = true;
      final storedMessages = await _storageService.getMessages();
      
      if (selectedDate.value != null) {
        // 按日期筛选
        messages.value = storedMessages.where((msg) {
          final msgDate = msg.timestamp;
          return msgDate.year == selectedDate.value!.year &&
                 msgDate.month == selectedDate.value!.month &&
                 msgDate.day == selectedDate.value!.day;
        }).toList();
      } else {
        messages.assignAll(storedMessages);
      }
    } finally {
      isLoading.value = false;
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
} 
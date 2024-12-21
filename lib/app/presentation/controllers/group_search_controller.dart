import 'package:flutter/material.dart';
import 'package:get/get.dart';
import '../../core/base/base_controller.dart';
import '../../services/group_message_service.dart';
import '../../data/models/message.dart';
import 'dart:async';

class GroupSearchController extends BaseController {
  final _messageService = Get.find<GroupMessageService>();
  final String groupId;

  final searchController = TextEditingController();
  final showFilter = false.obs;
  final isLoading = false.obs;
  final searchResults = <Message>[].obs;

  // 搜索过滤器
  final searchText = true.obs;
  final searchImage = false.obs;
  final searchFile = false.obs;
  final timeRange = 'all'.obs;

  Timer? _debounce;

  GroupSearchController({required this.groupId});

  @override
  void onInit() {
    super.onInit();
    searchController.addListener(_onSearchChanged);
  }

  @override
  void onClose() {
    searchController.dispose();
    _debounce?.cancel();
    super.onClose();
  }

  void onSearchChanged(String value) {
    if (_debounce?.isActive ?? false) _debounce!.cancel();
    _debounce = Timer(const Duration(milliseconds: 500), () {
      _performSearch();
    });
  }

  void showFilterOptions() {
    showFilter.value = !showFilter.value;
  }

  void toggleSearchText(bool value) {
    searchText.value = value;
    _performSearch();
  }

  void toggleSearchImage(bool value) {
    searchImage.value = value;
    _performSearch();
  }

  void toggleSearchFile(bool value) {
    searchFile.value = value;
    _performSearch();
  }

  void setTimeRange(String? value) {
    if (value != null) {
      timeRange.value = value;
      _performSearch();
    }
  }

  Future<void> _performSearch() async {
    if (searchController.text.isEmpty) {
      searchResults.clear();
      return;
    }

    try {
      isLoading.value = true;

      // 构建搜索条件
      final types = <String>[];
      if (searchText.value) types.add('text');
      if (searchImage.value) types.add('image');
      if (searchFile.value) types.add('file');

      DateTime? startTime;
      switch (timeRange.value) {
        case 'today':
          startTime = DateTime.now().subtract(const Duration(days: 1));
          break;
        case 'week':
          startTime = DateTime.now().subtract(const Duration(days: 7));
          break;
        case 'month':
          startTime = DateTime.now().subtract(const Duration(days: 30));
          break;
      }

      final results = await _messageService.searchMessages(
        groupId,
        searchController.text,
        types: types,
        startTime: startTime,
      );

      searchResults.value = results;
    } catch (e) {
      showError('搜索失败');
    } finally {
      isLoading.value = false;
    }
  }

  void onMessageTap(Message message) {
    // 跳转到消息位置
    Get.toNamed(
      '/chat/detail/${message.chatId}',
      arguments: {'scrollToMessage': message},
    );
  }
} 
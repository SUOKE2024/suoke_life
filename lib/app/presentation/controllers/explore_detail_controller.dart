import 'package:flutter/material.dart';
import 'package:get/get.dart';
import 'package:intl/intl.dart';
import '../../data/models/explore_item.dart';
import '../../routes/app_routes.dart';

class ExploreDetailController extends GetxController {
  final item = ExploreItem(
    id: '',
    title: '',
    description: '',
    imageUrl: '',
    type: '',
    publishDate: DateTime.now(),
  ).obs;
  
  final content = ''.obs;
  final isLoading = true.obs;
  final isFavorite = false.obs;
  
  @override
  void onInit() {
    super.onInit();
    if (Get.arguments is ExploreItem) {
      item.value = Get.arguments as ExploreItem;
      _loadContent();
    }
  }
  
  Future<void> _loadContent() async {
    isLoading.value = true;
    try {
      // TODO: 从服务器加载内容
      await Future.delayed(const Duration(seconds: 1));
      content.value = '''
# ${item.value.title}

${item.value.description}

## 主要内容

这里是详细内容...
''';
    } finally {
      isLoading.value = false;
    }
  }
  
  IconData getTypeIcon() {
    switch (item.value.type) {
      case 'article':
        return Icons.article_outlined;
      case 'video':
        return Icons.video_library_outlined;
      case 'course':
        return Icons.school_outlined;
      case 'tool':
        return Icons.build_outlined;
      default:
        return Icons.help_outline;
    }
  }
  
  String getPublishDate() {
    return DateFormat('yyyy-MM-dd').format(item.value.publishDate);
  }
  
  void toggleFavorite() {
    isFavorite.value = !isFavorite.value;
    // TODO: 保存收藏状态
  }
  
  void shareItem() {
    // TODO: 实现分享功能
  }
  
  void showAIAssistant() {
    Get.toNamed(AppRoutes.AI_CHAT, arguments: {
      'type': 'explore_detail',
      'assistant': 'lao_ke',
      'item': item.value,
    });
  }
} 
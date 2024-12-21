import 'package:get/get.dart';
import 'package:suoke_life/data/models/life_record.dart';

class RecordDetailController extends GetxController {
  late final LifeRecord record;
  
  @override
  void onInit() {
    super.onInit();
    record = Get.arguments as LifeRecord;
  }

  // 分享记录
  void shareRecord() {
    // TODO: 实现分享功能
    Get.snackbar('提示', '分享功能开发中');
  }

  // 删除记录
  void deleteRecord() {
    Get.dialog(
      AlertDialog(
        title: Text('确认删除'),
        content: Text('确定要删除这条记录吗？'),
        actions: [
          TextButton(
            onPressed: () => Get.back(),
            child: Text('取消'),
          ),
          TextButton(
            onPressed: () {
              Get.back();
              Get.back(result: 'deleted');
            },
            child: Text('删除', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }

  // AI分析
  void analyzeWithAI() {
    Get.toNamed(
      AppRoutes.AI_CHAT,
      arguments: {
        'assistant': 'xiao_ke',
        'context': record.content,
      },
    );
  }
} 
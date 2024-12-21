import 'package:get/get.dart';
import '../../data/models/network_connection_record.dart';
import '../../core/services/storage_service.dart';

class NetworkHistoryController extends GetxController {
  final _storage = Get.find<StorageService>();
  
  final records = <NetworkConnectionRecord>[].obs;
  final isLoading = false.obs;
  final currentFilter = '全部'.obs;

  @override
  void onInit() {
    super.onInit();
    loadRecords();
  }

  Future<void> loadRecords() async {
    try {
      isLoading.value = true;
      // TODO: 从存储加载历史记录
      await Future.delayed(const Duration(seconds: 1));
      
      // 模拟数据
      records.value = [
        NetworkConnectionRecord(
          id: '1',
          timestamp: DateTime.now().subtract(const Duration(minutes: 30)),
          type: 'WiFi',
          isConnected: true,
        ),
        NetworkConnectionRecord(
          id: '2',
          timestamp: DateTime.now().subtract(const Duration(hours: 2)),
          type: '移动网络',
          isConnected: false,
          errorMessage: '信号弱',
        ),
      ];
    } finally {
      isLoading.value = false;
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
                'WiFi',
                '移动网络',
                '连接成功',
                '连接失败',
              ].map((filter) => FilterChip(
                label: Text(filter),
                selected: currentFilter.value == filter,
                onSelected: (selected) {
                  if (selected) {
                    currentFilter.value = filter;
                    // TODO: 应用筛选
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

  void showRecordDetail(NetworkConnectionRecord record) {
    Get.dialog(
      AlertDialog(
        title: const Text('连接详情'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('连接类型: ${record.type}'),
            const SizedBox(height: 8),
            Text('状态: ${record.isConnected ? "已连接" : "未连接"}'),
            if (record.errorMessage != null) ...[
              const SizedBox(height: 8),
              Text('错误信息: ${record.errorMessage}'),
            ],
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

  Future<void> clearHistory() async {
    final confirmed = await Get.dialog<bool>(
      AlertDialog(
        title: const Text('确认清空'),
        content: const Text('确定要清空所有连接历史记录吗？'),
        actions: [
          TextButton(
            onPressed: () => Get.back(result: false),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () => Get.back(result: true),
            child: const Text('确定'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      // TODO: 清空历史记录
      records.clear();
      Get.snackbar('提示', '历史记录已清空');
    }
  }
} 
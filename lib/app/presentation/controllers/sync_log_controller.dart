import 'package:get/get.dart';
import '../../core/base/base_controller.dart';
import '../../data/models/sync_log.dart';
import '../../data/services/sync_log_storage.dart';
import 'package:share_plus/share_plus.dart';
import 'package:path_provider/path_provider.dart';
import 'dart:io';

class SyncLogController extends BaseController {
  final _logStorage = Get.find<SyncLogStorage>();
  final logs = <SyncLog>[].obs;
  final selectedType = '全部'.obs;
  final selectedDateRange = '全部'.obs;
  final searchText = ''.obs;
  final sortOrder = Rx<SortOrder>(SortOrder.descending);
  final statusFilter = '全部'.obs;
  final stats = Rx<SyncLogStats?>(null);
  
  @override
  void onInit() {
    super.onInit();
    loadLogs();
    loadStats();
  }

  Future<void> loadLogs() async {
    try {
      showLoading();
      final result = await _logStorage.getLogs();
      logs.value = _filterLogs(result);
      hideLoading();
    } catch (e) {
      showError(e.toString());
    }
  }

  Future<void> loadStats() async {
    try {
      stats.value = await _logStorage.getStats();
    } catch (e) {
      print('Failed to load stats: $e');
    }
  }

  Future<void> addLog(SyncLog log) async {
    try {
      await _logStorage.addLog(log);
      logs.insert(0, log);
    } catch (e) {
      print('Failed to add sync log: $e');
    }
  }

  Future<void> clearLogs() async {
    try {
      final confirmed = await Get.dialog<bool>(
        AlertDialog(
          title: const Text('确认清除'),
          content: const Text('确定要清除所有同步日志吗？此操作不可恢复。'),
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
        showLoading();
        await _logStorage.clearLogs();
        logs.clear();
        hideLoading();
        showSuccess('同步日志已清除');
      }
    } catch (e) {
      showError(e.toString());
    }
  }

  Future<void> exportLogs({ExportFormat format = ExportFormat.csv}) async {
    try {
      showLoading();
      
      String filePath;
      String extension;
      String mimeType;
      
      switch (format) {
        case ExportFormat.csv:
          final csv = await _logStorage.exportLogs(format: format);
          filePath = '${(await getTemporaryDirectory()).path}/sync_logs_${DateTime.now().millisecondsSinceEpoch}.csv';
          await File(filePath).writeAsString(csv);
          extension = 'csv';
          mimeType = 'text/csv';
          break;
        case ExportFormat.excel:
          filePath = await _logStorage.exportLogs(format: format);
          extension = 'xlsx';
          mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
          break;
        case ExportFormat.json:
          final json = await _logStorage.exportLogs(format: format);
          filePath = '${(await getTemporaryDirectory()).path}/sync_logs_${DateTime.now().millisecondsSinceEpoch}.json';
          await File(filePath).writeAsString(json);
          extension = 'json';
          mimeType = 'application/json';
          break;
      }
      
      hideLoading();
      
      // 分享文件
      await Share.shareFiles(
        [filePath],
        text: '同步日志导出文件',
        subject: '同步日志.$extension',
        mimeTypes: [mimeType],
      );
    } catch (e) {
      hideLoading();
      showError(e.toString());
    }
  }

  void updateFilter({String? type, String? dateRange}) {
    if (type != null) selectedType.value = type;
    if (dateRange != null) selectedDateRange.value = dateRange;
    logs.value = _filterLogs(logs);
  }

  void updateSearch(String text) {
    searchText.value = text;
    _applyFilters();
  }

  void updateSortOrder(SortOrder order) {
    sortOrder.value = order;
    _applyFilters();
  }

  void updateStatusFilter(String status) {
    statusFilter.value = status;
    _applyFilters();
  }

  void _applyFilters() {
    final allLogs = _logStorage.getLogs();
    logs.value = _filterLogs(allLogs);
  }

  @override
  List<SyncLog> _filterLogs(List<SyncLog> allLogs) {
    var filtered = allLogs;
    
    // 搜索过滤
    if (searchText.value.isNotEmpty) {
      final searchLower = searchText.value.toLowerCase();
      filtered = filtered.where((log) {
        return log.type.toLowerCase().contains(searchLower) ||
               log.status.toLowerCase().contains(searchLower) ||
               log.details.toLowerCase().contains(searchLower);
      }).toList();
    }
    
    // 状态过滤
    if (statusFilter.value != '全部') {
      filtered = filtered.where((log) => log.status == statusFilter.value).toList();
    }
    
    // 类型过滤
    if (selectedType.value != '全部') {
      filtered = filtered.where((log) => log.type == selectedType.value).toList();
    }
    
    // 时间范围过滤
    if (selectedDateRange.value.contains('至')) {
      final dates = selectedDateRange.value.split('至');
      final start = DateTime.parse(dates[0].trim());
      final end = DateTime.parse(dates[1].trim()).add(const Duration(days: 1));
      filtered = filtered.where((log) => 
        log.timestamp.isAfter(start) && log.timestamp.isBefore(end)
      ).toList();
    } else {
      switch (selectedDateRange.value) {
        case '今天':
          final today = DateTime.now().subtract(const Duration(days: 1));
          filtered = filtered.where((log) => log.timestamp.isAfter(today)).toList();
          break;
        case '最近7天':
          final weekAgo = DateTime.now().subtract(const Duration(days: 7));
          filtered = filtered.where((log) => log.timestamp.isAfter(weekAgo)).toList();
          break;
        case '最近30天':
          final monthAgo = DateTime.now().subtract(const Duration(days: 30));
          filtered = filtered.where((log) => log.timestamp.isAfter(monthAgo)).toList();
          break;
      }
    }
    
    // 排序
    filtered.sort((a, b) {
      final comparison = b.timestamp.compareTo(a.timestamp);
      return sortOrder.value == SortOrder.ascending ? -comparison : comparison;
    });
    
    return filtered;
  }

  void showLogDetail(SyncLog log) {
    Get.dialog(
      AlertDialog(
        title: Text('同步详情 - ${log.type}'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text('时间: ${log.timestamp}'),
              const SizedBox(height: 8),
              Text('状态: ${log.status}'),
              const SizedBox(height: 8),
              Text('记录数: ${log.recordCount}'),
              const SizedBox(height: 8),
              Text('详情: ${log.details}'),
            ],
          ),
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

  void showExportOptions() {
    Get.bottomSheet(
      Container(
        color: Theme.of(Get.context!).scaffoldBackgroundColor,
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.table_chart),
              title: const Text('导出为CSV'),
              onTap: () {
                Get.back();
                exportLogs(format: ExportFormat.csv);
              },
            ),
            ListTile(
              leading: const Icon(Icons.grid_on),
              title: const Text('导出为Excel'),
              onTap: () {
                Get.back();
                exportLogs(format: ExportFormat.excel);
              },
            ),
            ListTile(
              leading: const Icon(Icons.code),
              title: const Text('导出为JSON'),
              onTap: () {
                Get.back();
                exportLogs(format: ExportFormat.json);
              },
            ),
          ],
        ),
      ),
    );
  }
}

enum SortOrder {
  ascending,
  descending,
} 
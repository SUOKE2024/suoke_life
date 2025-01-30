import 'package:get/get.dart';

class SyncMessages extends Translations {
  @override
  Map<String, Map<String, String>> get keys => {
    'zh_CN': {
      'sync.status.syncing': '正在同步...',
      'sync.status.success': '同步成功',
      'sync.status.failed': '同步失败',
      'sync.item.life_records': '生活记录',
      'sync.item.tags': '标签管理',
      'sync.item.settings': '应用设置',
      'sync.item.feedback': '反馈记录',
      'sync.error.network': '网络连接失败',
      'sync.error.server': '服务器错误',
      'sync.error.conflict': '数据冲突',
      'sync.error.unknown': '未知错误',
    },
    'en_US': {
      'sync.status.syncing': 'Syncing...',
      'sync.status.success': 'Sync completed',
      'sync.status.failed': 'Sync failed',
      'sync.item.life_records': 'Life Records',
      'sync.item.tags': 'Tags',
      'sync.item.settings': 'Settings',
      'sync.item.feedback': 'Feedback',
      'sync.error.network': 'Network error',
      'sync.error.server': 'Server error',
      'sync.error.conflict': 'Data conflict',
      'sync.error.unknown': 'Unknown error',
    },
  };
} 
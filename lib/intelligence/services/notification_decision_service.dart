import '../../services/models/notification.dart';
import '../../services/services/notification_service.dart';
import '../models/intent.dart';

class NotificationDecisionService {
  final NotificationService _notificationService;

  NotificationDecisionService(this._notificationService);

  Future<void> processAIResponse(String response, Intent intent) async {
    if (response.isEmpty) return;

    // 根据意图进行智能决策
    switch (intent.type) {
      case 'task_completion':
        await _notificationService.addNotification(
          NotificationMessage(
            title: '任务完成',
            body: response,
          ),
        );
        break;
      case 'information':
        await _notificationService.addNotification(
          NotificationMessage(
            title: '信息提示',
            body: response,
          ),
        );
        break;
      case 'warning':
        await _notificationService.addNotification(
          NotificationMessage(
            title: '警告提醒',
            body: response,
          ),
        );
        break;
      default:
        await _notificationService.addNotification(
          NotificationMessage(
            title: 'AI 助手',
            body: response,
          ),
        );
    }
  }

  Future<void> processSystemEvent(String event, String description, double priority) async {
    // 根据优先级和事件类型进行智能决策
    if (priority > 0.8) {
      // 高优先级事件
      await _notificationService.addNotification(
        NotificationMessage(
          title: '重要: $event',
          body: description,
        ),
      );
    } else if (priority > 0.5) {
      // 中等优先级事件
      await _notificationService.addNotification(
        NotificationMessage(
          title: event,
          body: description,
        ),
      );
    } else {
      // 低优先级事件，可能不需要通知
      if (_shouldNotifyLowPriority(event)) {
        await _notificationService.addNotification(
          NotificationMessage(
            title: event,
            body: description,
          ),
        );
      }
    }
  }

  bool _shouldNotifyLowPriority(String event) {
    // 简单的低优先级事件过滤逻辑
    final lowPriorityKeywords = ['更新', '提示', '建议'];
    return !lowPriorityKeywords.any((keyword) => event.contains(keyword));
  }
} 
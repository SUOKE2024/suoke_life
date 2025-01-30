class BackgroundTaskManager {
  static final instance = BackgroundTaskManager._();
  BackgroundTaskManager._();

  final _storage = Get.find<StorageManager>();
  final _eventBus = Get.find<EventBus>();
  
  final _tasks = <String, BackgroundTask>{};
  final _taskQueue = Queue<BackgroundTask>();
  final _runningTasks = <String>{};
  
  bool _isProcessing = false;
  Timer? _processingTimer;

  static const _config = {
    'max_concurrent_tasks': 3,
    'task_timeout': 300000,  // 5分钟
    'retry_delay': 60000,    // 1分钟
    'max_retries': 3,
  };

  Future<void> initialize() async {
    // 恢复未完成的任务
    await _restorePendingTasks();
    
    // 启动任务处理
    _startTaskProcessing();
  }

  Future<void> _restorePendingTasks() async {
    final pendingTasks = await _storage.getObject<List>(
      'pending_tasks',
      (json) => (json['tasks'] as List)
          .map((e) => BackgroundTask.fromJson(e))
          .toList(),
    );

    if (pendingTasks != null) {
      for (final task in pendingTasks) {
        _tasks[task.id] = task;
        if (task.status == TaskStatus.pending) {
          _taskQueue.add(task);
        }
      }
    }
  }

  void _startTaskProcessing() {
    _processingTimer = Timer.periodic(
      const Duration(seconds: 1),
      (_) => _processTasks(),
    );
  }

  Future<void> _processTasks() async {
    if (_isProcessing || _taskQueue.isEmpty) return;
    if (_runningTasks.length >= _config['max_concurrent_tasks']) return;

    _isProcessing = true;
    try {
      while (_taskQueue.isNotEmpty && 
             _runningTasks.length < _config['max_concurrent_tasks']) {
        final task = _taskQueue.removeFirst();
        await _executeTask(task);
      }
    } finally {
      _isProcessing = false;
    }
  }

  Future<void> _executeTask(BackgroundTask task) async {
    if (_runningTasks.contains(task.id)) return;
    
    _runningTasks.add(task.id);
    task.status = TaskStatus.running;
    task.startTime = DateTime.now();
    
    try {
      final result = await task.execute();
      task.complete(result);
      _eventBus.fire(TaskCompletedEvent(task));
    } catch (e) {
      task.fail(e);
      if (task.retryCount < _config['max_retries']) {
        task.retryCount++;
        task.status = TaskStatus.pending;
        _taskQueue.add(task);
        await Future.delayed(Duration(milliseconds: _config['retry_delay']));
      } else {
        _eventBus.fire(TaskFailedEvent(task, e));
      }
    } finally {
      _runningTasks.remove(task.id);
      await _savePendingTasks();
    }
  }

  Future<String> scheduleTask(BackgroundTask task) async {
    _tasks[task.id] = task;
    _taskQueue.add(task);
    await _savePendingTasks();
    _eventBus.fire(TaskScheduledEvent(task));
    return task.id;
  }

  Future<void> cancelTask(String taskId) async {
    final task = _tasks[taskId];
    if (task != null) {
      task.status = TaskStatus.cancelled;
      _taskQueue.removeWhere((t) => t.id == taskId);
      _eventBus.fire(TaskCancelledEvent(task));
      await _savePendingTasks();
    }
  }

  Future<void> _savePendingTasks() async {
    await _storage.setObject('pending_tasks', {
      'tasks': _tasks.values
          .where((t) => t.status != TaskStatus.completed)
          .map((t) => t.toJson())
          .toList(),
    });
  }

  BackgroundTask? getTask(String taskId) => _tasks[taskId];
  
  List<BackgroundTask> getTasksByStatus(TaskStatus status) {
    return _tasks.values.where((t) => t.status == status).toList();
  }

  void dispose() {
    _processingTimer?.cancel();
    _tasks.clear();
    _taskQueue.clear();
    _runningTasks.clear();
  }
}

abstract class BackgroundTask {
  final String id;
  final String type;
  final Map<String, dynamic> params;
  
  TaskStatus status = TaskStatus.pending;
  DateTime? startTime;
  DateTime? endTime;
  dynamic result;
  dynamic error;
  int retryCount = 0;

  BackgroundTask({
    required this.type,
    required this.params,
  }) : id = const Uuid().v4();

  Future<dynamic> execute();

  void complete(dynamic result) {
    this.result = result;
    status = TaskStatus.completed;
    endTime = DateTime.now();
  }

  void fail(dynamic error) {
    this.error = error;
    status = TaskStatus.failed;
    endTime = DateTime.now();
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'type': type,
    'params': params,
    'status': status.toString(),
    'startTime': startTime?.toIso8601String(),
    'endTime': endTime?.toIso8601String(),
    'result': result,
    'error': error?.toString(),
    'retryCount': retryCount,
  };

  factory BackgroundTask.fromJson(Map<String, dynamic> json) {
    // 工厂方法需要根据具体任务类型实现
    throw UnimplementedError();
  }
}

enum TaskStatus {
  pending,
  running,
  completed,
  failed,
  cancelled,
}

// 任务相关事件
class TaskScheduledEvent extends AppEvent {
  final BackgroundTask task;
  TaskScheduledEvent(this.task);
}

class TaskCompletedEvent extends AppEvent {
  final BackgroundTask task;
  TaskCompletedEvent(this.task);
}

class TaskFailedEvent extends AppEvent {
  final BackgroundTask task;
  final dynamic error;
  TaskFailedEvent(this.task, this.error);
}

class TaskCancelledEvent extends AppEvent {
  final BackgroundTask task;
  TaskCancelledEvent(this.task);
} 
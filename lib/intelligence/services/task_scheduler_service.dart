class TaskSchedulerService extends GetxService {
  final EventTrackingService _eventTracking;
  final LogManagerService _logManager;
  
  // 任务队列
  final Queue<AITask> _taskQueue = Queue();
  final Map<String, AITask> _runningTasks = {};
  
  // 任务配置
  static const int _maxConcurrentTasks = 3;
  static const Duration _taskTimeout = Duration(minutes: 5);
  
  TaskSchedulerService({
    required EventTrackingService eventTracking,
    required LogManagerService logManager,
  })  : _eventTracking = eventTracking,
        _logManager = logManager {
    _startTaskProcessor();
  }

  Future<String> scheduleTask(AITask task) async {
    try {
      // 生成任务ID
      final taskId = 'task_${DateTime.now().millisecondsSinceEpoch}';
      task.id = taskId;
      
      // 添加到队列
      _taskQueue.add(task);
      
      // 记录事件
      await _trackTaskEvent(task, 'scheduled');
      
      return taskId;
    } catch (e) {
      await _logManager.log(
        'Task scheduling failed',
        userId: 'system',
        assistantName: 'system',
        level: LogLevel.error,
        metadata: {'error': e.toString()},
      );
      rethrow;
    }
  }

  Future<AITaskStatus> getTaskStatus(String taskId) async {
    // 检查运行中的任务
    if (_runningTasks.containsKey(taskId)) {
      return _runningTasks[taskId]!.status;
    }
    
    // 检查队列中的任务
    final queuedTask = _taskQueue.firstWhere(
      (task) => task.id == taskId,
      orElse: () => AITask(
        type: AITaskType.unknown,
        status: AITaskStatus(
          state: TaskState.notFound,
          message: '任务不存在',
        ),
      ),
    );
    
    return queuedTask.status;
  }

  Future<void> cancelTask(String taskId) async {
    try {
      // 从队列中移除
      _taskQueue.removeWhere((task) => task.id == taskId);
      
      // 取消运行中的任务
      if (_runningTasks.containsKey(taskId)) {
        final task = _runningTasks[taskId]!;
        task.status = AITaskStatus(
          state: TaskState.cancelled,
          message: '任务已取消',
        );
        await _trackTaskEvent(task, 'cancelled');
        _runningTasks.remove(taskId);
      }
    } catch (e) {
      await _logManager.log(
        'Task cancellation failed',
        userId: 'system',
        assistantName: 'system',
        level: LogLevel.error,
        metadata: {
          'task_id': taskId,
          'error': e.toString(),
        },
      );
    }
  }

  void _startTaskProcessor() {
    Timer.periodic(Duration(seconds: 1), (_) async {
      await _processNextTask();
    });
  }

  Future<void> _processNextTask() async {
    if (_taskQueue.isEmpty) return;
    if (_runningTasks.length >= _maxConcurrentTasks) return;
    
    final task = _taskQueue.removeFirst();
    _runningTasks[task.id] = task;
    
    try {
      await _trackTaskEvent(task, 'started');
      
      // 设置超时
      final timeout = Timer(_taskTimeout, () => _handleTaskTimeout(task));
      
      // 执行任务
      await _executeTask(task);
      
      timeout.cancel();
      _runningTasks.remove(task.id);
      
      await _trackTaskEvent(task, 'completed');
    } catch (e) {
      task.status = AITaskStatus(
        state: TaskState.failed,
        message: e.toString(),
      );
      await _trackTaskEvent(task, 'failed', error: e);
      _runningTasks.remove(task.id);
    }
  }

  Future<void> _executeTask(AITask task) async {
    switch (task.type) {
      case AITaskType.dataSync:
        await _executeSyncTask(task);
        break;
      case AITaskType.modelTraining:
        await _executeTrainingTask(task);
        break;
      case AITaskType.dataAnalysis:
        await _executeAnalysisTask(task);
        break;
      default:
        throw AIException(
          '未知的任务类型',
          code: 'UNKNOWN_TASK_TYPE',
        );
    }
  }

  Future<void> _handleTaskTimeout(AITask task) async {
    task.status = AITaskStatus(
      state: TaskState.timeout,
      message: '任务执行超时',
    );
    await _trackTaskEvent(task, 'timeout');
    _runningTasks.remove(task.id);
  }

  Future<void> _trackTaskEvent(
    AITask task,
    String event, {
    dynamic error,
  }) async {
    await _eventTracking.trackEvent(AIEvent(
      id: 'task_${DateTime.now().millisecondsSinceEpoch}',
      userId: 'system',
      assistantName: 'system',
      type: AIEventType.task,
      data: {
        'task_id': task.id,
        'task_type': task.type.toString(),
        'event': event,
        'status': task.status.toMap(),
        'error': error?.toString(),
      },
    ));
  }
} 
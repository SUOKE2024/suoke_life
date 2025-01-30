abstract class AgentService {
  Future<void> performTask(String taskId);
  Future<String> getTaskStatus(String taskId);
}

class AgentServiceImpl implements AgentService {
  @override
  Future<void> performTask(String taskId) async {
    // 实现任务执行逻辑
  }

  @override
  Future<String> getTaskStatus(String taskId) async {
    // 实现获取任务状态逻辑
    return 'completed';
  }
} 
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/di/providers.dart';

/// MCP服务状态小部件
///
/// 显示MCP服务的健康状态
class MCPStatusWidget extends ConsumerWidget {
  const MCPStatusWidget({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final healthStatus = ref.watch(mcpHealthProvider);

    return Card(
      margin: const EdgeInsets.all(8),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(16),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'MCP服务状态',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                healthStatus.when(
                  data: (isHealthy) => Row(
                    children: [
                      Icon(
                        isHealthy ? Icons.check_circle : Icons.error,
                        color: isHealthy ? Colors.green : Colors.red,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        isHealthy ? '服务正常' : '服务异常',
                        style: TextStyle(
                          color: isHealthy ? Colors.green : Colors.red,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  loading: () => const Row(
                    children: [
                      SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          strokeWidth: 2,
                        ),
                      ),
                      SizedBox(width: 8),
                      Text('检查中...'),
                    ],
                  ),
                  error: (error, stack) => Row(
                    children: [
                      const Icon(
                        Icons.error,
                        color: Colors.red,
                      ),
                      const SizedBox(width: 8),
                      Text(
                        '连接失败: ${error.toString().split('\n').first}',
                        style: const TextStyle(
                          color: Colors.red,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            OutlinedButton(
              onPressed: () {
                ref.refresh(mcpHealthProvider);
              },
              child: const Text('刷新状态'),
            ),
          ],
        ),
      ),
    );
  }
} 
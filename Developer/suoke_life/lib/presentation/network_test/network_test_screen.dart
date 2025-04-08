import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/constants/api_constants.dart';
import 'package:suoke_life/core/network/network_tester.dart';
import 'package:suoke_life/core/theme/app_colors.dart';

/// 网络测试页面
class NetworkTestScreen extends ConsumerStatefulWidget {
  /// 创建网络测试页面
  const NetworkTestScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<NetworkTestScreen> createState() => _NetworkTestScreenState();
}

class _NetworkTestScreenState extends ConsumerState<NetworkTestScreen> {
  bool _isLoading = false;
  Map<String, ServerTestResult> _results = {};
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('网络连接测试'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            _buildHeader(),
            const SizedBox(height: 20),
            _buildTestButton(),
            const SizedBox(height: 20),
            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : _buildResultsList(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader() {
    return Card(
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '后端API连接测试',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '基础URL: ${ApiConstants.apiBaseUrl}',
              style: const TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 4),
            const Text(
              '此页面用于测试与后端API的连接状态，点击下方按钮开始测试。',
              style: TextStyle(fontSize: 14),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTestButton() {
    return ElevatedButton.icon(
      onPressed: _isLoading ? null : _runTests,
      icon: const Icon(Icons.network_check),
      label: const Text('开始测试'),
      style: ElevatedButton.styleFrom(
        padding: const EdgeInsets.symmetric(vertical: 12),
      ),
    );
  }

  Widget _buildResultsList() {
    if (_results.isEmpty) {
      return const Center(
        child: Text('尚未运行测试，点击上方按钮开始测试'),
      );
    }

    return ListView.builder(
      itemCount: _results.length,
      itemBuilder: (context, index) {
        final entry = _results.entries.elementAt(index);
        final endpoint = entry.key;
        final result = entry.value;
        
        return _buildResultCard(endpoint, result);
      },
    );
  }

  Widget _buildResultCard(String endpoint, ServerTestResult result) {
    final isSuccess = result.success;
    final statusText = isSuccess ? '成功 (${result.statusCode})' : '失败';
    final statusColor = isSuccess ? Colors.green : Colors.red;
    
    return Card(
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '端点: $endpoint',
              style: const TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 14,
              ),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Text(
                  '状态: $statusText',
                  style: TextStyle(
                    color: statusColor,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(width: 12),
                Text('响应时间: ${result.responseTimeMs}ms'),
              ],
            ),
            const SizedBox(height: 8),
            if (isSuccess)
              Text('数据: ${_formatResponseData(result.data)}')
            else
              Text(
                '错误: ${result.errorMessage}',
                style: const TextStyle(color: Colors.red),
              ),
          ],
        ),
      ),
    );
  }

  String _formatResponseData(dynamic data) {
    if (data == null) return 'null';
    if (data is Map) {
      if (data.isEmpty) return '{}';
      if (data.length > 5) {
        return '{...} (${data.length} 个键)';
      }
      return data.toString();
    }
    if (data is List) {
      if (data.isEmpty) return '[]';
      if (data.length > 5) {
        return '[...] (${data.length} 个项)';
      }
      return data.toString();
    }
    return data.toString();
  }

  Future<void> _runTests() async {
    setState(() {
      _isLoading = true;
      _results = {};
    });
    
    try {
      final networkTester = ref.read(networkTesterProvider);
      
      // 先测试健康端点
      final healthResult = await networkTester.testServerHealth();
      setState(() {
        _results[ApiConstants.connectionTestUrl] = healthResult;
      });
      
      // 如果健康检查成功，测试其他端点
      if (healthResult.success) {
        final endpoints = [
          '${ApiConstants.apiBaseUrl}${ApiConstants.userEndpoint}',
          '${ApiConstants.apiBaseUrl}${ApiConstants.healthDataPath}',
          '${ApiConstants.apiBaseUrl}${ApiConstants.aiEndpoint}',
        ];
        
        for (final endpoint in endpoints) {
          final result = await networkTester.testApiEndpoint(endpoint);
          setState(() {
            _results[endpoint] = result;
          });
        }
      }
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }
} 
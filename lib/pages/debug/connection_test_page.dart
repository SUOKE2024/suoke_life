import 'package:flutter/material.dart';
import '../../core/network/connection_test.dart';
import '../../core/theme/app_colors.dart';

class ConnectionTestPage extends StatefulWidget {
  const ConnectionTestPage({super.key});

  @override
  State<ConnectionTestPage> createState() => _ConnectionTestPageState();
}

class _ConnectionTestPageState extends State<ConnectionTestPage> {
  final ConnectionTest _connectionTest = ConnectionTest();
  Map<String, bool> _testResults = {};
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _runTests();
  }

  Future<void> _runTests() async {
    if (_isLoading) return;
    
    setState(() {
      _isLoading = true;
      _testResults = {};
    });

    try {
      final results = await _connectionTest.runAllTests();
      setState(() {
        _testResults = results;
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('测试过程中发生错误: $e')),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Widget _buildTestItem(String title, bool? result) {
    final icon = result == null
        ? const CircularProgressIndicator()
        : Icon(
            result ? Icons.check_circle : Icons.error,
            color: result ? Colors.green : Colors.red,
          );

    return ListTile(
      leading: SizedBox(
        width: 24,
        height: 24,
        child: icon,
      ),
      title: Text(title),
      subtitle: Text(
        result == null
            ? '测试中...'
            : result
                ? '连接成功'
                : '连接失败',
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('连接测试'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _isLoading ? null : _runTests,
          ),
        ],
      ),
      body: ListView(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Text(
              '连接状态',
              style: Theme.of(context).textTheme.titleLarge,
            ),
          ),
          _buildTestItem(
            'HTTP服务器',
            _testResults['http'],
          ),
          const Divider(),
          _buildTestItem(
            'WebSocket服务器',
            _testResults['websocket'],
          ),
          const Divider(),
          _buildTestItem(
            '数据库',
            _testResults['database'],
          ),
          if (_isLoading)
            const Padding(
              padding: EdgeInsets.all(16.0),
              child: Center(
                child: CircularProgressIndicator(),
              ),
            ),
          const SizedBox(height: 16),
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Text(
              '连接信息',
              style: Theme.of(context).textTheme.titleLarge,
            ),
          ),
          ListTile(
            title: const Text('服务器地址'),
            subtitle: Text(_connectionTest.serverUrl),
          ),
          ListTile(
            title: const Text('WebSocket地址'),
            subtitle: Text(_connectionTest.wsUrl),
          ),
          ListTile(
            title: const Text('数据库地址'),
            subtitle: Text('${_connectionTest.dbHost}:${_connectionTest.dbPort}'),
          ),
        ],
      ),
    );
  }
} 
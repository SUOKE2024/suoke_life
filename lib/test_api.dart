import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'services/doubao_api_service.dart';
import 'dart:convert';

Future<void> main() async {
  await dotenv.load(fileName: '.env');
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: const ApiTestPage(),
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.blue),
      ),
    );
  }
}

class ApiTestPage extends StatefulWidget {
  const ApiTestPage({super.key});

  @override
  State<ApiTestPage> createState() => _ApiTestPageState();
}

class _ApiTestPageState extends State<ApiTestPage> {
  final DoubaoApiService _apiService = DoubaoApiService();
  Map<String, dynamic>? _testResult;
  bool _isLoading = false;

  Future<void> _testConnection() async {
    setState(() {
      _isLoading = true;
      _testResult = null;
    });

    try {
      final result = await _apiService.testConnection();
      setState(() {
        _testResult = result;
      });
    } catch (e) {
      setState(() {
        _testResult = {
          'success': false,
          'error': e.toString(),
          'message': '测试过程发生异常',
        };
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('豆包API测试'),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            ElevatedButton(
              onPressed: _isLoading ? null : _testConnection,
              child: _isLoading
                  ? const SizedBox(
                      width: 20,
                      height: 20,
                      child: CircularProgressIndicator(strokeWidth: 2),
                    )
                  : const Text('测试连接'),
            ),
            const SizedBox(height: 20),
            if (_testResult != null) ...[
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: _testResult!['success'] ? Colors.green[50] : Colors.red[50],
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: _testResult!['success'] ? Colors.green : Colors.red,
                  ),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '状态: ${_testResult!['success'] ? '成功' : '失败'}',
                      style: TextStyle(
                        color: _testResult!['success'] ? Colors.green : Colors.red,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text('消息: ${_testResult!['message']}'),
                    if (_testResult!['error'] != null) ...[
                      const SizedBox(height: 8),
                      Text('错误: ${_testResult!['error']}'),
                    ],
                    if (_testResult!['data'] != null) ...[
                      const SizedBox(height: 8),
                      const Text('响应数据:'),
                      Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: Colors.grey[100],
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: SelectableText(
                          JsonEncoder.withIndent('  ')
                              .convert(_testResult!['data']),
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            fontFamily: 'monospace',
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
} 
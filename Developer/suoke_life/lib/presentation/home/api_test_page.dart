import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/core/constants/api_constants.dart';
import 'package:dio/dio.dart';
import 'package:auto_route/auto_route.dart';

@RoutePage()
class ApiTestPage extends ConsumerStatefulWidget {
  const ApiTestPage({Key? key}) : super(key: key);

  @override
  ConsumerState<ApiTestPage> createState() => _ApiTestPageState();
}

class _ApiTestPageState extends ConsumerState<ApiTestPage> {
  List<ApiTestResult> results = [];
  bool isLoading = false;
  String? errorMessage;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('API测试'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            ElevatedButton(
              onPressed: isLoading ? null : _testApiConnections,
              child: Text(isLoading ? '测试中...' : '测试API连接'),
            ),
            const SizedBox(height: 16),
            
            if (errorMessage != null)
              Card(
                color: Colors.red.shade100,
                child: Padding(
                  padding: const EdgeInsets.all(8.0),
                  child: Text(
                    errorMessage!,
                    style: TextStyle(color: Colors.red.shade800),
                  ),
                ),
              ),
              
            const SizedBox(height: 8),
            
            Text('测试结果:', style: Theme.of(context).textTheme.titleMedium),
            
            const SizedBox(height: 8),
            
            Expanded(
              child: ListView.builder(
                itemCount: results.length,
                itemBuilder: (context, index) {
                  final result = results[index];
                  return Card(
                    color: result.success ? Colors.green.shade100 : Colors.red.shade100,
                    child: Padding(
                      padding: const EdgeInsets.all(12.0),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            '端点: ${result.endpoint}',
                            style: Theme.of(context).textTheme.titleSmall,
                          ),
                          const SizedBox(height: 4),
                          Text('状态: ${result.status ?? "未知"}'),
                          if (result.response != null)
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const SizedBox(height: 4),
                                Text('响应:'),
                                Container(
                                  padding: const EdgeInsets.all(8),
                                  color: Colors.black.withAlpha(20),
                                  child: Text(
                                    result.response!,
                                    style: const TextStyle(fontFamily: 'monospace'),
                                  ),
                                ),
                              ],
                            ),
                          if (result.errorMessage != null)
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const SizedBox(height: 4),
                                Text(
                                  '错误: ${result.errorMessage}',
                                  style: TextStyle(color: Colors.red.shade800),
                                ),
                              ],
                            ),
                        ],
                      ),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  Future<void> _testApiConnections() async {
    setState(() {
      isLoading = true;
      errorMessage = null;
      results = [];
    });

    final dio = Dio();
    dio.options.baseUrl = ApiConstants.baseUrl;
    dio.options.connectTimeout = const Duration(seconds: 10);
    dio.options.receiveTimeout = const Duration(seconds: 10);

    final endpoints = [
      '/health', 
      '/api/auth/health',
      '/api/users/health',
      '/api/users',
      '/api/rag/health'
    ];

    try {
      for (final endpoint in endpoints) {
        try {
          final response = await dio.get(
            endpoint,
            options: Options(
              validateStatus: (status) => true,
              headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
              },
            ),
          );

          setState(() {
            results.add(
              ApiTestResult(
                endpoint: endpoint,
                status: response.statusCode,
                response: response.data is Map 
                    ? response.data.toString() 
                    : response.data is String 
                        ? response.data 
                        : response.data.toString(),
                success: response.statusCode != null && 
                    response.statusCode! >= 200 && 
                    response.statusCode! < 300,
              ),
            );
          });
        } catch (e) {
          setState(() {
            results.add(
              ApiTestResult(
                endpoint: endpoint,
                errorMessage: e is DioException 
                    ? '${e.type}: ${e.message}' 
                    : e.toString(),
                success: false,
              ),
            );
          });
        }
      }
    } catch (e) {
      setState(() {
        errorMessage = '测试过程中出错: ${e.toString()}';
      });
    } finally {
      setState(() {
        isLoading = false;
      });
    }
  }
}

class ApiTestResult {
  final String endpoint;
  final int? status;
  final String? response;
  final String? errorMessage;
  final bool success;

  ApiTestResult({
    required this.endpoint,
    this.status,
    this.response,
    this.errorMessage,
    required this.success,
  });
}
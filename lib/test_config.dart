import 'package:flutter/material.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'core/config/env_config.dart';
import 'core/config/ai_config.dart';

Future<void> main() async {
  // 加载环境变量
  await EnvConfig.load();
  
  // 测试环境变量是否正确加载
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      home: Scaffold(
        appBar: AppBar(
          title: const Text('环境配置测试'),
        ),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text('豆包API密钥: ${AIConfig.doubaoApiKey}'),
              const SizedBox(height: 20),
              Text('小艾模型ID: ${AIConfig.xiaoiModelId}'),
              Text('老克模型ID: ${AIConfig.laokeModelId}'),
              Text('嵌入模型ID: ${AIConfig.embeddingModelId}'),
              const SizedBox(height: 20),
              Text('AI服务地址: ${AIConfig.aiServiceHost}:${AIConfig.aiServicePort}'),
              const SizedBox(height: 20),
              Text('最大并发请求: ${AIConfig.maxConcurrentRequests}'),
              Text('请求超时时间: ${AIConfig.requestTimeout}ms'),
            ],
          ),
        ),
      ),
    );
  }
} 
import 'package:flutter/material.dart';
import '../../core/routes/route_lifecycle.dart';

class ExamplePage extends StatefulWidget {
  const ExamplePage({super.key});

  @override
  State<ExamplePage> createState() => _ExamplePageState();
}

class _ExamplePageState extends BasePageState<ExamplePage> {
  int _counter = 0;
  
  @override
  Future<void> onPagePreBuild() async {
    // 在页面构建前加载数据
    await Future.delayed(const Duration(seconds: 1));
  }
  
  @override
  void onPageFirstBuild() {
    super.onPageFirstBuild();
    // 页面首次构建完成后的初始化工作
    print('页面首次构建完成');
  }
  
  @override
  void onPageStart() {
    super.onPageStart();
    // 页面开始时的处理
    print('页面开始');
  }
  
  @override
  void onPageEnd() {
    // 页面结束时的清理工作
    print('页面结束');
    super.onPageEnd();
  }
  
  @override
  void onPageResume() {
    super.onPageResume();
    // 页面恢复时的处理
    print('页面恢复');
  }
  
  @override
  void onPagePause() {
    super.onPagePause();
    // 页面暂停时的处理
    print('页面暂停');
  }
  
  @override
  void onPageRebuild() {
    super.onPageRebuild();
    // 页面重建时的处理
    print('页面重建');
  }
  
  void _incrementCounter() {
    setState(() {
      _counter++;
      if (_counter == 5) {
        // 模拟错误
        throw Exception('计数达到5时触发的测试错误');
      }
    });
  }
  
  @override
  Widget buildPage(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('生命周期示例'),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text(
              '你已经点击了这么多次:',
            ),
            Text(
              '$_counter',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const ExamplePage(),
                  ),
                );
              },
              child: const Text('打开新页面'),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _incrementCounter,
        tooltip: '增加',
        child: const Icon(Icons.add),
      ),
    );
  }
} 
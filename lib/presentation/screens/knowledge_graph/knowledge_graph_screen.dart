import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/router/app_router.gr.dart';

/// 知识图谱页面
/// 展示健康养生领域的知识网络，使用节点和边表示知识之间的关联
@RoutePage()
class KnowledgeGraphScreen extends ConsumerWidget {
  const KnowledgeGraphScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("知识图谱"),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Text(
              "知识图谱功能即将推出",
              style: TextStyle(fontSize: 18),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                // 导航到知识详情页面（示例）
                context.router.push(
                  KnowledgeDetailRoute(
                    nodeId: "中医养生",
                    nodeType: "理论",
                    nodeDescription: "中医养生是中医学的重要组成部分，是研究如何调养生命、增强体质、预防疾病、延年益寿的一门学问。",
                  ),
                );
              },
              child: const Text("查看示例知识节点"),
            ),
          ],
        ),
      ),
    );
  }
} 

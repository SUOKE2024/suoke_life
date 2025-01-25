import 'package:flutter/material.dart';
import 'package:auto_route/auto_route.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import '../../blocs/explore/knowledge_graph_bloc.dart';

@RoutePage()
class KnowledgeGraphPage extends StatelessWidget {
  const KnowledgeGraphPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (context) => context.read<KnowledgeGraphBloc>()
        ..add(const KnowledgeGraphEvent.started()),
      child: Scaffold(
        appBar: AppBar(
          title: const Text('知识图谱'),
          actions: [
            IconButton(
              icon: const Icon(Icons.filter_list),
              onPressed: () {
                // 显示筛选选项
              },
            ),
          ],
        ),
        body: BlocBuilder<KnowledgeGraphBloc, KnowledgeGraphState>(
          builder: (context, state) {
            return state.when(
              initial: () => const Center(child: Text('加载中...')),
              loading: () => const Center(child: CircularProgressIndicator()),
              loaded: (data) => CustomPaint(
                painter: GraphPainter(data),
                child: GestureDetector(
                  onScaleStart: (details) {
                    // 处理缩放开始
                  },
                  onScaleUpdate: (details) {
                    // 处理缩放更新
                  },
                  onTapDown: (details) {
                    // 处理点击节点
                  },
                ),
              ),
              error: (message) => Center(child: Text('错误: $message')),
            );
          },
        ),
        floatingActionButton: FloatingActionButton(
          onPressed: () {
            // 重置视图
          },
          child: const Icon(Icons.refresh),
        ),
      ),
    );
  }
}

class GraphPainter extends CustomPainter {
  final GraphData data;

  GraphPainter(this.data);

  @override
  void paint(Canvas canvas, Size size) {
    // 实现图谱绘制逻辑
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
} 
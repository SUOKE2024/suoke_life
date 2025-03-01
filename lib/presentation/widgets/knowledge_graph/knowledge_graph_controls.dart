import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../presentation/providers/knowledge_graph_providers.dart';
import '../../../core/theme/app_colors.dart';

class KnowledgeGraphControls extends ConsumerWidget {
  const KnowledgeGraphControls({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final controller = ref.watch(knowledgeGraphControllerProvider);
    final zoomLevel = ref.watch(knowledgeGraphZoomLevelProvider);
    
    // 监听主题列表
    final topics = ['中医养生', '健康饮食', '运动健身', '情绪管理', '慢性病防治'];
    // 过滤器类型
    final filters = ['全部', '疾病', '症状', '治疗方法', '养生方法', '药物'];
    
    return Column(
      children: [
        // 主题选择器
        Container(
          height: 50,
          padding: const EdgeInsets.symmetric(horizontal: 16),
          decoration: BoxDecoration(
            color: Theme.of(context).cardColor,
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.05),
                blurRadius: 3,
                offset: const Offset(0, 1),
              ),
            ],
          ),
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: topics.length,
            separatorBuilder: (context, index) => const SizedBox(width: 16),
            itemBuilder: (context, index) {
              final topic = topics[index];
              final isSelected = topic == controller.selectedTopic;
              
              return GestureDetector(
                onTap: () {
                  ref.read(knowledgeGraphControllerProvider.notifier).selectTopic(topic);
                },
                child: Center(
                  child: AnimatedContainer(
                    duration: const Duration(milliseconds: 200),
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                    decoration: BoxDecoration(
                      color: isSelected
                          ? AppColors.primaryColor
                          : Colors.transparent,
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Text(
                      topic,
                      style: TextStyle(
                        color: isSelected ? Colors.white : null,
                        fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                      ),
                    ),
                  ),
                ),
              );
            },
          ),
        ),
        
        // 过滤器选择器
        Container(
          height: 40,
          padding: const EdgeInsets.symmetric(horizontal: 16),
          decoration: BoxDecoration(
            color: Theme.of(context).scaffoldBackgroundColor,
            border: Border(
              bottom: BorderSide(
                color: Colors.grey.withOpacity(0.2),
                width: 1,
              ),
            ),
          ),
          child: ListView.separated(
            scrollDirection: Axis.horizontal,
            itemCount: filters.length,
            separatorBuilder: (context, index) => const SizedBox(width: 16),
            itemBuilder: (context, index) {
              final filter = filters[index];
              final isSelected = filter == controller.filter;
              
              return GestureDetector(
                onTap: () {
                  ref.read(knowledgeGraphControllerProvider.notifier).setFilter(filter);
                },
                child: Center(
                  child: Text(
                    filter,
                    style: TextStyle(
                      color: isSelected ? AppColors.primaryColor : Colors.grey,
                      fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                      fontSize: 13,
                    ),
                  ),
                ),
              );
            },
          ),
        ),
        
        // 缩放控制器
        Container(
          height: 40,
          padding: const EdgeInsets.symmetric(horizontal: 16),
          decoration: BoxDecoration(
            color: Theme.of(context).scaffoldBackgroundColor,
            border: Border(
              bottom: BorderSide(
                color: Colors.grey.withOpacity(0.2),
                width: 1,
              ),
            ),
          ),
          child: Row(
            children: [
              IconButton(
                icon: const Icon(Icons.zoom_out, size: 18),
                padding: EdgeInsets.zero,
                constraints: const BoxConstraints(),
                onPressed: () {
                  ref.read(knowledgeGraphControllerProvider.notifier)
                     .setZoomLevel(zoomLevel - 0.1);
                },
              ),
              Expanded(
                child: Slider(
                  value: zoomLevel,
                  min: 0.5,
                  max: 2.0,
                  divisions: 15,
                  label: zoomLevel.toStringAsFixed(1),
                  onChanged: (value) {
                    ref.read(knowledgeGraphControllerProvider.notifier)
                       .setZoomLevel(value);
                  },
                ),
              ),
              IconButton(
                icon: const Icon(Icons.zoom_in, size: 18),
                padding: EdgeInsets.zero,
                constraints: const BoxConstraints(),
                onPressed: () {
                  ref.read(knowledgeGraphControllerProvider.notifier)
                     .setZoomLevel(zoomLevel + 0.1);
                },
              ),
            ],
          ),
        ),
      ],
    );
  }
} 
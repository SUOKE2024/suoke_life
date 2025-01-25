import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:get/get.dart';
import '../../controllers/health_advice_detail_controller.dart';
import '../../../data/models/health_advice.dart';
import 'package:share_plus/share_plus.dart';
import '../../../services/health_advice_service.dart';

class AdviceDetailPage extends StatelessWidget {
  const AdviceDetailPage({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('健康建议详情'),
        centerTitle: true,
        elevation: 0.5,
        backgroundColor: Theme.of(context).scaffoldBackgroundColor,
        actions: [
          Obx(() {
            final isFavorite = Get.find<HealthAdviceService>()
                .favorites.contains(controller.advice.value?.id);
            return IconButton(
              icon: Icon(
                isFavorite ? Icons.favorite : Icons.favorite_border,
                color: isFavorite ? Colors.red : Theme.of(context).iconTheme.color,
              ),
              onPressed: () {
                if (controller.advice.value != null) {
                  Get.find<HealthAdviceService>()
                      .toggleFavorite(controller.advice.value!.id);
                }
              },
              tooltip: isFavorite ? '取消收藏' : '收藏',
            );
          }),
          IconButton(
            icon: const Icon(Icons.share),
            onPressed: () {
              final advice = controller.advice.value;
              if (advice != null) {
                Share.share('${advice.title}\n${advice.content}');
              }
            },
            tooltip: '分享',
          ),
        ],
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios),
          onPressed: () => Navigator.pop(),
        ),
        systemOverlayStyle: SystemUiOverlayStyle(
          statusBarColor: Colors.transparent,
          statusBarIconBrightness: Theme.of(context).brightness == Brightness.light 
            ? Brightness.dark 
            : Brightness.light,
        ),
      ),
      body: Obx(() {
        if (controller.isLoading.value) {
          return const Center(child: CircularProgressIndicator());
        }
        if (controller.error.value != null) {
          return Center(
            child: Text(controller.error.value!),
          );
        }
        final advice = controller.advice.value;
        if (advice == null) return const SizedBox();
        
        return SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              _buildHeader(context, advice),
              const SizedBox(height: 16),
              _buildContent(context, advice),
              if (advice.tags.isNotEmpty) ...[
                const SizedBox(height: 16),
                _buildTags(context, advice),
              ],
            ],
          ),
        );
      }),
    );
  }

  Widget _buildHeader(BuildContext context, HealthAdvice advice) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(
                  advice.typeIcon,
                  color: advice.levelColor,
                  size: 32,
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    advice.title,
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                _buildInfoChip(
                  context,
                  '优先级',
                  _getLevelText(advice.level),
                  advice.levelColor,
                ),
                const SizedBox(width: 8),
                _buildInfoChip(
                  context,
                  '类型',
                  _getTypeText(advice.type),
                  Colors.blue,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildContent(BuildContext context, HealthAdvice advice) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '建议内容',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            Text(
              advice.content,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTags(BuildContext context, HealthAdvice advice) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '相关标签',
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: advice.tags.map((tag) {
                return Chip(
                  label: Text(tag),
                  materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                );
              }).toList(),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoChip(
    BuildContext context,
    String label,
    String value,
    Color color,
  ) {
    return Container(
      padding: const EdgeInsets.symmetric(
        horizontal: 12,
        vertical: 6,
      ),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(16),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Text(
            label,
            style: TextStyle(
              color: color,
              fontSize: 12,
            ),
          ),
          const SizedBox(width: 4),
          Text(
            value,
            style: TextStyle(
              color: color,
              fontSize: 12,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  String _getLevelText(AdviceLevel level) {
    switch (level) {
      case AdviceLevel.low:
        return '一般';
      case AdviceLevel.medium:
        return '重要';
      case AdviceLevel.high:
        return '紧急';
      case AdviceLevel.urgent:
        return '非常紧急';
    }
  }

  String _getTypeText(AdviceType type) {
    switch (type) {
      case AdviceType.diet:
        return '饮食';
      case AdviceType.exercise:
        return '运动';
      case AdviceType.sleep:
        return '睡眠';
      case AdviceType.mental:
        return '心理';
      case AdviceType.medical:
        return '医疗';
      case AdviceType.lifestyle:
        return '生活方式';
    }
  }
} 
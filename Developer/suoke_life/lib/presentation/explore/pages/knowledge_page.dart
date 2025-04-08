import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:suoke_life/presentation/common/widgets/custom_app_bar.dart';
import 'package:suoke_life/presentation/explore/widgets/knowledge_list.dart';

/// 知识页面 - 展示老克服务的知识内容
class KnowledgePage extends ConsumerStatefulWidget {
  const KnowledgePage({Key? key}) : super(key: key);

  @override
  ConsumerState<KnowledgePage> createState() => _KnowledgePageState();
}

class _KnowledgePageState extends ConsumerState<KnowledgePage> {
  String? _selectedCategoryId;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const CustomAppBar(
        title: Text('老克知识库'),
      ),
      body: Column(
        children: [
          // 分类选择器
          KnowledgeCategorySelector(
            selectedCategoryId: _selectedCategoryId,
            onCategorySelected: (categoryId) {
              setState(() {
                _selectedCategoryId = categoryId;
              });
            },
          ),
          
          // 知识文章列表
          Expanded(
            child: KnowledgeList(
              categoryId: _selectedCategoryId,
            ),
          ),
        ],
      ),
    );
  }
} 
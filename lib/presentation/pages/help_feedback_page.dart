import 'package:flutter/material.dart';

class HelpFeedbackPage extends StatefulWidget {
  const HelpFeedbackPage({super.key});

  @override
  State<HelpFeedbackPage> createState() => _HelpFeedbackPageState();
}

class _HelpFeedbackPageState extends State<HelpFeedbackPage> {
  final _searchController = TextEditingController();
  final _feedbackController = TextEditingController();
  bool _isLoading = false;

  @override
  void dispose() {
    _searchController.dispose();
    _feedbackController.dispose();
    super.dispose();
  }

  Future<void> _submitFeedback() async {
    if (_feedbackController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请输入反馈内容')),
      );
      return;
    }

    setState(() => _isLoading = true);
    try {
      // TODO: 提交反馈到服务器
      await Future.delayed(const Duration(seconds: 1));
      _feedbackController.clear();
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('感谢您的反馈')),
        );
        Navigator.pop(context);
      }
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return DefaultTabController(
      length: 2,
      child: Scaffold(
        appBar: AppBar(
          title: const Text('帮助与反馈'),
          bottom: const TabBar(
            tabs: [
              Tab(text: '常见问题'),
              Tab(text: '意见反馈'),
            ],
          ),
        ),
        body: TabBarView(
          children: [
            _buildHelpTab(),
            _buildFeedbackTab(),
          ],
        ),
      ),
    );
  }

  Widget _buildHelpTab() {
    return Column(
      children: [
        Padding(
          padding: const EdgeInsets.all(16),
          child: TextField(
            controller: _searchController,
            decoration: InputDecoration(
              hintText: '搜索常见问题',
              prefixIcon: const Icon(Icons.search),
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(24),
              ),
            ),
            onChanged: (value) {
              // TODO: 实现搜索功能
            },
          ),
        ),
        Expanded(
          child: ListView(
            children: [
              _buildHelpSection(
                '账号相关',
                [
                  _HelpItem(
                    question: '如何修改密码？',
                    answer: '您可以在"设置-账号安全-修改密码"中修改您的登录密码。',
                  ),
                  _HelpItem(
                    question: '如何绑定手机号？',
                    answer: '您可以在"设置-账号安全-手机号绑定"中绑定或更换手机号。',
                  ),
                ],
              ),
              _buildHelpSection(
                'AI助理',
                [
                  _HelpItem(
                    question: 'AI助理是如何工作的？',
                    answer: 'AI助理使用先进的人工智能技术，可以理解您的需求并提供个性化的服务。',
                  ),
                  _HelpItem(
                    question: '如何提高AI助理的回答准确度？',
                    answer: '您可以通过更清晰地描述需求，并在对话中提供必要的上下文信息来提高回答的准确度。',
                  ),
                ],
              ),
              _buildHelpSection(
                '功能介绍',
                [
                  _HelpItem(
                    question: '如何使用健康检测功能？',
                    answer: '在首页点击"健康检测"图标，按照提示完成相关操作即可。',
                  ),
                  _HelpItem(
                    question: '如何查看运动记录？',
                    answer: '您可以在"我的-运动记录"中查看您的运动历史数据。',
                  ),
                ],
              ),
            ],
          ),
        ),
      ],
    );
  }

  Widget _buildHelpSection(String title, List<_HelpItem> items) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
          child: Text(
            title,
            style: const TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
        ),
        Container(
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.surface,
            border: Border(
              top: BorderSide(color: Colors.grey[200]!),
              bottom: BorderSide(color: Colors.grey[200]!),
            ),
          ),
          child: Column(
            children: items.map((item) {
              return _buildHelpItemTile(item);
            }).toList(),
          ),
        ),
      ],
    );
  }

  Widget _buildHelpItemTile(_HelpItem item) {
    return Theme(
      data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
      child: ExpansionTile(
        title: Text(item.question),
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
            child: Text(
              item.answer,
              style: TextStyle(
                color: Colors.grey[600],
                height: 1.5,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFeedbackTab() {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text(
          '请描述您遇到的问题或建议',
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
          ),
        ),
        const SizedBox(height: 16),
        TextField(
          controller: _feedbackController,
          maxLines: 5,
          maxLength: 500,
          decoration: const InputDecoration(
            hintText: '请输入您的反馈内容（最多500字）',
            border: OutlineInputBorder(),
          ),
        ),
        const SizedBox(height: 24),
        ElevatedButton(
          onPressed: _isLoading ? null : _submitFeedback,
          child: _isLoading
              ? const SizedBox(
                  height: 20,
                  width: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('提交反馈'),
        ),
        const SizedBox(height: 24),
        Card(
          child: Padding(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  '其他联系方式',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 16),
                _buildContactItem(
                  Icons.email,
                  '邮箱：support@example.com',
                ),
                _buildContactItem(
                  Icons.phone,
                  '电话：400-123-4567',
                ),
                _buildContactItem(
                  Icons.access_time,
                  '工作时间：周一至周五 9:00-18:00',
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildContactItem(IconData icon, String text) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Icon(icon, size: 20, color: Colors.grey[600]),
          const SizedBox(width: 12),
          Text(
            text,
            style: TextStyle(
              color: Colors.grey[600],
            ),
          ),
        ],
      ),
    );
  }
}

class _HelpItem {
  final String question;
  final String answer;

  const _HelpItem({
    required this.question,
    required this.answer,
  });
} 
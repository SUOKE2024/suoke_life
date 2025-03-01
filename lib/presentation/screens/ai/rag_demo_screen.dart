import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:auto_route/auto_route.dart';

import '../../../ai_agents/models/ai_agent.dart';
import '../../../ai_agents/rag/rag_service.dart';
import '../../../core/theme/app_colors.dart';
import '../../widgets/message_bubble.dart';
import '../../../ai_agents/models/rag_result.dart';
import '../../../ai_agents/models/rag_models.dart';
import '../../../ai_agents/rag/rag_provider.dart';

@RoutePage()
class RAGDemoScreen extends ConsumerStatefulWidget {
  const RAGDemoScreen({super.key});

  @override
  ConsumerState<RAGDemoScreen> createState() => _RAGDemoScreenState();
}

class _RAGDemoScreenState extends ConsumerState<RAGDemoScreen> {
  final TextEditingController _queryController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  
  // 当前选中的AI代理
  AIAgent _selectedAgent = AIAgent.xiaoai;
  
  // 检索类型
  RAGRetrievalType _retrievalType = RAGRetrievalType.hybrid;
  
  // 是否使用本地知识库
  bool _useLocalKnowledge = true;
  
  // 消息列表
  final List<Message> _messages = [];
  
  // 加载状态
  bool _isLoading = false;
  
  @override
  void dispose() {
    _queryController.dispose();
    _scrollController.dispose();
    super.dispose();
  }
  
  // 发送消息
  Future<void> _sendMessage() async {
    final query = _queryController.text.trim();
    
    if (query.isEmpty) {
      return;
    }
    
    // 清空输入框
    _queryController.clear();
    
    // 添加用户消息
    setState(() {
      _messages.add(Message(
        content: query,
        isFromUser: true,
        timestamp: DateTime.now(),
      ));
      _isLoading = true;
    });
    
    // 滚动到底部
    _scrollToBottom();
    
    // 获取RAG服务
    final ragService = ref.read(ragServiceProvider);
    
    if (ragService == null) {
      // 服务未初始化，显示错误消息
      setState(() {
        _messages.add(Message(
          content: '抱歉，RAG服务未初始化，无法处理您的请求。',
          isFromUser: false,
          timestamp: DateTime.now(),
          agent: _selectedAgent,
        ));
        _isLoading = false;
      });
      
      _scrollToBottom();
      return;
    }
    
    try {
      // 使用RAG服务生成回复
      final response = await ragService.generateWithRAG(
        query: query,
        agent: _selectedAgent,
        retrievalType: _retrievalType,
        useLocalKnowledge: _useLocalKnowledge,
      );
      
      // 添加AI回复
      setState(() {
        _messages.add(Message(
          content: response,
          isFromUser: false,
          timestamp: DateTime.now(),
          agent: _selectedAgent,
        ));
        _isLoading = false;
      });
      
      _scrollToBottom();
    } catch (e) {
      // 处理错误
      setState(() {
        _messages.add(Message(
          content: '抱歉，发生了一个错误：$e',
          isFromUser: false,
          timestamp: DateTime.now(),
          agent: _selectedAgent,
        ));
        _isLoading = false;
      });
      
      _scrollToBottom();
    }
  }
  
  // 滚动到底部
  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('RAG 知识增强演示'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: _showSettingsDialog,
          ),
        ],
      ),
      body: Column(
        children: [
          // 消息列表
          Expanded(
            child: _messages.isEmpty
                ? _buildEmptyState()
                : _buildMessageList(),
          ),
          
          // 加载指示器
          if (_isLoading)
            const LinearProgressIndicator(),
          
          // 输入区域
          _buildInputArea(),
        ],
      ),
    );
  }
  
  // 构建空状态
  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            Icons.chat_bubble_outline,
            size: 80,
            color: Colors.grey.shade400,
          ),
          const SizedBox(height: 16),
          Text(
            '开始与${_selectedAgent.name}对话吧',
            style: TextStyle(
              fontSize: 18,
              color: Colors.grey.shade600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            '通过RAG技术，${_selectedAgent.name}可以基于知识库回答您的问题',
            style: TextStyle(
              fontSize: 14,
              color: Colors.grey.shade500,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
  
  // 构建消息列表
  Widget _buildMessageList() {
    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.all(16),
      itemCount: _messages.length,
      itemBuilder: (context, index) {
        final message = _messages[index];
        return MessageBubble(
          message: message.content,
          isFromUser: message.isFromUser,
          senderName: message.isFromUser 
              ? '我' 
              : message.agent?.name ?? '系统',
          senderAvatar: message.isFromUser
              ? null
              : message.agent?.avatarUrl,
          timestamp: message.timestamp,
          color: message.isFromUser
              ? Theme.of(context).colorScheme.primary
              : message.agent?.color ?? Colors.grey,
        );
      },
    );
  }
  
  // 构建输入区域
  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 3,
            offset: const Offset(0, -1),
          ),
        ],
      ),
      child: Row(
        children: [
          // 代理选择器
          GestureDetector(
            onTap: _showAgentSelector,
            child: CircleAvatar(
              radius: 20,
              backgroundColor: _selectedAgent.color.withOpacity(0.2),
              child: Text(
                _selectedAgent.name.characters.first,
                style: TextStyle(
                  color: _selectedAgent.color,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ),
          
          const SizedBox(width: 8),
          
          // 输入框
          Expanded(
            child: TextField(
              controller: _queryController,
              decoration: InputDecoration(
                hintText: '输入您的问题...',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(24),
                  borderSide: BorderSide.none,
                ),
                filled: true,
                fillColor: Theme.of(context).brightness == Brightness.light
                    ? Colors.grey.shade100
                    : Colors.grey.shade800,
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 16,
                  vertical: 8,
                ),
              ),
              textInputAction: TextInputAction.send,
              onSubmitted: (_) => _sendMessage(),
            ),
          ),
          
          const SizedBox(width: 8),
          
          // 发送按钮
          MaterialButton(
            onPressed: _sendMessage,
            shape: const CircleBorder(),
            color: AppColors.primaryColor,
            padding: const EdgeInsets.all(12),
            child: const Icon(
              Icons.send,
              color: Colors.white,
              size: 20,
            ),
          ),
        ],
      ),
    );
  }
  
  // 显示代理选择器
  void _showAgentSelector() {
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const ListTile(
              title: Text(
                '选择AI代理',
                style: TextStyle(fontWeight: FontWeight.bold),
              ),
            ),
            
            const Divider(),
            
            ...AIAgent.allAgents.map((agent) {
              return ListTile(
                leading: CircleAvatar(
                  backgroundColor: agent.color.withOpacity(0.2),
                  child: Text(
                    agent.name.characters.first,
                    style: TextStyle(
                      color: agent.color,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                title: Text(agent.name),
                subtitle: Text(
                  agent.description,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
                selected: _selectedAgent.id == agent.id,
                onTap: () {
                  setState(() {
                    _selectedAgent = agent;
                  });
                  Navigator.pop(context);
                },
              );
            }).toList(),
          ],
        );
      },
    );
  }
  
  // 显示设置对话框
  void _showSettingsDialog() {
    showDialog(
      context: context,
      builder: (context) {
        return StatefulBuilder(
          builder: (context, setDialogState) {
            return AlertDialog(
              title: const Text('RAG设置'),
              content: Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 检索类型
                  const Text(
                    '检索类型',
                    style: TextStyle(fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  DropdownButton<RAGRetrievalType>(
                    value: _retrievalType,
                    isExpanded: true,
                    onChanged: (value) {
                      if (value != null) {
                        setDialogState(() {
                          _retrievalType = value;
                        });
                      }
                    },
                    items: RAGRetrievalType.values.map((type) {
                      return DropdownMenuItem(
                        value: type,
                        child: Text(_getRetrievalTypeLabel(type)),
                      );
                    }).toList(),
                  ),
                  
                  const SizedBox(height: 16),
                  
                  // 本地知识库开关
                  Row(
                    children: [
                      const Text(
                        '使用本地知识库',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                      const Spacer(),
                      Switch(
                        value: _useLocalKnowledge,
                        onChanged: (value) {
                          setDialogState(() {
                            _useLocalKnowledge = value;
                          });
                        },
                      ),
                    ],
                  ),
                ],
              ),
              actions: [
                TextButton(
                  onPressed: () {
                    Navigator.pop(context);
                  },
                  child: const Text('确定'),
                ),
              ],
            );
          },
        );
      },
    );
  }
  
  // 获取检索类型标签
  String _getRetrievalTypeLabel(RAGRetrievalType type) {
    switch (type) {
      case RAGRetrievalType.dense:
        return '稠密向量检索';
      case RAGRetrievalType.sparse:
        return '稀疏向量检索';
      case RAGRetrievalType.hybrid:
        return '混合检索';
      case RAGRetrievalType.multiHop:
        return '多跳检索';
    }
  }
}

/// 消息模型
class Message {
  final String content;
  final bool isFromUser;
  final DateTime timestamp;
  final AIAgent? agent;
  
  Message({
    required this.content,
    required this.isFromUser,
    required this.timestamp,
    this.agent,
  });
} 
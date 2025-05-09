import 'package:flutter/material.dart';
import 'package:suoke_life/domain/models/agent_model.dart';

/// 智能体选择回调
typedef AgentSelectionCallback = void Function(AgentType type);

/// 智能体选择器组件
class AgentSelector extends StatelessWidget {
  /// 所有可用的智能体
  final List<Agent> agents;
  
  /// 当前选中的智能体
  final Agent? selectedAgent;
  
  /// 智能体选择回调
  final AgentSelectionCallback onAgentSelected;

  /// 构造函数
  const AgentSelector({
    Key? key,
    required this.agents,
    required this.selectedAgent,
    required this.onAgentSelected,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 100,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 16),
        itemCount: agents.length,
        itemBuilder: (context, index) {
          final agent = agents[index];
          final isSelected = selectedAgent?.id == agent.id;
          
          return _buildAgentCard(context, agent, isSelected);
        },
      ),
    );
  }

  /// 构建智能体卡片
  Widget _buildAgentCard(BuildContext context, Agent agent, bool isSelected) {
    return Padding(
      padding: const EdgeInsets.only(right: 12),
      child: InkWell(
        onTap: () => onAgentSelected(agent.type),
        borderRadius: BorderRadius.circular(12),
        child: Container(
          width: 72,
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: isSelected ? agent.themeColor.withOpacity(0.1) : Colors.transparent,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(
              color: isSelected ? agent.themeColor : Colors.grey.withOpacity(0.3),
              width: isSelected ? 2 : 1,
            ),
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CircleAvatar(
                radius: 24,
                backgroundColor: agent.themeColor.withOpacity(0.2),
                backgroundImage: AssetImage(agent.avatarUrl),
              ),
              const SizedBox(height: 8),
              Text(
                agent.name,
                style: TextStyle(
                  color: isSelected ? agent.themeColor : Theme.of(context).colorScheme.onSurface,
                  fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                  fontSize: 14,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
} 
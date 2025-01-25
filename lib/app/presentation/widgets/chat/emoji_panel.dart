import 'package:flutter/material.dart';
import '../../../core/constants/emojis.dart';

class EmojiPanel extends StatelessWidget {
  final Function(String) onEmojiSelected;

  const EmojiPanel({
    Key? key,
    required this.onEmojiSelected,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 300,
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Theme.of(context).cardColor,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 4,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Column(
        children: [
          // 表情分类标签
          SizedBox(
            height: 40,
            child: ListView(
              scrollDirection: Axis.horizontal,
              children: [
                _buildTabItem('常用', Icons.emoji_emotions_outlined),
                _buildTabItem('表情', Icons.face),
                _buildTabItem('动物', Icons.pets),
                _buildTabItem('食物', Icons.fastfood),
                _buildTabItem('活动', Icons.sports_soccer),
                _buildTabItem('旅行', Icons.flight),
                _buildTabItem('物品', Icons.lightbulb_outline),
                _buildTabItem('符号', Icons.tag),
              ],
            ),
          ),
          const Divider(height: 1),
          // 表情网格
          Expanded(
            child: GridView.builder(
              padding: const EdgeInsets.all(8),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 8,
                childAspectRatio: 1,
              ),
              itemCount: Emojis.frequently.length,
              itemBuilder: (context, index) {
                return GestureDetector(
                  onTap: () => onEmojiSelected(Emojis.frequently[index]),
                  child: Center(
                    child: Text(
                      Emojis.frequently[index],
                      style: const TextStyle(fontSize: 24),
                    ),
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTabItem(String label, IconData icon) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 12),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(icon, size: 20),
          const SizedBox(height: 2),
          Text(label, style: const TextStyle(fontSize: 12)),
        ],
      ),
    );
  }
} 
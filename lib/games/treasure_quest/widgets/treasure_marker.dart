import 'package:flutter/material.dart';
import '../models/treasure.dart';
import '../models/player.dart';

class TreasureMarker extends StatelessWidget {
  final Treasure treasure;
  final double distance;
  final double bearing;
  final Player player;

  const TreasureMarker({
    Key? key,
    required this.treasure,
    required this.distance,
    required this.bearing,
    required this.player,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => _showTreasureInfo(context),
      child: Container(
        padding: const EdgeInsets.all(8),
        decoration: BoxDecoration(
          color: _getMarkerColor().withOpacity(0.8),
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.2),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            // 宝藏图标
            Icon(
              _getTreasureIcon(),
              color: Colors.white,
              size: 32,
            ),

            const SizedBox(height: 4),

            // 距离信息
            Text(
              _formatDistance(distance),
              style: const TextStyle(
                color: Colors.white,
                fontSize: 12,
                fontWeight: FontWeight.bold,
              ),
            ),

            // 稀有度指示器
            Container(
              margin: const EdgeInsets.only(top: 4),
              padding: const EdgeInsets.symmetric(
                horizontal: 6,
                vertical: 2,
              ),
              decoration: BoxDecoration(
                color: _getRarityColor(),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                _formatRarity(treasure.rarity),
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 10,
                  fontWeight: FontWeight.bold,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // 显示宝藏详情
  void _showTreasureInfo(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        padding: const EdgeInsets.all(16),
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(
            top: Radius.circular(20),
          ),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 标题
            Row(
              children: [
                Icon(
                  _getTreasureIcon(),
                  color: _getMarkerColor(),
                  size: 24,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    treasure.name,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 4,
                  ),
                  decoration: BoxDecoration(
                    color: _getRarityColor(),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    _formatRarity(treasure.rarity),
                    style: const TextStyle(
                      color: Colors.white,
                      fontSize: 12,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // 描述
            if (treasure.description != null)
              Text(
                treasure.description!,
                style: const TextStyle(
                  fontSize: 14,
                  color: Colors.black87,
                ),
              ),

            const SizedBox(height: 16),

            // 距离和方向
            Row(
              children: [
                const Icon(
                  Icons.location_on,
                  color: Colors.grey,
                  size: 16,
                ),
                const SizedBox(width: 4),
                Text(
                  '距离: ${_formatDistance(distance)}',
                  style: const TextStyle(
                    fontSize: 14,
                    color: Colors.grey,
                  ),
                ),
                const SizedBox(width: 16),
                const Icon(
                  Icons.navigation,
                  color: Colors.grey,
                  size: 16,
                ),
                const SizedBox(width: 4),
                Text(
                  '方向: ${_formatBearing(bearing)}',
                  style: const TextStyle(
                    fontSize: 14,
                    color: Colors.grey,
                  ),
                ),
              ],
            ),

            const SizedBox(height: 16),

            // 提示信息
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: Colors.grey[100],
                borderRadius: BorderRadius.circular(8),
              ),
              child: Row(
                children: [
                  const Icon(
                    Icons.lightbulb_outline,
                    color: Colors.amber,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      treasure.getHint(player.level),
                      style: const TextStyle(
                        fontSize: 14,
                        color: Colors.black87,
                      ),
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 16),

            // 关闭按钮
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () => Navigator.pop(context),
                style: ElevatedButton.styleFrom(
                  backgroundColor: _getMarkerColor(),
                  padding: const EdgeInsets.symmetric(vertical: 12),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                ),
                child: const Text(
                  '关闭',
                  style: TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // 获取宝藏图标
  IconData _getTreasureIcon() {
    switch (treasure.type) {
      case 'mushroom':
        return Icons.eco;
      case 'product':
        return Icons.card_giftcard;
      case 'special':
        return Icons.stars;
      default:
        return Icons.help_outline;
    }
  }

  // 获取标记颜色
  Color _getMarkerColor() {
    switch (treasure.type) {
      case 'mushroom':
        return Colors.green;
      case 'product':
        return Colors.blue;
      case 'special':
        return Colors.purple;
      default:
        return Colors.grey;
    }
  }

  // 获取稀���度颜色
  Color _getRarityColor() {
    switch (treasure.rarity) {
      case 'common':
        return Colors.grey;
      case 'rare':
        return Colors.blue;
      case 'epic':
        return Colors.purple;
      case 'legendary':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }

  // 格式化距离
  String _formatDistance(double meters) {
    if (meters < 1000) {
      return '${meters.toStringAsFixed(0)}米';
    } else {
      return '${(meters / 1000).toStringAsFixed(1)}千米';
    }
  }

  // 格式化方位角
  String _formatBearing(double bearing) {
    const directions = ['北', '东北', '东', '东南', '南', '西南', '西', '西北'];
    final index = ((bearing + 22.5) % 360 / 45).floor();
    return directions[index];
  }

  // 格式化稀有度
  String _formatRarity(String rarity) {
    switch (rarity) {
      case 'common':
        return '普通';
      case 'rare':
        return '稀有';
      case 'epic':
        return '史诗';
      case 'legendary':
        return '传说';
      default:
        return '未知';
    }
  }
} 
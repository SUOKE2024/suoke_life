import 'package:flutter/material.dart';
import '../models/player.dart';
import '../models/game_config.dart';
import '../services/game_service.dart';

class InventoryScreen extends StatefulWidget {
  final Player player;
  final GameService gameService;

  const InventoryScreen({
    Key? key,
    required this.player,
    required this.gameService,
  }) : super(key: key);

  @override
  State<InventoryScreen> createState() => _InventoryScreenState();
}

class _InventoryScreenState extends State<InventoryScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  String _selectedCategory = 'tools';

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('我的背包'),
        bottom: TabBar(
          controller: _tabController,
          tabs: const [
            Tab(text: '工具'),
            Tab(text: '消耗品'),
            Tab(text: '收藏品'),
          ],
          onTap: (index) {
            setState(() {
              _selectedCategory = ['tools', 'consumables', 'collectibles'][index];
            });
          },
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildToolsGrid(),
          _buildConsumablesGrid(),
          _buildCollectiblesGrid(),
        ],
      ),
    );
  }

  // 构建工具格子
  Widget _buildToolsGrid() {
    final tools = widget.player.inventory.entries
        .where((e) => GameConfig.gameItems['tools']?.containsKey(e.key) ?? false)
        .toList();

    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 1,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
      ),
      itemCount: tools.length,
      itemBuilder: (context, index) {
        final item = tools[index];
        final itemConfig = GameConfig.gameItems['tools']![item.key];
        return _buildItemCard(
          name: itemConfig['name'],
          description: itemConfig['description'],
          durability: itemConfig['durability'],
          accuracy: itemConfig['accuracy'],
          icon: _getToolIcon(item.key),
          onTap: () => _showItemDetails(item.key, 'tools'),
        );
      },
    );
  }

  // 构建消耗品格子
  Widget _buildConsumablesGrid() {
    final consumables = widget.player.inventory.entries
        .where((e) =>
            GameConfig.gameItems['consumables']?.containsKey(e.key) ?? false)
        .toList();

    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 1,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
      ),
      itemCount: consumables.length,
      itemBuilder: (context, index) {
        final item = consumables[index];
        final itemConfig = GameConfig.gameItems['consumables']![item.key];
        return _buildItemCard(
          name: itemConfig['name'],
          description: itemConfig['description'],
          count: item.value is int ? item.value : 1,
          duration: itemConfig['duration'],
          icon: _getConsumableIcon(item.key),
          onTap: () => _showItemDetails(item.key, 'consumables'),
        );
      },
    );
  }

  // 构建收藏品格子
  Widget _buildCollectiblesGrid() {
    final collectibles = widget.player.inventory.entries
        .where((e) => e.key.startsWith('collectible_'))
        .toList();

    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 1,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
      ),
      itemCount: collectibles.length,
      itemBuilder: (context, index) {
        final item = collectibles[index];
        return _buildItemCard(
          name: item.value['name'] ?? '未知物品',
          description: item.value['description'] ?? '神秘的收藏品',
          rarity: item.value['rarity'] ?? 'common',
          icon: Icons.star,
          onTap: () => _showItemDetails(item.key, 'collectibles'),
        );
      },
    );
  }

  // 构建物品卡片
  Widget _buildItemCard({
    required String name,
    required String description,
    required IconData icon,
    int? count,
    int? durability,
    double? accuracy,
    int? duration,
    String? rarity,
    required VoidCallback onTap,
  }) {
    return Card(
      elevation: 4,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(
                icon,
                size: 48,
                color: _getItemColor(rarity),
              ),
              const SizedBox(height: 8),
              Text(
                name,
                style: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 4),
              if (count != null)
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 8,
                    vertical: 2,
                  ),
                  decoration: BoxDecoration(
                    color: Colors.blue.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    '数量: $count',
                    style: const TextStyle(
                      fontSize: 12,
                      color: Colors.blue,
                    ),
                  ),
                ),
              if (durability != null)
                LinearProgressIndicator(
                  value: durability / 100,
                  backgroundColor: Colors.grey[200],
                  valueColor: AlwaysStoppedAnimation<Color>(
                    _getDurabilityColor(durability),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  // 显示物品详情
  void _showItemDetails(String itemId, String category) {
    final item = GameConfig.gameItems[category]?[itemId];
    if (item == null) return;

    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: Colors.transparent,
      builder: (context) => Container(
        height: MediaQuery.of(context).size.height * 0.7,
        decoration: const BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.vertical(
            top: Radius.circular(20),
          ),
        ),
        child: Column(
          children: [
            // 顶部拖动条
            Container(
              margin: const EdgeInsets.symmetric(vertical: 8),
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // 物品标题
                    Row(
                      children: [
                        Icon(
                          _getItemIcon(itemId, category),
                          size: 32,
                          color: _getItemColor(item['rarity']),
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(
                                item['name'],
                                style: const TextStyle(
                                  fontSize: 20,
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                              Text(
                                category == 'tools' ? '工具' : '消耗品',
                                style: TextStyle(
                                  fontSize: 14,
                                  color: Colors.grey[600],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),

                    const SizedBox(height: 24),

                    // 物品描述
                    Text(
                      '描述',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.grey[800],
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      item['description'],
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey[600],
                      ),
                    ),

                    const SizedBox(height: 24),

                    // 物品属性
                    Text(
                      '属性',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Colors.grey[800],
                      ),
                    ),
                    const SizedBox(height: 8),
                    _buildItemProperties(item, category),

                    const SizedBox(height: 24),

                    // 使用按钮
                    if (category == 'consumables')
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton(
                          onPressed: () => _useItem(itemId),
                          style: ElevatedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 12),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(8),
                            ),
                          ),
                          child: const Text('使用'),
                        ),
                      ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  // 构建物品属性
  Widget _buildItemProperties(Map<String, dynamic> item, String category) {
    if (category == 'tools') {
      return Column(
        children: [
          _buildPropertyRow(
            '耐久度',
            '${item['durability']}',
            icon: Icons.build,
          ),
          const SizedBox(height: 8),
          _buildPropertyRow(
            '精确度',
            '${(item['accuracy'] * 100).toStringAsFixed(1)}%',
            icon: Icons.gps_fixed,
          ),
        ],
      );
    } else if (category == 'consumables') {
      return Column(
        children: [
          _buildPropertyRow(
            '持续时间',
            '${item['duration']}秒',
            icon: Icons.timer,
          ),
          const SizedBox(height: 8),
          _buildPropertyRow(
            '数量',
            '${widget.player.inventory[item['id']]}',
            icon: Icons.inventory_2,
          ),
        ],
      );
    }
    return const SizedBox.shrink();
  }

  // 构建属性行
  Widget _buildPropertyRow(String label, String value, {IconData? icon}) {
    return Row(
      children: [
        if (icon != null) ...[
          Icon(
            icon,
            size: 16,
            color: Colors.grey[600],
          ),
          const SizedBox(width: 8),
        ],
        Text(
          label,
          style: TextStyle(
            fontSize: 14,
            color: Colors.grey[600],
          ),
        ),
        const Spacer(),
        Text(
          value,
          style: const TextStyle(
            fontSize: 14,
            fontWeight: FontWeight.bold,
          ),
        ),
      ],
    );
  }

  // 使用物品
  void _useItem(String itemId) {
    if (widget.player.useItem(itemId)) {
      Navigator.pop(context);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('使用成功！'),
          duration: Duration(seconds: 2),
        ),
      );
      setState(() {});
    }
  }

  // 获取工具图标
  IconData _getToolIcon(String toolId) {
    switch (toolId) {
      case 'basic_compass':
        return Icons.explore;
      case 'advanced_detector':
        return Icons.radar;
      case 'master_radar':
        return Icons.satellite_alt;
      default:
        return Icons.build;
    }
  }

  // 获取消耗品图标
  IconData _getConsumableIcon(String itemId) {
    switch (itemId) {
      case 'hint_scroll':
        return Icons.article;
      case 'time_potion':
        return Icons.hourglass_bottom;
      case 'luck_charm':
        return Icons.auto_awesome;
      default:
        return Icons.inventory_2;
    }
  }

  // 获取物品图标
  IconData _getItemIcon(String itemId, String category) {
    if (category == 'tools') {
      return _getToolIcon(itemId);
    } else if (category == 'consumables') {
      return _getConsumableIcon(itemId);
    }
    return Icons.help_outline;
  }

  // 获取物品颜色
  Color _getItemColor(String? rarity) {
    switch (rarity) {
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

  // 获取耐久度颜色
  Color _getDurabilityColor(int durability) {
    if (durability > 70) {
      return Colors.green;
    } else if (durability > 30) {
      return Colors.orange;
    } else {
      return Colors.red;
    }
  }
} 
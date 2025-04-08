import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../widgets/app_dashboard_widget.dart';
import '../../widgets/animated_gradient_card.dart';
import '../../../di/providers/dashboard_providers.dart';

/// 应用桌面主屏幕
class DashboardScreen extends ConsumerStatefulWidget {
  const DashboardScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends ConsumerState<DashboardScreen> {
  bool _isEditMode = false;
  bool _isSearchMode = false;
  String _searchQuery = '';
  final TextEditingController _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _searchController.addListener(() {
      setState(() {
        _searchQuery = _searchController.text;
      });
    });
  }

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  void _toggleEditMode() {
    setState(() {
      _isEditMode = !_isEditMode;
    });
    ref.read(dashboardControllerProvider.notifier).setEditMode(_isEditMode);
  }

  void _toggleSearchMode() {
    setState(() {
      _isSearchMode = !_isSearchMode;
      if (!_isSearchMode) {
        _searchController.clear();
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    final dashboardState = ref.watch(dashboardControllerProvider);
    final theme = Theme.of(context);
    
    return Scaffold(
      appBar: AppBar(
        title: _isSearchMode 
          ? TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: '搜索应用...',
                border: InputBorder.none,
                hintStyle: TextStyle(color: theme.colorScheme.onPrimary.withAlpha(180)),
              ),
              style: TextStyle(color: theme.colorScheme.onPrimary),
              autofocus: true,
            )
          : const Text('应用桌面'),
        actions: [
          IconButton(
            icon: Icon(_isSearchMode ? Icons.close : Icons.search),
            onPressed: _toggleSearchMode,
            tooltip: _isSearchMode ? '取消搜索' : '搜索应用',
          ),
          IconButton(
            icon: Icon(_isEditMode ? Icons.done : Icons.edit),
            onPressed: _toggleEditMode,
            tooltip: _isEditMode ? '完成编辑' : '编辑桌面',
          ),
          PopupMenuButton<String>(
            onSelected: (value) {
              switch (value) {
                case 'reset':
                  _showResetConfirmDialog();
                  break;
                case 'save':
                  _showSaveLayoutDialog();
                  break;
                case 'load':
                  _showLoadLayoutDialog();
                  break;
                case 'settings':
                  _showSettingsDialog();
                  break;
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'reset',
                child: Row(
                  children: [
                    Icon(Icons.restore),
                    SizedBox(width: 8),
                    Text('重置为默认'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'save',
                child: Row(
                  children: [
                    Icon(Icons.save),
                    SizedBox(width: 8),
                    Text('保存当前布局'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'load',
                child: Row(
                  children: [
                    Icon(Icons.folder_open),
                    SizedBox(width: 8),
                    Text('加载已保存布局'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'settings',
                child: Row(
                  children: [
                    Icon(Icons.settings),
                    SizedBox(width: 8),
                    Text('桌面设置'),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: Column(
        children: [
          if (_isEditMode) _buildEditModeToolbar(),
          Expanded(
            child: AppDashboardWidget(
              isEditMode: _isEditMode,
              searchQuery: _isSearchMode ? _searchQuery : null,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEditModeToolbar() {
    return AnimatedGradientCard(
      colors: const [Color(0xFF35BB78), Color(0xFF2E9E67)],
      child: Padding(
        padding: const EdgeInsets.all(8.0),
        child: Row(
          children: [
            const Icon(Icons.info_outline, color: Colors.white),
            const SizedBox(width: 8),
            const Expanded(
              child: Text(
                '编辑模式：拖动小部件调整位置，长按小部件查看更多选项',
                style: TextStyle(color: Colors.white),
              ),
            ),
            TextButton.icon(
              onPressed: () {
                ref.read(dashboardControllerProvider.notifier).loadCategories();
                _showAddWidgetDialog();
              },
              icon: const Icon(Icons.add, color: Colors.white),
              label: const Text('添加', style: TextStyle(color: Colors.white)),
              style: TextButton.styleFrom(
                backgroundColor: Colors.white.withAlpha(50),
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showResetConfirmDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('重置桌面'),
        content: const Text('确定要将桌面重置为默认布局吗？这将删除您所有的自定义设置。'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              ref.read(dashboardControllerProvider.notifier).resetDashboardToDefault();
            },
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }

  void _showSaveLayoutDialog() {
    final TextEditingController nameController = TextEditingController();
    
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('保存布局'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text('为您的布局取个名字，方便以后找到它'),
            const SizedBox(height: 16),
            TextField(
              controller: nameController,
              decoration: const InputDecoration(
                labelText: '布局名称',
                hintText: '例如：工作模式、娱乐模式',
                border: OutlineInputBorder(),
              ),
              autofocus: true,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              if (nameController.text.isNotEmpty) {
                Navigator.of(context).pop();
                final dashboardState = ref.read(dashboardControllerProvider);
                
                dashboardState.dashboard.whenData((dashboard) {
                  ref.read(dashboardControllerProvider.notifier)
                    .saveCustomLayout(nameController.text, dashboard);
                });
                
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('布局 "${nameController.text}" 已保存')),
                );
              }
            },
            child: const Text('保存'),
          ),
        ],
      ),
    );
  }

  void _showLoadLayoutDialog() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.6,
        minChildSize: 0.3,
        maxChildSize: 0.9,
        expand: false,
        builder: (context, scrollController) {
          final savedLayoutsAsync = ref.watch(savedLayoutsProvider);
          
          return savedLayoutsAsync.when(
            data: (layouts) {
              if (layouts.isEmpty) {
                return const Center(
                  child: Text('没有保存的布局'),
                );
              }
              
              return Column(
                children: [
                  Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Row(
                      children: [
                        const Expanded(
                          child: Text(
                            '已保存的布局',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                            ),
                          ),
                        ),
                        IconButton(
                          icon: const Icon(Icons.close),
                          onPressed: () => Navigator.of(context).pop(),
                        ),
                      ],
                    ),
                  ),
                  const Divider(),
                  Expanded(
                    child: ListView.builder(
                      controller: scrollController,
                      itemCount: layouts.length,
                      itemBuilder: (context, index) {
                        final layout = layouts[index];
                        return ListTile(
                          leading: const Icon(Icons.dashboard),
                          title: Text(layout.name),
                          subtitle: Text(
                            '创建于: ${_formatDate(layout.createdAt)}',
                          ),
                          trailing: IconButton(
                            icon: const Icon(Icons.delete_outline),
                            onPressed: () {
                              Navigator.of(context).pop();
                              _showDeleteLayoutConfirmDialog(layout.id, layout.name);
                            },
                          ),
                          onTap: () {
                            Navigator.of(context).pop();
                            ref.read(dashboardControllerProvider.notifier)
                              .loadCustomLayout(layout.id);
                            
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(content: Text('已加载布局 "${layout.name}"')),
                            );
                          },
                        );
                      },
                    ),
                  ),
                ],
              );
            },
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (error, stack) => Center(
              child: Text('加载失败: $error'),
            ),
          );
        },
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.year}/${date.month}/${date.day} ${date.hour}:${date.minute}';
  }

  void _showDeleteLayoutConfirmDialog(String layoutId, String layoutName) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('删除布局'),
        content: Text('确定要删除布局 "$layoutName" 吗？此操作无法撤销。'),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              Navigator.of(context).pop();
              ref.read(dashboardControllerProvider.notifier)
                .deleteCustomLayout(layoutId);
              
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text('布局 "$layoutName" 已删除')),
              );
            },
            child: const Text('删除'),
          ),
        ],
      ),
    );
  }

  void _showAddWidgetDialog() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (context) => DraggableScrollableSheet(
        initialChildSize: 0.6,
        minChildSize: 0.3,
        maxChildSize: 0.9,
        expand: false,
        builder: (context, scrollController) {
          final categoriesAsync = ref.watch(appCategoriesProvider);
          
          return categoriesAsync.when(
            data: (categories) {
              return DefaultTabController(
                length: categories.length,
                child: Column(
                  children: [
                    Padding(
                      padding: const EdgeInsets.all(16.0),
                      child: Row(
                        children: [
                          const Expanded(
                            child: Text(
                              '添加小部件',
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          IconButton(
                            icon: const Icon(Icons.close),
                            onPressed: () => Navigator.of(context).pop(),
                          ),
                        ],
                      ),
                    ),
                    TabBar(
                      tabs: categories.map((c) => Tab(text: c.name)).toList(),
                      isScrollable: true,
                    ),
                    Expanded(
                      child: TabBarView(
                        children: categories.map((category) {
                          return _buildCategoryWidgetsGrid(category.id, scrollController);
                        }).toList(),
                      ),
                    ),
                  ],
                ),
              );
            },
            loading: () => const Center(child: CircularProgressIndicator()),
            error: (error, stack) => Center(
              child: Text('加载失败: $error'),
            ),
          );
        },
      ),
    );
  }

  Widget _buildCategoryWidgetsGrid(String categoryId, ScrollController scrollController) {
    final widgetsAsync = ref.watch(appWidgetsByCategoryProvider(categoryId));
    
    return widgetsAsync.when(
      data: (widgets) {
        if (widgets.isEmpty) {
          return const Center(
            child: Text('该分类下没有可用小部件'),
          );
        }
        
        return GridView.builder(
          controller: scrollController,
          padding: const EdgeInsets.all(16),
          gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
            crossAxisCount: 2,
            childAspectRatio: 1.5,
            crossAxisSpacing: 16,
            mainAxisSpacing: 16,
          ),
          itemCount: widgets.length,
          itemBuilder: (context, index) {
            final widget = widgets[index];
            return GestureDetector(
              onTap: () {
                Navigator.of(context).pop();
                ref.read(dashboardControllerProvider.notifier)
                  .addWidget(widget);
                
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(content: Text('已添加 "${widget.title}" 小部件')),
                );
              },
              child: Card(
                elevation: 2,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(
                      _getIconData(widget.iconName),
                      size: 36,
                      color: Theme.of(context).primaryColor,
                    ),
                    const SizedBox(height: 8),
                    Text(
                      widget.title,
                      style: const TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      widget.description,
                      style: Theme.of(context).textTheme.bodySmall,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      textAlign: TextAlign.center,
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
      loading: () => const Center(child: CircularProgressIndicator()),
      error: (error, stack) => Center(
        child: Text('加载失败: $error'),
      ),
    );
  }

  IconData _getIconData(String iconName) {
    // 简单映射一些常用图标，实际应用中应扩展此函数
    switch (iconName) {
      case 'health': return Icons.favorite;
      case 'tcm': return Icons.healing;
      case 'food': return Icons.restaurant;
      case 'calendar': return Icons.calendar_today;
      case 'weather': return Icons.cloud;
      case 'stats': return Icons.bar_chart;
      case 'shopping': return Icons.shopping_cart;
      case 'chat': return Icons.chat;
      case 'role': return Icons.person;
      case 'points': return Icons.stars;
      default: return Icons.apps;
    }
  }

  void _showSettingsDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('桌面设置'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            SwitchListTile(
              title: const Text('显示推荐小部件'),
              subtitle: const Text('根据您的使用习惯显示推荐小部件'),
              value: true, // 从设置中读取
              onChanged: (value) {
                // 保存设置
              },
            ),
            SwitchListTile(
              title: const Text('小部件自动排列'),
              subtitle: const Text('自动整理桌面小部件布局'),
              value: false, // 从设置中读取
              onChanged: (value) {
                // 保存设置
              },
            ),
            SwitchListTile(
              title: const Text('显示小部件边框'),
              subtitle: const Text('在小部件周围显示边框'),
              value: true, // 从设置中读取
              onChanged: (value) {
                // 保存设置
              },
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: const Text('关闭'),
          ),
        ],
      ),
    );
  }
}

// 添加应用分类Provider
final appWidgetsByCategoryProvider = Provider.family<AsyncValue<List<AppWidget>>, String>((ref, categoryId) {
  final controller = ref.watch(dashboardControllerProvider.notifier);
  final result = controller.getAppWidgetsByCategory(categoryId);
  return result;
});

// 添加保存的布局Provider
final savedLayoutsProvider = Provider<AsyncValue<List<SavedLayout>>>((ref) {
  final controller = ref.watch(dashboardControllerProvider.notifier);
  final result = controller.getSavedLayouts();
  return result;
}); 
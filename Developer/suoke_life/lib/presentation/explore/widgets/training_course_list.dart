import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:auto_route/auto_route.dart';
import 'package:suoke_life/core/router/app_router.dart';
import 'package:suoke_life/di/providers/explore_providers.dart';
import 'package:suoke_life/presentation/common/widgets/error_message.dart';
import 'package:suoke_life/presentation/common/widgets/loading_indicator.dart';

class TrainingCourseList extends ConsumerWidget {
  final String? categoryId;
  final String? level;
  
  const TrainingCourseList({
    Key? key,
    this.categoryId,
    this.level,
  }) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // 监听培训课程列表状态
    final coursesState = ref.watch(trainingCoursesProvider);
    
    // 初始加载或切换分类时重新加载数据
    ref.listen(trainingCoursesProvider, (previous, current) {
      if (previous?.currentPage == 1 && !current.isLoading && current.courses.isEmpty) {
        ref.read(trainingCoursesProvider.notifier).fetchCourses(
          categoryId: categoryId,
          level: level,
        );
      }
    });
    
    // 显示加载中状态
    if (coursesState.isLoading && coursesState.courses.isEmpty) {
      return const Center(
        child: LoadingIndicator(),
      );
    }
    
    // 显示错误信息
    if (coursesState.errorMessage != null && coursesState.courses.isEmpty) {
      return Center(
        child: ErrorMessage(
          message: coursesState.errorMessage!,
          onRetry: () => ref.read(trainingCoursesProvider.notifier).fetchCourses(
            categoryId: categoryId,
            level: level,
          ),
        ),
      );
    }
    
    // 显示空数据状态
    if (coursesState.courses.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(
              Icons.school_outlined,
              size: 64,
              color: Colors.grey,
            ),
            const SizedBox(height: 16),
            Text(
              '暂无课程',
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: Colors.grey[600],
              ),
            ),
            const SizedBox(height: 8),
            TextButton(
              onPressed: () => ref.read(trainingCoursesProvider.notifier).fetchCourses(
                categoryId: categoryId,
                level: level,
              ),
              child: const Text('刷新'),
            ),
          ],
        ),
      );
    }
    
    // 显示课程列表
    return RefreshIndicator(
      onRefresh: () async {
        ref.read(trainingCoursesProvider.notifier).refreshCourses(
          categoryId: categoryId,
          level: level,
        );
      },
      child: NotificationListener<ScrollNotification>(
        onNotification: (ScrollNotification scrollInfo) {
          if (scrollInfo.metrics.pixels == scrollInfo.metrics.maxScrollExtent) {
            // 滚动到底部时加载更多
            ref.read(trainingCoursesProvider.notifier).loadMoreCourses(
              categoryId: categoryId,
              level: level,
            );
          }
          return false;
        },
        child: ListView.builder(
          padding: const EdgeInsets.symmetric(vertical: 8),
          itemCount: coursesState.isLoading 
              ? coursesState.courses.length + 1 
              : coursesState.courses.length,
          itemBuilder: (context, index) {
            // 显示加载更多指示器
            if (index == coursesState.courses.length && coursesState.isLoading) {
              return const Padding(
                padding: EdgeInsets.all(16.0),
                child: Center(
                  child: CircularProgressIndicator(),
                ),
              );
            }
            
            // 显示课程项
            final course = coursesState.courses[index];
            
            return TrainingCourseItem(
              id: course['id'],
              title: course['title'],
              description: course['description'] ?? '',
              instructorName: course['instructor_name'] ?? '',
              coverImageUrl: course['cover_image_url'],
              duration: course['duration'] ?? 0,
              level: course['level'] ?? '初级',
              studentsCount: course['students_count'] ?? 0,
              rating: (course['rating'] ?? 0.0).toDouble(),
            );
          },
        ),
      ),
    );
  }
}

class TrainingCourseItem extends StatelessWidget {
  final String id;
  final String title;
  final String description;
  final String instructorName;
  final String? coverImageUrl;
  final int duration;
  final String level;
  final int studentsCount;
  final double rating;
  
  const TrainingCourseItem({
    Key? key,
    required this.id,
    required this.title,
    required this.description,
    required this.instructorName,
    this.coverImageUrl,
    required this.duration,
    required this.level,
    required this.studentsCount,
    required this.rating,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      elevation: 2,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: InkWell(
        onTap: () {
          // 导航到课程详情页
          // 当我们创建了课程详情页后，应该更新这里的导航
          // context.router.push(TrainingCourseDetailRoute(courseId: id));
        },
        borderRadius: BorderRadius.circular(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 封面图片
            if (coverImageUrl != null)
              ClipRRect(
                borderRadius: const BorderRadius.vertical(
                  top: Radius.circular(12),
                ),
                child: AspectRatio(
                  aspectRatio: 16 / 9,
                  child: Image.network(
                    coverImageUrl!,
                    fit: BoxFit.cover,
                    errorBuilder: (context, error, stackTrace) {
                      return Container(
                        color: Colors.grey[200],
                        child: const Center(
                          child: Icon(
                            Icons.broken_image,
                            color: Colors.grey,
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ),
              
            // 课程内容
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // 课程难度和时长
                  Row(
                    children: [
                      // 课程难度
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 4,
                        ),
                        decoration: BoxDecoration(
                          color: _getLevelColor(level).withOpacity(0.1),
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: Text(
                          level,
                          style: TextStyle(
                            color: _getLevelColor(level),
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ),
                      
                      const SizedBox(width: 8),
                      
                      // 课程时长
                      Row(
                        children: [
                          Icon(
                            Icons.access_time,
                            size: 16,
                            color: Colors.grey[600],
                          ),
                          const SizedBox(width: 4),
                          Text(
                            '$duration 分钟',
                            style: TextStyle(
                              color: Colors.grey[600],
                              fontSize: 12,
                            ),
                          ),
                        ],
                      ),
                      
                      const Spacer(),
                      
                      // 课程评分
                      if (rating > 0)
                        Row(
                          children: [
                            Icon(
                              Icons.star,
                              size: 16,
                              color: Colors.amber[600],
                            ),
                            const SizedBox(width: 4),
                            Text(
                              rating.toStringAsFixed(1),
                              style: TextStyle(
                                color: Colors.grey[800],
                                fontSize: 12,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ],
                        ),
                    ],
                  ),
                  
                  const SizedBox(height: 8),
                  
                  // 标题
                  Text(
                    title,
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      fontWeight: FontWeight.bold,
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  
                  const SizedBox(height: 8),
                  
                  // 描述
                  Text(
                    description,
                    style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                      color: Colors.grey[700],
                    ),
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  
                  const SizedBox(height: 8),
                  
                  // 讲师和学生数量
                  Row(
                    children: [
                      // 讲师
                      Icon(
                        Icons.person,
                        size: 16,
                        color: Colors.grey[600],
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '讲师: $instructorName',
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontSize: 12,
                        ),
                      ),
                      
                      const Spacer(),
                      
                      // 学生数量
                      Icon(
                        Icons.people,
                        size: 16,
                        color: Colors.grey[600],
                      ),
                      const SizedBox(width: 4),
                      Text(
                        '$studentsCount 人学习',
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontSize: 12,
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
  
  Color _getLevelColor(String level) {
    switch (level) {
      case '初级':
        return Colors.green;
      case '中级':
        return Colors.blue;
      case '高级':
        return Colors.orange;
      default:
        return Colors.grey;
    }
  }
}

/// 培训课程难度选择器
class TrainingLevelSelector extends StatelessWidget {
  final String? selectedLevel;
  final ValueChanged<String?> onLevelSelected;
  
  const TrainingLevelSelector({
    Key? key,
    this.selectedLevel,
    required this.onLevelSelected,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final levels = ['全部', '初级', '中级', '高级'];
    
    return SizedBox(
      height: 48,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 8),
        itemCount: levels.length,
        itemBuilder: (context, index) {
          final level = index == 0 ? null : levels[index];
          final isSelected = 
              (index == 0 && selectedLevel == null) || 
              (index > 0 && selectedLevel == level);
          
          return _buildLevelChip(
            context,
            level,
            levels[index],
            isSelected,
          );
        },
      ),
    );
  }
  
  Widget _buildLevelChip(
    BuildContext context, 
    String? level, 
    String label,
    bool isSelected,
  ) {
    Color chipColor;
    
    if (level == null) {
      chipColor = Colors.grey;
    } else {
      switch (level) {
        case '初级':
          chipColor = Colors.green;
          break;
        case '中级':
          chipColor = Colors.blue;
          break;
        case '高级':
          chipColor = Colors.orange;
          break;
        default:
          chipColor = Colors.grey;
      }
    }
    
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4),
      child: ChoiceChip(
        label: Text(label),
        selected: isSelected,
        onSelected: (selected) {
          if (selected) {
            onLevelSelected(level);
          }
        },
        backgroundColor: Colors.grey[200],
        selectedColor: chipColor.withOpacity(0.2),
        labelStyle: TextStyle(
          color: isSelected ? chipColor : Colors.grey[700],
          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
        ),
      ),
    );
  }
}
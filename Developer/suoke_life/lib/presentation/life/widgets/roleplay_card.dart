import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:auto_route/auto_route.dart';
import '../../../core/router/app_router.dart';
import '../../../core/widgets/animated_gradient_card.dart';
import '../../../core/widgets/animated_press_button.dart';
import '../../../core/theme/app_colors.dart';
import '../../../di/providers/user_providers.dart';

class RoleplayCard extends ConsumerWidget {
  const RoleplayCard({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final roleplayProgress = ref.watch(rolePlayProgressProvider);
    
    return AnimatedGradientCard(
      title: '角色扮演',
      subtitle: '解锁专属角色体验养生世界',
      gradientColors: [AppColors.primaryColor, AppColors.primaryDarkColor],
      child: roleplayProgress.when(
        data: (progress) {
          final currentRole = ref.watch(currentRoleProvider);
          return Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              currentRole.when(
                data: (role) => Text(
                  '当前角色: ${role.name}',
                  style: const TextStyle(
                    fontSize: 18, 
                    fontWeight: FontWeight.bold,
                    color: Colors.white
                  ),
                ),
                loading: () => const Text(
                  '加载中...',
                  style: TextStyle(
                    fontSize: 18, 
                    fontWeight: FontWeight.bold,
                    color: Colors.white
                  ),
                ),
                error: (_, __) => const Text(
                  '尚未解锁角色',
                  style: TextStyle(
                    fontSize: 18, 
                    fontWeight: FontWeight.bold,
                    color: Colors.white
                  ),
                ),
              ),
              
              const SizedBox(height: 12),
              
              // 角色进度条
              LinearProgressIndicator(
                value: progress.progressToNextLevel,
                backgroundColor: Colors.white.withAlpha(50),
                valueColor: const AlwaysStoppedAnimation<Color>(Colors.white),
              ),
              
              const SizedBox(height: 4),
              Text(
                '等级 ${progress.level} • ${(progress.progressToNextLevel * 100).toStringAsFixed(0)}% 到下一级',
                style: TextStyle(fontSize: 12, color: Colors.white.withAlpha(200)),
              ),
              
              const SizedBox(height: 16),
              Row(
                children: [
                  Expanded(
                    child: AnimatedPressButton(
                      onPressed: () => context.router.push(const RoleplayRoute()),
                      child: const Text('管理角色'),
                      backgroundColor: Colors.white,
                      textColor: AppColors.primaryColor,
                    ),
                  ),
                  if (progress.unlockedRoles.length < 6) ...[
                    const SizedBox(width: 8),
                    Expanded(
                      child: AnimatedPressButton(
                        onPressed: () => _showAvailableRoles(context, ref),
                        child: const Text('解锁新角色'),
                        backgroundColor: AppColors.secondaryColor,
                        textColor: Colors.white,
                      ),
                    ),
                  ]
                ],
              ),
            ],
          );
        },
        loading: () => const Center(
          child: CircularProgressIndicator(
            valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
          ),
        ),
        error: (_, __) => Column(
          children: [
            const Text(
              '无法加载角色信息',
              style: TextStyle(color: Colors.white),
            ),
            const SizedBox(height: 12),
            AnimatedPressButton(
              onPressed: () => ref.refresh(rolePlayProgressProvider),
              child: const Text('重试'),
              backgroundColor: Colors.white,
              textColor: AppColors.primaryColor,
            ),
          ],
        ),
      ),
    );
  }
  
  void _showAvailableRoles(BuildContext context, WidgetRef ref) {
    context.router.push(const AvailableRolesRoute());
  }
} 
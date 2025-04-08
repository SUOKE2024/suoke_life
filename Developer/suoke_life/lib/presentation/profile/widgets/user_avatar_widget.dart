import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../../di/providers/user_providers.dart';
import '../../../core/theme/app_colors.dart';

class UserAvatarWidget extends ConsumerWidget {
  final double size;
  final bool editable;
  final VoidCallback? onTap;
  
  const UserAvatarWidget({
    Key? key, 
    this.size = 128, 
    this.editable = false,
    this.onTap
  }) : super(key: key);
  
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final userAvatar = ref.watch(userAvatarProvider);
    
    return Stack(
      children: [
        // 头像显示
        GestureDetector(
          onTap: onTap,
          child: Container(
            width: size,
            height: size,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: Theme.of(context).colorScheme.surface,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withAlpha(40),
                  blurRadius: 8,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: userAvatar.when(
              data: (avatar) => ClipOval(
                child: avatar.url.isNotEmpty
                  ? CachedNetworkImage(
                      imageUrl: avatar.url,
                      placeholder: (context, url) => _buildPlaceholder(),
                      errorWidget: (context, url, error) => Icon(
                        Icons.person, 
                        size: size * 0.6,
                        color: AppColors.primaryColor,
                      ),
                      fit: BoxFit.cover,
                    )
                  : Icon(
                      Icons.person, 
                      size: size * 0.6, 
                      color: AppColors.primaryColor,
                    ),
              ),
              loading: () => _buildPlaceholder(),
              error: (err, stack) => Icon(
                Icons.error, 
                size: size * 0.6,
                color: Colors.red,
              ),
            ),
          ),
        ),
        
        // 编辑按钮
        if (editable)
          Positioned(
            right: 0,
            bottom: 0,
            child: GestureDetector(
              onTap: () => _showAvatarOptions(context, ref),
              child: Container(
                width: size * 0.3,
                height: size * 0.3,
                decoration: BoxDecoration(
                  color: AppColors.primaryColor,
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: Theme.of(context).scaffoldBackgroundColor,
                    width: 2,
                  ),
                ),
                child: Icon(
                  Icons.camera_alt,
                  color: Colors.white,
                  size: size * 0.15,
                ),
              ),
            ),
          ),
      ],
    );
  }
  
  Widget _buildPlaceholder() {
    return Center(
      child: SizedBox(
        width: size * 0.3,
        height: size * 0.3,
        child: CircularProgressIndicator(
          valueColor: AlwaysStoppedAnimation<Color>(AppColors.primaryColor),
          strokeWidth: 2.0,
        ),
      ),
    );
  }
  
  void _showAvatarOptions(BuildContext context, WidgetRef ref) {
    showModalBottomSheet(
      context: context,
      builder: (context) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.photo_camera, color: AppColors.primaryColor),
              title: const Text('拍摄照片'),
              onTap: () {
                Navigator.pop(context);
                ref.read(userAvatarControllerProvider.notifier).takePhoto();
              },
            ),
            ListTile(
              leading: const Icon(Icons.photo_library, color: AppColors.primaryColor),
              title: const Text('从相册选择'),
              onTap: () {
                Navigator.pop(context);
                ref.read(userAvatarControllerProvider.notifier).pickFromGallery();
              },
            ),
            ListTile(
              leading: const Icon(Icons.auto_fix_high, color: AppColors.secondaryColor),
              title: const Text('AI增强头像'),
              onTap: () {
                Navigator.pop(context);
                ref.read(userAvatarControllerProvider.notifier).applyAIEnhancement();
              },
            ),
            if (ref.read(userAvatarControllerProvider).hasAvatar)
              ListTile(
                leading: const Icon(Icons.delete, color: Colors.red),
                title: const Text('删除当前头像'),
                onTap: () {
                  Navigator.pop(context);
                  _showDeleteConfirmation(context, ref);
                },
              ),
          ],
        ),
      ),
    );
  }
  
  void _showDeleteConfirmation(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('删除头像'),
        content: const Text('确定要删除当前头像吗？将会使用系统默认头像。'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              ref.read(userAvatarControllerProvider.notifier).removeAvatar();
            },
            child: const Text('删除', style: TextStyle(color: Colors.red)),
          ),
        ],
      ),
    );
  }
} 
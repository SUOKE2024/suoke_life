import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import '../models/moment.dart';

class MomentCard extends StatelessWidget {
  final Moment moment;

  const MomentCard({
    super.key,
    required this.moment,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.only(bottom: 16.h),
      child: Padding(
        padding: EdgeInsets.all(16.w),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // 用户信息
            Row(
              children: [
                CircleAvatar(
                  backgroundImage: NetworkImage(moment.avatar),
                ),
                SizedBox(width: 8.w),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      moment.userName,
                      style: TextStyle(
                        fontWeight: FontWeight.bold,
                        fontSize: 16.sp,
                      ),
                    ),
                    Text(
                      _formatTime(moment.createTime),
                      style: TextStyle(
                        color: Colors.grey[600],
                        fontSize: 12.sp,
                      ),
                    ),
                  ],
                ),
              ],
            ),
            
            // 动态内容
            SizedBox(height: 12.h),
            Text(moment.content),
            
            // 图片
            if (moment.images.isNotEmpty) ...[
              SizedBox(height: 12.h),
              _buildImageGrid(moment.images),
            ],
            
            // 互动按钮
            SizedBox(height: 12.h),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                _buildActionButton(
                  icon: Icons.thumb_up_outlined,
                  label: moment.likes.toString(),
                  onPressed: () {
                    // TODO: 实现点赞功能
                  },
                ),
                SizedBox(width: 16.w),
                _buildActionButton(
                  icon: Icons.comment_outlined,
                  label: moment.comments.toString(),
                  onPressed: () {
                    // TODO: 实现评论功能
                  },
                ),
                SizedBox(width: 16.w),
                _buildActionButton(
                  icon: Icons.share_outlined,
                  label: moment.shares.toString(),
                  onPressed: () {
                    // TODO: 实现分享功能
                  },
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildImageGrid(List<String> images) {
    if (images.length == 1) {
      return AspectRatio(
        aspectRatio: 16 / 9,
        child: Image.network(
          images[0],
          fit: BoxFit.cover,
        ),
      );
    }

    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        mainAxisSpacing: 4.w,
        crossAxisSpacing: 4.w,
      ),
      itemCount: images.length,
      itemBuilder: (context, index) {
        return Image.network(
          images[index],
          fit: BoxFit.cover,
        );
      },
    );
  }

  Widget _buildActionButton({
    required IconData icon,
    required String label,
    required VoidCallback onPressed,
  }) {
    return TextButton.icon(
      onPressed: onPressed,
      icon: Icon(icon, size: 20.w),
      label: Text(label),
      style: TextButton.styleFrom(
        padding: EdgeInsets.symmetric(horizontal: 8.w),
        minimumSize: Size.zero,
        tapTargetSize: MaterialTapTargetSize.shrinkWrap,
      ),
    );
  }

  String _formatTime(DateTime time) {
    final now = DateTime.now();
    final difference = now.difference(time);

    if (difference.inMinutes < 1) {
      return '刚刚';
    } else if (difference.inHours < 1) {
      return '${difference.inMinutes}分钟前';
    } else if (difference.inDays < 1) {
      return '${difference.inHours}小时前';
    } else if (difference.inDays < 30) {
      return '${difference.inDays}天前';
    } else {
      return '${time.year}-${time.month}-${time.day}';
    }
  }
} 
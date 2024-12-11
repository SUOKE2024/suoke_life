class Moment {
  final String id;
  final String userId;
  final String userName;
  final String avatar;
  final String content;
  final List<String> images;
  final int likes;
  final int comments;
  final int shares;
  final DateTime createTime;

  const Moment({
    required this.id,
    required this.userId,
    required this.userName,
    required this.avatar,
    required this.content,
    required this.images,
    required this.likes,
    required this.comments,
    required this.shares,
    required this.createTime,
  });
} 
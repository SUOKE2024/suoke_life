import 'dart:io';

import 'package:dartz/dartz.dart';
import '../entities/user_avatar.dart';
import '../../core/utils/failure.dart';

abstract class UserAvatarRepository {
  /// 获取用户当前头像
  Future<Either<Failure, UserAvatar>> getCurrentAvatar(String userId);
  
  /// 上传新头像
  Future<Either<Failure, UserAvatar>> uploadAvatar(String userId, File imageFile);
  
  /// 从相册选择头像
  Future<Either<Failure, UserAvatar>> pickFromGallery(String userId);
  
  /// 拍照设置头像
  Future<Either<Failure, UserAvatar>> takePhoto(String userId);
  
  /// 设置默认头像
  Future<Either<Failure, UserAvatar>> setDefaultAvatar(String userId, String avatarSetName);
  
  /// 删除当前头像
  Future<Either<Failure, bool>> removeAvatar(String userId);
  
  /// 应用AI增强
  Future<Either<Failure, UserAvatar>> applyAIEnhancement(String userId, String avatarId);
} 
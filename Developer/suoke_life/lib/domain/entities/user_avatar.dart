import 'package:freezed_annotation/freezed_annotation.dart';

part 'user_avatar.freezed.dart';

@freezed
class UserAvatar with _$UserAvatar {
  const factory UserAvatar({
    required String id,
    required String userId,
    required String url,
    required String thumbnailSmallUrl,
    required String thumbnailMediumUrl,
    required String thumbnailLargeUrl,
    required bool isDefault,
    @Default(AvatarStorageType.cloud) AvatarStorageType storageType,
    DateTime? lastUpdated,
    Map<String, dynamic>? metadata,
  }) = _UserAvatar;
}

enum AvatarStorageType {
  cloud,
  local
} 
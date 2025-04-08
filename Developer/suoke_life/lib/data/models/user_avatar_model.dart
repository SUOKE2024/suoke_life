import 'package:freezed_annotation/freezed_annotation.dart';
import 'package:json_annotation/json_annotation.dart';
import '../../domain/entities/user_avatar.dart';

part 'user_avatar_model.freezed.dart';
part 'user_avatar_model.g.dart';

@freezed
class UserAvatarModel with _$UserAvatarModel {
  const factory UserAvatarModel({
    required String id,
    required String userId,
    required String url,
    required String thumbnailSmallUrl,
    required String thumbnailMediumUrl,
    required String thumbnailLargeUrl,
    required bool isDefault,
    @Default('cloud') String storageType,
    String? lastUpdatedAt,
    Map<String, dynamic>? metadata,
  }) = _UserAvatarModel;

  factory UserAvatarModel.fromJson(Map<String, dynamic> json) =>
      _$UserAvatarModelFromJson(json);

  factory UserAvatarModel.fromEntity(UserAvatar entity) {
    return UserAvatarModel(
      id: entity.id,
      userId: entity.userId,
      url: entity.url,
      thumbnailSmallUrl: entity.thumbnailSmallUrl,
      thumbnailMediumUrl: entity.thumbnailMediumUrl,
      thumbnailLargeUrl: entity.thumbnailLargeUrl,
      isDefault: entity.isDefault,
      storageType: entity.storageType.toString().split('.').last,
      lastUpdatedAt: entity.lastUpdated?.toIso8601String(),
      metadata: entity.metadata,
    );
  }
}

extension UserAvatarModelX on UserAvatarModel {
  UserAvatar toEntity() {
    return UserAvatar(
      id: id,
      userId: userId,
      url: url,
      thumbnailSmallUrl: thumbnailSmallUrl,
      thumbnailMediumUrl: thumbnailMediumUrl,
      thumbnailLargeUrl: thumbnailLargeUrl,
      isDefault: isDefault,
      storageType: storageType == 'cloud'
          ? AvatarStorageType.cloud
          : AvatarStorageType.local,
      lastUpdated: lastUpdatedAt != null ? DateTime.parse(lastUpdatedAt!) : null,
      metadata: metadata,
    );
  }
} 
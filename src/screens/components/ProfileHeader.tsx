import { View, Text, StyleSheet, TouchableOpacity, Image } from "react-native";
import Icon from "../../components/common/Icon";
import { UserProfile } from "../../types/profile";
import React from "react";






  colors,
  spacing,
  typography,
  borderRadius,
} from "../../constants/theme";

interface ProfileHeaderProps {
  userProfile: UserProfile;
  onEditPress: () => void;
  getHealthScoreColor: (score: number) => string;
  getMemberLevelText: (level: string) => string;
}

const ProfileHeader: React.FC<ProfileHeaderProps> = ({
  userProfile,
  onEditPress,
  getHealthScoreColor,
  getMemberLevelText,
}) => {
  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <View style={styles.avatarContainer}>
          <Text style={styles.avatar}>{userProfile.avatar}</Text>
        </View>
        <View style={styles.userInfo}>
          <View style={styles.nameRow}>
            <Text style={styles.name}>{userProfile.name}</Text>
            <TouchableOpacity onPress={onEditPress} style={styles.editButton}>
              <Icon name="pencil" size={16} color={colors.primary} />
            </TouchableOpacity>
          </View>
          <Text style={styles.memberLevel}>
            {getMemberLevelText(userProfile.memberLevel)}
          </Text>
          <Text style={styles.joinDate}>加入时间：{userProfile.joinDate}</Text>
        </View>
      </View>

      <View style={styles.statsContainer}>
        <View style={styles.statItem}>
          <Text
            style={[
              styles.statValue,
              { color: getHealthScoreColor(userProfile.healthScore) },
            ]}
          >
            {userProfile.healthScore}
          </Text>
          <Text style={styles.statLabel}>健康分数</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statValue}>{userProfile.totalDiagnosis}</Text>
          <Text style={styles.statLabel}>诊断次数</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statValue}>{userProfile.consecutiveDays}</Text>
          <Text style={styles.statLabel}>连续天数</Text>
        </View>
        <View style={styles.statItem}>
          <Text style={styles.statValue}>{userProfile.healthPoints}</Text>
          <Text style={styles.statLabel}>健康积分</Text>
        </View>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    backgroundColor: colors.white,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.xl,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: spacing.lg,
  },
  avatarContainer: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: colors.gray300,
    justifyContent: "center",
    alignItems: "center",
    marginRight: spacing.lg,
  },
  avatar: {
    fontSize: 40,
  },
  userInfo: {
    flex: 1,
  },
  nameRow: {
    flexDirection: "row",
    alignItems: "center",
    marginBottom: spacing.xs,
  },
  name: {
    fontSize: typography.fontSize.xl,
    fontWeight: "700" as any,
    color: colors.textPrimary,
    marginRight: spacing.sm,
  },
  editButton: {
    padding: spacing.xs,
  },
  memberLevel: {
    fontSize: typography.fontSize.base,
    color: colors.primary,
    fontWeight: "500" as any,
    marginBottom: spacing.xs,
  },
  joinDate: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
  statsContainer: {
    flexDirection: "row",
    justifyContent: "space-around",
    paddingTop: spacing.lg,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  statItem: {
    alignItems: "center",
  },
  statValue: {
    fontSize: typography.fontSize.xl,
    fontWeight: "700" as any,
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  statLabel: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
  },
});

export default React.memo(ProfileHeader);

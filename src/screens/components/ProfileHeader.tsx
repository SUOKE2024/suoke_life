

const importIcon = from ";../../components/common/    Icon";""/;,"/g"/;
const importReact = from "react";";
colors,;
spacing,";,"";
typography,";"";
  { borderRadius } from "../../constants/    theme";""/;,"/g"/;
interface ProfileHeaderProps {userProfile: UserProfile}onEditPress: () => void,;
getHealthScoreColor: (score: number) => string,;
}
}
  getMemberLevelText: (level: string) => string;}
}";,"";
const  ProfileHeader: React.FC<ProfileHeaderProps /    > = ({/;)// 性能监控)"/;,}const: performanceMonitor = usePerformanceMonitor(ProfileHeader", {")";}}"/g,"/;
  trackRender: true,}
    trackMemory: false,warnThreshold: 50, // ms ;};);/;,/g/;
userProfile,;
onEditPress,;
getHealthScoreColor,;
getMemberLevelText;
}) => {}
  // 记录渲染性能/;,/g/;
performanceMonitor.recordRender();
return (<View style={styles.container} /    >/;)      <View style={styles.header} /    >/;/g/;
        <View style={styles.avatarContainer} /    >/;/g/;
          <Text style={styles.avatar}>{userProfile.avatar}</    Text>/;/g/;
        </    View>;/;/g/;
        <View style={styles.userInfo} /    >;/;/g/;
          <View style={styles.nameRow} /    >;"/;"/g"/;
            <Text style={styles.name}>{userProfile.name}</    Text>;"/;"/g"/;
            <TouchableOpacity onPress={onEditPress} style={styles.editButton} accessibilityLabel="TODO: 添加无障碍标签" /    >;"/;"/g"/;
              <Icon name="pencil" size={16} color={colors.primary} /    >;"/;"/g"/;
            </    TouchableOpacity>;)/;/g/;
          </    View>;)/;/g/;
          <Text style={styles.memberLevel} /    >;)/;/g/;
            {getMemberLevelText(userProfile.memberLevel)};
          </    Text>;/;/g/;
          <Text style={styles.joinDate}>加入时间：{userProfile.joinDate}</    Text>;/;/g/;
        </    View>;/;/g/;
      </    View>;/;/g/;
      <View style={styles.statsContainer} /    >;/;/g/;
        <View style={styles.statItem} /    >;/;/g/;
          <Text;  />/;,/g/;
style={}[;]}
              styles.statValue,}
              { color: getHealthScoreColor(userProfile.healthScore)   ;}}
];
            ]} /    >/;/g/;
            {userProfile.healthScore}
          </    Text>/;/g/;
          <Text style={styles.statLabel}>健康分数</    Text>/;/g/;
        </    View>/;/g/;
        <View style={styles.statItem} /    >/;/g/;
          <Text style={styles.statValue}>{userProfile.totalDiagnosis}</    Text>/;/g/;
          <Text style={styles.statLabel}>诊断次数</    Text>/;/g/;
        </    View>/;/g/;
        <View style={styles.statItem} /    >/;/g/;
          <Text style={styles.statValue}>{userProfile.consecutiveDays}</    Text>/;/g/;
          <Text style={styles.statLabel}>连续天数</    Text>/;/g/;
        </    View>/;/g/;
        <View style={styles.statItem} /    >/;/g/;
          <Text style={styles.statValue}>{userProfile.healthPoints}</    Text>/;/g/;
          <Text style={styles.statLabel}>健康积分</    Text>/;/g/;
        </    View>/;/g/;
      </    View>/;/g/;
    </    View;>/;/g/;
  ;);
}
const: styles = StyleSheet.create({)container: {)}backgroundColor: colors.white,;
paddingHorizontal: spacing.lg,;
paddingVertical: spacing.xl,;
borderBottomWidth: 1,;
}
    const borderBottomColor = colors.border;}
  },";,"";
header: {,";,}flexDirection: "row";",";
alignItems: "center";","";"";
}
    const marginBottom = spacing.lg;}
  }
avatarContainer: {width: 80,;
height: 80,;
borderRadius: 40,";,"";
backgroundColor: colors.gray300,";,"";
justifyContent: "center";",";
alignItems: "center";","";"";
}
    const marginRight = spacing.lg;}
  }
avatar: { fontSize: 40  ;}
userInfo: { flex: 1  ;},";,"";
nameRow: {,";,}flexDirection: "row";",";
alignItems: "center";","";"";
}
    const marginBottom = spacing.xs;}
  }
name: {,";,}fontSize: typography.fontSize.xl,";,"";
fontWeight: "700" as any;",";
color: colors.textPrimary,;
}
    const marginRight = spacing.sm;}
  }
editButton: { padding: spacing.xs  ;}
memberLevel: {fontSize: typography.fontSize.base,";,"";
color: colors.primary,";,"";
fontWeight: "500" as any;","";"";
}
    const marginBottom = spacing.xs;}
  }
joinDate: {fontSize: typography.fontSize.sm,;
}
    const color = colors.textSecondary;}
  },";,"";
statsContainer: {,";,}flexDirection: "row";",";
justifyContent: "space-around";",";
paddingTop: spacing.lg,;
borderTopWidth: 1,;
}
    const borderTopColor = colors.border;}";"";
  },";,"";
statItem: { alignItems: "center"  ;},";,"";
statValue: {,";,}fontSize: typography.fontSize.xl,";,"";
fontWeight: "700" as any;",";
color: colors.textPrimary,;
}
    const marginBottom = spacing.xs;}
  }
statLabel: {,}
  fontSize: typography.fontSize.sm,color: colors.textSecondary;};};);";,"";
export default React.memo(ProfileHeader);""";
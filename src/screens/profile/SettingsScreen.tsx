import { useNavigation } from "@react-navigation/native";
import { colors, spacing, fonts } from "../../constants/theme";
import { useDispatch } from "react-redux";
import { logout } from "../../store/slices/authSlice";
import { NativeStackNavigationProp } from "@react-navigation/native-stack";
import { MainStackParamList } from "../../navigation/MainNavigator";
import React from "react";


  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
} from "react-native";

type SettingsScreenNavigationProp = NativeStackNavigationProp<
  MainStackParamList,
  "Settings"
>;

export const SettingsScreen: React.FC = () => {
  const navigation = useNavigation<SettingsScreenNavigationProp>();
  const dispatch = useDispatch();

  const handleLogout = async () => {
    try {
      await dispatch(logout() as any);
    } catch (error) {
      console.error("登出失败:", error);
    }
  };

  const handleBack = useCallback( () => {, []);
    navigation.goBack();
  };

  const navigateToServiceStatus = useCallback( () => {, []);
    navigation.navigate("ServiceStatus");
  };

  const navigateToServiceManagement = useCallback( () => {, []);
    navigation.navigate("ServiceManagement");
  };

  const navigateToDeveloperPanel = useCallback( () => {, []);
    navigation.navigate("DeveloperPanel");
  };

  return (
    <View style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={handleBack} style={styles.backButton}>
          <Text style={styles.backButtonText}>返回</Text>
        </TouchableOpacity>
        <Text style={styles.headerTitle}>设置</Text>
        <View style={styles.placeholder} />
      </View>

      <ScrollView style={styles.content}>
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>账户设置</Text>
          <TouchableOpacity style={styles.settingItem}>
            <Text style={styles.settingText}>个人资料</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.settingItem}>
            <Text style={styles.settingText}>修改密码</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.settingItem}>
            <Text style={styles.settingText}>隐私设置</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>应用设置</Text>
          <TouchableOpacity style={styles.settingItem}>
            <Text style={styles.settingText}>通知</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.settingItem}>
            <Text style={styles.settingText}>语言</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.settingItem}>
            <Text style={styles.settingText}>显示主题</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>系统与开发</Text>
          <TouchableOpacity
            style={styles.settingItem}
            onPress={navigateToServiceStatus}
          >
            <Text style={styles.settingText}>服务状态</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.settingItem}
            onPress={navigateToServiceManagement}
          >
            <Text style={styles.settingText}>服务管理</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.settingItem}
            onPress={navigateToDeveloperPanel}
          >
            <Text style={styles.settingText}>开发者面板</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.settingItem}>
            <Text style={styles.settingText}>清除缓存</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.settingItem}>
            <Text style={styles.settingText}>检查更新</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>其他</Text>
          <TouchableOpacity style={styles.settingItem}>
            <Text style={styles.settingText}>关于我们</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.settingItem}>
            <Text style={styles.settingText}>帮助与反馈</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.settingItem}>
            <Text style={styles.settingText}>服务条款</Text>
          </TouchableOpacity>
        </View>

        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Text style={styles.logoutButtonText}>退出登录</Text>
        </TouchableOpacity>
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    padding: spacing.md,
    backgroundColor: colors.white,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  backButton: {
    padding: spacing.sm,
  },
  backButtonText: {
    color: colors.primary,
    fontSize: fonts.size.md,
    fontWeight: "bold",
  },
  headerTitle: {
    fontSize: fonts.size.lg,
    fontWeight: "bold",
    color: colors.text,
  },
  placeholder: {
    width: 50,
  },
  content: {
    flex: 1,
    padding: spacing.md,
  },
  section: {
    marginBottom: spacing.xl,
    backgroundColor: colors.white,
    borderRadius: 8,
    padding: spacing.md,
    ...StyleSheet.flatten({
      shadowColor: "#000",
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
      elevation: 2,
    }),
  },
  sectionTitle: {
    fontSize: fonts.size.md,
    fontWeight: "bold",
    color: colors.textSecondary,
    marginBottom: spacing.md,
  },
  settingItem: {
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  settingText: {
    fontSize: fonts.size.md,
    color: colors.text,
  },
  logoutButton: {
    marginVertical: spacing.xl,
    backgroundColor: colors.error,
    padding: spacing.md,
    borderRadius: 8,
    alignItems: "center",
  },
  logoutButtonText: {
    color: colors.white,
    fontSize: fonts.size.md,
    fontWeight: "bold",
  },
});

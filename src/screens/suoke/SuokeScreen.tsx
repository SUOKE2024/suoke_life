import {import { SafeAreaView } from "react-native-safe-area-context";
import { useNavigation } from "@react-navigation/native";
import Icon from "react-native-vector-icons/MaterialCommunityIcons";
import { colors, spacing, typography } from "../../constants/theme";

import React, { useState, useEffect } from "react";
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Alert,
  ActivityIndicator
} from "react-native";

interface ServiceItem {
  id: string;
  title: string;
  description: string;
  icon: string;
  status: "active" | "inactive" | "maintenance";
  lastUpdate: string;
  action?: () => void;
}

const SuokeScreen: React.FC = () => {
  const navigation = useNavigation();
  const [services, setServices] = useState<ServiceItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadServices();
  }, [])  // 检查是否需要添加依赖项;

  const loadServices = async () => {try {const mockServices: ServiceItem[] = [;
        {id: "medical-resource",title: "医疗资源管理",description: "智能搜索和管理医疗资源，预约医疗服务",icon: "hospital-box",status: "active",lastUpdate: "2024-01-15 10:30",action: () => navigateToMedicalResources();
        },
        {
          id: "appointment-management",
          title: "预约管理服务",
          description: "管理用户的医疗预约，提供预约提醒和管理",
          icon: "calendar-clock",
          status: "active",
          lastUpdate: "2024-01-15 09:45",
          action: () => navigateToAppointments();
        },
        {
          id: "health-monitoring",
          title: "健康监测服务",
          description: "实时监控用户健康状态变化，提供健康建议",
          icon: "heart-pulse",
          status: "active",
          lastUpdate: "2024-01-15 09:45",
          action: () => navigateToHealthMonitoring();
        },
        {
          id: "tcm-diagnosis",
          title: "中医辨证诊断",
          description: "基于传统中医理论的智能辨证系统",
          icon: "medical-bag",
          status: "active",
          lastUpdate: "2024-01-15 10:30",
          action: () => navigateToTCMDiagnosis();
        },
        {
          id: "agent-coordination",
          title: "智能体协调",
          description: "管理四个智能体之间的协作关系",
          icon: "account-group",
          status: "active",
          lastUpdate: "2024-01-15 08:20",
          action: () => navigateToAgentCoordination();
        },
        {
          id: "data-analysis",
          title: "数据分析引擎",
          description: "深度分析用户健康数据趋势",
          icon: "chart-line",
          status: "maintenance",
          lastUpdate: "2024-01-14 16:00",
          action: () => navigateToDataAnalysis();
        };
      ];

      setServices(mockServices);
    } catch (error) {
      Alert.alert("错误", "加载服务列表失败，请稍后重试");
    } finally {
      setLoading(false);
    }
  };

  // 导航到医疗资源页面
  const navigateToMedicalResources = () => {// 导航到Life标签页的医疗资源部分;
    navigation.navigate("Life" as never);
  };

  // 导航到预约管理页面
  const navigateToAppointments = () => {// 导航到Life标签页的预约管理部分;
    navigation.navigate("Life" as never);
  };

  // 导航到健康监测页面
  const navigateToHealthMonitoring = () => {Alert.alert("健康监测", "即将打开健康监测面板");
  };

  // 导航到中医诊断页面
  const navigateToTCMDiagnosis = () => {Alert.alert("中医诊断", "即将启动中医辨证诊断功能");
  };

  // 导航到智能体协调页面
  const navigateToAgentCoordination = () => {Alert.alert("智能体协调", "即将打开智能体管理界面");
  };

  // 导航到数据分析页面
  const navigateToDataAnalysis = () => {Alert.alert("数据分析", "即将打开数据分析报告");
  };

  // 搜索附近医院
  const searchNearbyHospitals = () => {Alert.alert("搜索附近医院", "正在搜索您附近的医疗机构...");
    // 这里可以集成实际的搜索功能
    setTimeout(() => {
      navigation.navigate("Life" as never);
    }, 1000);
  };

  const handleServicePress = (service: ServiceItem) => {if (service.status === "maintenance") {Alert.alert("服务维护中", `${service.title} 正在维护，请稍后再试`);
      return;
    }

    if (service.action) {
      service.action();
    } else {
      Alert.alert("功能开发中", "该功能正在开发中，敬请期待");
    }
  };

  const getStatusColor = (status: ServiceItem["status"]) => {switch (status) {case "active":return colors.success;
      case "inactive":
        return colors.error;
      case "maintenance":
        return colors.warning;
      default:
        return colors.textSecondary;
    }
  };

  const getStatusText = (status: ServiceItem["status"]) => {switch (status) {case "active":return "运行中";
      case "inactive":
        return "已停止";
      case "maintenance":
        return "维护中";
      default:
        return "未知";
    }
  };

  const renderServiceCard = (service: ServiceItem) => (
    <TouchableOpacity
      key={service.id}
      style={styles.serviceCard}
      onPress={() => handleServicePress(service)}
      activeOpacity={0.7}
    >
      <View style={styles.serviceHeader}>
        <View style={styles.serviceIconContainer}>
          <Icon name={service.icon} size={24} color={colors.primary} />
        </View>
        <View style={styles.serviceInfo}>;
          <Text style={styles.serviceTitle}>{service.title}</Text>;
          <Text style={styles.serviceDescription}>{service.description}</Text>;
        </View>;
        <View style={styles.serviceStatus}>;
          <View style={[styles.statusIndicator, { backgroundColor: getStatusColor(service.status) }]} />;
          <Text style={[styles.statusText, { color: getStatusColor(service.status) }]}>;
            {getStatusText(service.status)};
          </Text>;
        </View>;
      </View>;
      <View style={styles.serviceFooter}>;
        <Text style={styles.lastUpdateText}>最后更新: {service.lastUpdate}</Text>;
        <Icon name="chevron-right" size={20} color={colors.textSecondary} />;
      </View>;
    </TouchableOpacity>;
  );

  if (loading) {
    return (;
      <SafeAreaView style={styles.container}>;
        <View style={styles.loadingContainer}>;
          <ActivityIndicator size="large" color={colors.primary} />;
          <Text style={styles.loadingText}>正在加载服务...</Text>;
        </View>;
      </SafeAreaView>;
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <View style={styles.headerContent}>
          <View style={styles.agentInfo}>
            <Text style={styles.agentEmoji}>🤖</Text>
            <View>
              <Text style={styles.agentName}>小克</Text>
              <Text style={styles.agentRole}>服务管理智能体</Text>
            </View>
          </View>
          <TouchableOpacity style={styles.settingsButton}>
            <Icon name="cog" size={24} color={colors.textSecondary} />
          </TouchableOpacity>
        </View>
        <Text style={styles.headerDescription}>
          负责管理和协调索克生活平台的各项服务，包括医疗资源管理、预约服务等
        </Text>
      </View>

      <ScrollView
        style={styles.scrollView}
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {// 医疗服务快捷入口}
        <View style={styles.quickActionsSection}>
          <Text style={styles.sectionTitle}>医疗服务快捷入口</Text>
          <View style={styles.quickActionsContainer}>
            <TouchableOpacity 
              style={styles.quickActionButton}
              onPress={navigateToMedicalResources}
            >
              <Icon name="hospital-box" size={24} color={colors.primary} />
              <Text style={styles.quickActionText}>医疗资源</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={styles.quickActionButton}
              onPress={navigateToAppointments}
            >
              <Icon name="calendar-clock" size={24} color={colors.primary} />
              <Text style={styles.quickActionText}>我的预约</Text>
            </TouchableOpacity>
            <TouchableOpacity 
              style={styles.quickActionButton}
              onPress={searchNearbyHospitals}
            >
              <Icon name="map-marker-radius" size={24} color={colors.primary} />
              <Text style={styles.quickActionText}>附近医院</Text>
            </TouchableOpacity>
          </View>
        </View>

        {// 管理的服务}
        <View style={styles.servicesSection}>
          <Text style={styles.sectionTitle}>管理的服务</Text>
          {services.map(renderServiceCard)}
        </View>

        {// 服务统计}
        <View style={styles.statsSection}>
          <Text style={styles.sectionTitle}>服务统计</Text>
          <View style={styles.statsContainer}>
            <View style={styles.statItem}>;
              <Text style={styles.statValue}>{services.filter(s => s.status === "active").length}</Text>;
              <Text style={styles.statLabel}>运行中</Text>;
            </View>;
            <View style={styles.statItem}>;
              <Text style={styles.statValue}>{services.filter(s => s.status === "maintenance").length}</Text>;
              <Text style={styles.statLabel}>维护中</Text>;
            </View>;
            <View style={styles.statItem}>;
              <Text style={styles.statValue}>{services.length}</Text>;
              <Text style={styles.statLabel}>总服务</Text>;
            </View>;
          </View>;
        </View>;
      </ScrollView>;
    </SafeAreaView>;
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background
  },
  loadingContainer: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center"
  },
  loadingText: {
    marginTop: spacing.md,
    fontSize: typography.fontSize.base,
    color: colors.textSecondary
  },
  header: {
    backgroundColor: colors.surface,
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border
  },
  headerContent: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: spacing.sm
  },
  agentInfo: {
    flexDirection: "row",
    alignItems: "center"
  },
  agentEmoji: {
    fontSize: 32,
    marginRight: spacing.md
  },
  agentName: {
    fontSize: typography.fontSize["2xl"],
    fontWeight: "700",
    color: colors.textPrimary
  },
  agentRole: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary
  },
  settingsButton: {
    padding: spacing.sm
  },
  headerDescription: {
    fontSize: typography.fontSize.base,
    color: colors.textSecondary,
    lineHeight: 20
  },
  scrollView: {
    flex: 1
  },
  scrollContent: {
    paddingVertical: spacing.lg
  },
  quickActionsSection: {
    paddingHorizontal: spacing.lg,
    marginBottom: spacing.xl
  },
  quickActionsContainer: {
    flexDirection: "row",
    justifyContent: "space-around",
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
    borderWidth: 1,
    borderColor: colors.border
  },
  quickActionButton: {
    alignItems: "center",
    padding: spacing.sm
  },
  quickActionText: {
    fontSize: typography.fontSize.sm,
    color: colors.text,
    marginTop: spacing.xs,
    textAlign: "center"
  },
  servicesSection: {
    paddingHorizontal: spacing.lg,
    marginBottom: spacing.xl
  },
  sectionTitle: {
    fontSize: typography.fontSize.lg,
    fontWeight: "600",
    color: colors.text,
    marginBottom: spacing.md
  },
  serviceCard: {
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.md,
    marginBottom: spacing.md,
    borderWidth: 1,
    borderColor: colors.border
  },
  serviceHeader: {
    flexDirection: "row",
    alignItems: "flex-start",
    marginBottom: spacing.sm
  },
  serviceIconContainer: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: colors.primaryLight,
    justifyContent: "center",
    alignItems: "center",
    marginRight: spacing.md
  },
  serviceInfo: {
    flex: 1,
    marginRight: spacing.md
  },
  serviceTitle: {
    fontSize: typography.fontSize.base,
    fontWeight: "600",
    color: colors.text,
    marginBottom: 4
  },
  serviceDescription: {
    fontSize: typography.fontSize.sm,
    color: colors.textSecondary,
    lineHeight: 16
  },
  serviceStatus: {
    alignItems: "flex-end"
  },
  statusIndicator: {
    width: 8,
    height: 8,
    borderRadius: 4,
    marginBottom: 4
  },
  statusText: {
    fontSize: typography.fontSize.xs,
    fontWeight: "600"
  },
  serviceFooter: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingTop: spacing.sm,
    borderTopWidth: 1,
    borderTopColor: colors.border
  },
  lastUpdateText: {
    fontSize: typography.fontSize.xs,
    color: colors.textSecondary
  },
  statsSection: {
    paddingHorizontal: spacing.lg
  },
  statsContainer: {
    flexDirection: "row",
    justifyContent: "space-around",
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: spacing.lg,
    borderWidth: 1,borderColor: colors.border;
  },statItem: {alignItems: "center";
  },statValue: {fontSize: 24,fontWeight: "bold",color: colors.primary,marginBottom: 4;
  },statLabel: {fontSize: typography.fontSize.xs,color: colors.textSecondary;
  };
});

export default SuokeScreen;

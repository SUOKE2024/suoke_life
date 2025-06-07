import { usePerformanceMonitor  } from "../../placeholder";../hooks/usePerformanceMonitor";/    import {   View,"
import { useNavigation } from "@react-navigation/native/import { colors, spacing  } from ;../../constants/theme";/import { API_CONFIG } from ../../constants/    config;
import React from "react";
interface ApiResponse<T = any /> { data: T;/     , success: boolean;
  message?: string;
  code?: number}
import React,{ useState, useEffect, useCallback, useMemo } from "react";
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  Switch,
  { Platform    } from react-native""
/
interface serviceInfo {
  id: string;
  name: string;
  description: string;
  type: "agent | "core" | diagnosis";
  isRunning: boolean;
  baseUrl: string;
  status: "starting | "running" | stopping" | "stopped | "error;
  lastAction?: string
};

export const serviceManagementScreen: React.FC  = () => {};

const performanceMonitor = usePerformanceMonitor(serviceManagementScreen", { ";
    trackRender: true,trackMemory: true,warnThreshold: 50,  };);
  const navigation = useNavigation;
  const [loading, setLoading] = useState<boolean>(fals;e;);
  const [services, setservices] = useState<serviceInfo[] />([;];);/      const [autoStart, setAutoStart] = useState<boolean>(fals;e;);
  const initializeservices = useCallback(); => {};

const servicesList: serviceInfo[] = [ { /,
  id: "xiaoai,",
        name: "小艾服务",
        description: 中医诊断智能体",
        type: "agent,",
        isRunning: false,
        baseUrl: API_CONFIG.AGENTS.XIAOAI,
        status: "stopped"
      },
      {
        id: xiaoke",
        name: "小克服务,",
        description: "服务管理智能体",
        type: agent",
        isRunning: false,
        baseUrl: API_CONFIG.AGENTS.XIAOKE,
        status: "stopped"
      },
      {
      id: "laoke",
      name: 老克服务",
        description: "教育智能体,",
        type: "agent",
        isRunning: false,
        baseUrl: API_CONFIG.AGENTS.LAOKE,
        status: stopped""
      },
      {
      id: "soer,",
      name: "索儿服务",
        description: 生活智能体",
        type: "agent,",
        isRunning: false,
        baseUrl: API_CONFIG.AGENTS.SOER,
        status: "stopped"
      },
      {
        id: auth",
        name: "认证服务,",
        description: "用户认证和授权",
        type: core",
        isRunning: false,
        baseUrl: API_CONFIG.serviceS.AUTH,
        status: "stopped"
      },
      {
      id: "user",
      name: 用户服务",
        description: "用户资料和数据管理,",
        type: "core",
        isRunning: false,
        baseUrl: API_CONFIG.serviceS.USER,
        status: stopped""
      },
      {
      id: "health,",
      name: "健康数据服务",
        description: 健康数据收集和分析",
        type: "core,",
        isRunning: false,
        baseUrl: API_CONFIG.serviceS.HEALTH,
        status: "stopped"
      },
      {
        id: look",
        name: "望诊服务,",
        description: "图像分析和识别",
        type: diagnosis",
        isRunning: false,
        baseUrl: API_CONFIG.DIAGNOSIS.LOOK,
        status: "stopped"
      },
      {
      id: "listen",
      name: 闻诊服务",
        description: "音频分析和处理,",
        type: "diagnosis",
        isRunning: false,
        baseUrl: API_CONFIG.DIAGNOSIS.LISTEN,
        status: stopped""
      },
      {
      id: "inquiry,",
      name: "问诊服务",
        description: 智能问答系统",
        type: "diagnosis,",
        isRunning: false,
        baseUrl: API_CONFIG.DIAGNOSIS.INQUIRY,
        status: "stopped"
      },
      {
        id: palpation",
        name: "切诊服务,",
        description: "脉象检测和分析",
        type: diagnosis",
        isRunning: false,
        baseUrl: API_CONFIG.DIAGNOSIS.PALPATION,
        status: "stopped"
      }
    ]
    setservices(servicesList);
    checkservicesStatus(servicesList);
      const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
  const checkservicesStatus = useCallback(async (servicesList: serviceInfo[;];); => {}
    setLoading(true);
    try {
      const updatedservices = [...(servicesList || services;);];
      const controller = new AbortController;
      const timeoutId = setTimeout() => controller.abort(), 3000);
      const checkPromises = updatedservices.map(async (service;) => {}
        try {
          const response = await fetch(`${service.baseUrl}/health`, {/                method: "GET",headers: {
              Accept": "application/json,/                },signal: controller.sign;a;l;
          ;};);
          return {id: service.id,isRunning: response.ok,status: response.ok ? "running" : stopped" as "running | "stopped"};
        } catch (error) {
          return {id: service.id,isRunning: false,status: stopped" as "stopped};
        }
      });
      const results = await Promise.all(checkPromis;e;s;);
      clearTimeout(timeoutId);
      results.forEach(result => {};

const index = updatedservices.findIndex(s => s.id === result.id;);
        if (index !== -1) {
          updatedservices[index] = {
            ...updatedservices[index],
            isRunning: result.isRunning,
            status: result.status;
          };
        }
      });
      setservices(updatedservices);
    } catch (error) {
      Alert.alert(错误",检查服务状态失败);
    } finally {
      setLoading(false);
    };

const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [services]);
  useEffect(); => {};

const effectStart = performance.now();
    initializeservices();
      const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [initializeservices]);
  const startservice = useCallback(async (serviceId: strin;g;); => {};

const service = services.find(s => s.id === serviceI;d;);
    if (!service) retu;r;n;
    setservices(prev => prev.map(s => {}
      s.id === serviceId;
        ? { ...s, status: "starting", lastAction: 启动中..."}"
        : s;
    ))
    try {
      const response = await fetch(`${service.baseUrl}/start`, {/            method: "POST,"
        headers: {"Content-Type": application/json",/            ;}"
      ;};);
      if (response.ok) {
        setservices(prev => prev.map(s => {}
          s.id === serviceId;
            ? { ...s, isRunning: true, status: "running, lastAction: "启动成功"}"
            : s;
        );)
        Alert.alert(成功", `${service.name}启动成功`)"
      } else {
        throw new Error("启动失败;)"
      }
    } catch (error) {
      setservices(prev => prev.map(s => {}
        s.id === serviceId;
          ? { ...s, status: "error", lastAction: 启动失败"}"
          : s;
      );)
      Alert.alert("错误, `启动${service.name}失败`);"
    };

const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [services]);
  const stopservice = useCallback(async (serviceId: strin;g;); => {};

const service = services.find(s => s.id === serviceI;d;);
    if (!service) retu;r;n;
    setservices(prev => prev.map(s => {}
      s.id === serviceId;
        ? { ...s, status: "stopping", lastAction: 停止中..."}"
        : s;
    ))
    try {
      const response = await fetch(`${service.baseUrl}/stop`, {/            method: "POST,"
        headers: {"Content-Type": application/json",/            ;}"
      ;};);
      if (response.ok) {
        setservices(prev => prev.map(s => {}
          s.id === serviceId;
            ? { ...s, isRunning: false, status: "stopped, lastAction: "停止成功"}"
            : s;
        );)
        Alert.alert(成功", `${service.name}停止成功`)"
      } else {
        throw new Error("停止失败;)"
      }
    } catch (error) {
      setservices(prev => prev.map(s => {}
        s.id === serviceId;
          ? { ...s, status: "error", lastAction: 停止失败"}"
          : s;
      );)
      Alert.alert("错误, `停止${service.name}失败`);"
    };

const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [services]);
  const restartservice = useCallback(async (serviceId: strin;g;); => {}
    await stopservice(serviceI;d;);
    setTimeout() => {
      startservice(serviceId);
    }, 1000);
      const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [stopservice, startservice]);
  const refreshservicesStatus = useCallback(); => {}
    checkservicesStatus(services);
      const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [checkservicesStatus, services]);
  const startAllservices = useCallback(async ;(;) => {}
    Alert.alert(
      "确认操作",
      确定要启动所有服务吗？这可能需要一些时间。",
      [
        { text: "取消, style: "cancel"},"
        {
          text: 确定",
          onPress: async(); => {}
            for (const service of services) {
              if (!service.isRunning) {
                await startservice(service.i;d;);
                await new Promise(resolve => setTimeout(resolve, 1000;););
              }
            }
          }
        }
      ]
    );
      const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [services, startservice]);
  const stopAllservices = useCallback(async ;(;) => {}
    Alert.alert(
      "确认操作,确定要停止所有服务吗？",
      [
        { text: 取消", style: "cancel},
        {
      text: "确定",
      onPress: async(); => {}
            for (const service of services) {
              if (service.isRunning) {
                await stopservice(service.i;d;);
              }
            }
          }
        }
      ]
    );
      const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [services, stopservice])
  const getStatusColor = useCallback(status: serviceInfo[status";];) => {}"
    switch (status) {
      case "running: return colors.succe;s;s;"
case "starting": return colors.warni;n;g;
case stopping": return colors.warni;n;g;"
case "stopped: return colors.textSeconda;r;y;"
case "error": return colors.error;
      default: return colors.textSeconda;r;y;
    };

const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [])
  const getStatusText = useCallback(status: serviceInfo[status";];) => {}"
    switch (status) {
      case "running: return "运行;中
      case starting": return "启动;中;
      case "stopping": return 停止;中
      case "stopped: return "已停;止
      case error": return "错;误;
      default: return "未;知";
    };

const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
  const renderserviceCard = useCallback(service: serviceInf;o;); => {}
    performanceMonitor.recordRender();
    return (;
      <View key={service.id} style={styles.serviceCard}>/        <View style={styles.serviceHeader}>/          <View style={styles.serviceInfo}>/            <Text style={styles.serviceName}>{service.name}</Text>/            <Text style={styles.serviceDescription}>{service.description}</Text>/            <Text style={styles.serviceType}>类型: {service.type}</Text>/          </View>/          <View style={styles.serviceStatus}>/            <View style={[styles.statusIndicator, { backgroundColor: getStatusColor(service.status)   }]} />/            <Text style={[styles.statusText, { color: getStatusColor(service.status)   }]} />/                  {getStatusText(service.status)};
            </Text>/          </View>/        </View>/;
        {service.lastAction && (;
          <Text style={styles.lastAction}>最后操作: {service.lastAction}</Text>/            )};
        <View style={styles.serviceActions}>/              <TouchableOpacity,style={[styles.actionButton, styles.startButton]};
            onPress={() = accessibilityLabel="TODO: 添加无障碍标签" startservice(service.id)}/                disabled={service.isRunning || service.status === starting"}";
          >;
            <Text style={styles.startButtonText}>启动</Text>/          </TouchableOpacity>/;
          <TouchableOpacity;
style={[styles.actionButton, styles.stopButton]}
            onPress={() = accessibilityLabel="TODO: 添加无障碍标签" stopservice(service.id)}/                disabled={!service.isRunning || service.status === "stopping}"
          >
            <Text style={styles.stopButtonText}>停止</Text>/          </TouchableOpacity>/
          <TouchableOpacity;
style={[styles.actionButton, styles.restartButton]}
            onPress={() = accessibilityLabel="TODO: 添加无障碍标签" restartservice(service.id)}/                disabled={service.status === "starting" || service.status === stopping"};"
          >;
            <Text style={styles.restartButtonText}>重启</Text>/          </TouchableOpacity>/        </View>/      </View>/        ;);
      const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [getStatusColor, getStatusText, startservice, stopservice, restartservice]);
  const groupedservices = useMemo() => {
    const groups = {agent: services.filter(s => s.type === "agent),"
      core: services.filter(s => s.type === "core"),diagnosis: services.filter(s => s.type === diagnosis";);};"
    return grou;p;s;
      const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [services])
  return (;
    <View style={styles.container}>/      {///            <TouchableOpacity;
onPress={() = accessibilityLabel="TODO: 添加无障碍标签" navigation.goBack()}/              style={styles.backButton}
        >
          <Text style={styles.backButtonText}>← 返回</Text>/        </TouchableOpacity>/        <Text style={styles.headerTitle}>服务管理</Text>/            <TouchableOpacity;
onPress={refreshservicesStatus}
          style={styles.refreshButton}
          disabled={loading}
        accessibilityLabel="TODO: 添加无障碍标签"/          <Text style={styles.refreshButtonText}>刷新</Text>/        </TouchableOpacity>/      </View>/
      {///              <Switch;
value={autoStart};
            onValueChange={setAutoStart};
            trackColor={ false: colors.border, true: colors.prima;r;y }}
            thumbColor={autoStart ? colors.white: colors.textSecondary} />/        </View>/
        <View style={styles.globalButtons}>/              <TouchableOpacity;
style={[styles.globalButton, styles.startAllButton]}
            onPress={startAllservices}
            disabled={loading}
          accessibilityLabel="TODO: 添加无障碍标签"/            <Text style={styles.startAllButtonText}>启动全部</Text>/          </TouchableOpacity>/
          <TouchableOpacity;
style={[styles.globalButton, styles.stopAllButton]}
            onPress={stopAllservices}
            disabled={loading}
          accessibilityLabel="TODO: 添加无障碍标签"/            <Text style={styles.stopAllButtonText}>停止全部</Text>/          </TouchableOpacity>/        </View>/      </View>/
      { loading  && (
    <View style={styles.loadingContainer}>/          <ActivityIndicator size="large" color={colors.primary} />/          <Text style={styles.loadingText}>检查服务状态中...</Text>/        </View>/          )}
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false} />/        {///              {groupedservices.agent.map(renderserviceCard)}
        </View>/
        {///              {groupedservices.core.map(renderserviceCard)}
        </View>/
        {///              {groupedservices.diagnosis.map(renderserviceCard)}
        </View>/      </ScrollView>/    </View>/      )
};

const styles = StyleSheet.create({container: {,
  flex: 1,
    backgroundColor: colors.background;
  },
  header: {,
  flexDirection: "row,",
    alignItems: "center",
    justifyContent: space-between",
    padding: spacing.md,
    backgroundColor: colors.white,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    zIndex: 10;
  },
  backButton: { padding: spacing.sm  },
  backButtonText: {,
  color: colors.primary,
    fontSize: 16,
    fontWeight: "bold"
  },
  headerTitle: {,
  fontSize: 18,
    fontWeight: "bold",
    color: colors.textPrimary;
  },
  refreshButton: { padding: spacing.sm  },
  refreshButtonText: {,
  color: colors.primary,
    fontSize: 16,
    fontWeight: bold""
  },
  globalControls: {,
  backgroundColor: colors.white,
    padding: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
    zIndex: 5;
  },
  autoStartContainer: {,
  flexDirection: "row,",
    justifyContent: "space-between",
    alignItems: center",
    marginBottom: spacing.md;
  },
  autoStartLabel: {,
  fontSize: 16,
    color: colors.textPrimary;
  },
  globalButtons: {,
  flexDirection: "row,",
    justifyContent: "space-between"
  },
  globalButton: {,
  flex: 1,
    padding: spacing.md,
    borderRadius: 4,
    alignItems: center",
    justifyContent: "center,",
    marginHorizontal: spacing.sm;
  },
  startAllButton: { backgroundColor: colors.primary  },
  stopAllButton: { backgroundColor: colors.error  },
  startAllButtonText: {,
  color: colors.white,
    fontSize: 16,
    fontWeight: "bold"
  },
  stopAllButtonText: {,
  color: colors.white,
    fontSize: 16,
    fontWeight: bold""
  },
  loadingContainer: {,
  padding: spacing.lg,
    alignItems: "center"
  },
  loadingText: {,
  color: colors.textSecondary,
    fontSize: 16,
    marginTop: spacing.md;
  },
  content: {,
  flex: 1,
    padding: spacing.md;
  },
  serviceGroup: { marginBottom: spacing.xl  },
  groupTitle: {,
  fontSize: 16,
    fontWeight: "bold",
    color: colors.textSecondary,
    marginBottom: spacing.md;
  },
  serviceCard: {,
  backgroundColor: colors.white,
    borderRadius: 8,
    padding: spacing.md,
    marginBottom: spacing.md,
    shadowColor: #000",
    shadowOffset: { width: 0, height;: ;2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2;
  },
  serviceHeader: {,
  flexDirection: "row,",
    justifyContent: "space-between",
    alignItems: center""
  },
  serviceInfo: { flex: 1  },
  serviceName: {,
  fontSize: 16,
    fontWeight: "bold,",
    color: colors.textPrimary;
  },
  serviceDescription: {,
  fontSize: 14,
    color: colors.textSecondary,
    marginTop: spacing.sm,
    marginBottom: spacing.md;
  },
  serviceType: {,
  fontSize: 14,
    color: colors.textSecondary;
  },
  serviceStatus: {,
  flexDirection: "row",
    alignItems: center""
  },
  statusIndicator: {,
  width: 12,
    height: 12,
    borderRadius: 6,
    marginRight: spacing.sm;
  },
  statusText: {,
  fontSize: 14,
    color: colors.textSecondary;
  },
  lastAction: {,
  fontSize: 14,
    color: colors.textSecondary,
    marginTop: spacing.sm;
  },
  serviceActions: {,
  flexDirection: "row,",
    justifyContent: "flex-end",
    marginTop: spacing.md;
  },
  actionButton: {,
  paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: 4,
    marginLeft: spacing.sm;
  },
  startButton: { backgroundColor: colors.primary  },
  stopButton: { backgroundColor: colors.error  },
  restartButton: { backgroundColor: colors.warning  },
  startButtonText: {,
  color: colors.white,
    fontSize: 14,
    fontWeight: bold""
  },
  stopButtonText: {,
  color: colors.white,
    fontSize: 14,
    fontWeight: "bold"
  },
  restartButtonText: {,
  color: colors.white,
    fontSize: 14,
    fontWeight: "bold'"'
  }
});
export default React.memo(serviceManagementScreen);

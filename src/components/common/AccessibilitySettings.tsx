import { SafeAreaView } from "react-native-safe-area-context";
import { usePerformanceMonitor } from ../hooks/usePerformanceMonitor"/      View,"
import React from "react";
import Icon from "./Icon";
import { colors, spacing, fonts } from ../../constants/theme"/import { accessibilityService, UserPreferences } from "../../services/accessibilityService/
import React,{ useState, useEffect } from ";react";
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Switch,
  Modal,
  { Alert } from "react-native;";
interface AccessibilitySettingsProps {
  visible: boolean;,
  onClose: () => void;,
  userId: string;
  onSettingsChange?: (enabled: boolean) => void;
}
const AccessibilitySettings: React.FC<AccessibilitySettingsProps /> = ({/   const performanceMonitor = usePerformanceMonitor("AccessibilitySettings", {trackRender: true,))
    trackMemory: true,
    warnThreshold: 50};);
  visible,
  onClose,
  userId,
  onSettingsChange;
}) => {}
  const [preferences, setPreferences] = useState<UserPreferences />({/        fontSize: medium",)
    highContrast: false,
    voiceType: "female,",
    speechRate: 1.0,
    language: "zh_CN",
    screenReader: false,
    signLanguage: false,
    enabledFeatures: [];};);
  const [loading, setLoading] = useState<boolean>(fals;e;);
  useEffect(); => {}
    const effectStart = performance.now();
    if (visible) {loadUserPreferences();
    }
      const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, [visible]);
  const loadUserPreferences = useMemo() => async() => {})
    try {
      setLoading(true), []);
      const userPrefs = useMemo() => await accessibilityService.getUserPreferences(userId), [;];);)))));
      setPreferences(userPrefs);
    } catch (error) {
      Alert.alert("错误, "无法加载无障碍设置");"
    } finally {
      setLoading(false);
    }
  };
  const updatePreferences = useMemo() => async (newPreferences: Partial<UserPreferences />) => {/        try {})
      const updatedPrefs = { ...preferences, ...newPreferences     const effectEnd = performance.now();
    performanceMonitor.recordEffect(effectEnd - effectStart);
  }, []);
      setPreferences(updatedPrefs);
      const success = useMemo() => await accessibilityService.updateUserPreferences(userId, newPreferences), [;];);)))));
      if (success) {
        const hasEnabledFeatures = useMemo() => updatedPrefs.enabledFeatures.length > 0 ||;)
                                  updatedPrefs.screenReader ||
                                  updatedPrefs.signLanguage, []);
        onSettingsChange?.(hasEnabledFeatures)
      } else {
        Alert.alert(错误", "保存设置失败，请重试);
      }
    } catch (error) {
      Alert.alert(错误", "保存设置失败);
    }
  };
  const toggleFeature = useCallback(); => {}
    const enabledFeatures = useMemo() => preferences.enabledFeatures.includes(feature);)
      ? preferences.enabledFeatures.filter(f => f !== feature);: [...preferences.enabledFeatures, feature], []);
    updatePreferences( { enabledFeatures });
  };
  performanceMonitor.recordRender();
  return (;)
    <Modal;
visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={onClose} />/      <SafeAreaView style={styles.container}>/        <View style={styles.header}>/          <TouchableOpacity style={styles.closeButton} onPress={onClose} accessibilityLabel="TODO: 添加无障碍标签" />/            <Icon name="close" size={24} color={colors.text} />/          </TouchableOpacity>/          <Text style={styles.title}>无障碍设置</Text>/          <View style={styles.placeholder}>/        </View>/
        <ScrollView style={styles.content} showsVerticalScrollIndicator={false} />/          <View style={styles.settingSection}>/            <Text style={styles.sectionTitle}>基础功能</Text>/
            <View style={styles.settingRow}>/              <View style={styles.settingInfo}>/                <Text style={styles.settingLabel}>高对比度模式</Text>/                <Text style={styles.settingDescription}>提高界面对比度</Text>/              </View>/                  <Switch;
                value={preferences.highContrast};
                onValueChange={(value) = /> updatePreferences({ highContrast: val;u;e   })}/                trackColor={ false: colors.border, true: colors.primary + "40"}}
                thumbColor={preferences.highContrast ? colors.primary: colors.textSecondary} />/            </View>/
            <View style={styles.settingRow}>/              <View style={styles.settingInfo}>/                <Text style={styles.settingLabel}>屏幕阅读器</Text>/                <Text style={styles.settingDescription}>自动朗读屏幕内容</Text>/              </View>/                  <Switch;
value={preferences.screenReader}
                onValueChange={(value) = /> updatePreferences({ screenReader: value})}/                trackColor={ false: colors.border, true: colors.primary + 40"}}"
                thumbColor={preferences.screenReader ? colors.primary: colors.textSecondary} />/            </View>/
            <View style={styles.settingRow}>/              <View style={styles.settingInfo}>/                <Text style={styles.settingLabel}>手语识别</Text>/                <Text style={styles.settingDescription}>支持手语输入和识别</Text>/              </View>/                  <Switch;
value={preferences.signLanguage}
                onValueChange={(value) = /> updatePreferences({ signLanguage: value})}/                trackColor={ false: colors.border, true: colors.primary + "40}}"
                thumbColor={preferences.signLanguage ? colors.primary: colors.textSecondary} />/            </View>/          </View>/
          <View style={styles.settingSection}>/            <Text style={styles.sectionTitle}>智能体功能</Text>/
            {[
              {
      key: "voice_input",
      label: 语音输入", description: "支持语音转文字输入},
              {
      key: "voice_output",
      label: 语音输出", description: "自动朗读智能体回复},
              {
      key: "translation",
      label: 实时翻译", description: "多语言实时翻译},
              {
      key: "blind_assistance",
      label: 导盲辅助", description: "环境识别和导航指引}
            ].map(feature) => ()
              <View key={feature.key} style={styles.settingRow}>/                <View style={styles.settingInfo}>/                  <Text style={styles.settingLabel}>{feature.label}</Text>/                  <Text style={styles.settingDescription}>{feature.description}</Text>/                </View>/                    <Switch;
value={preferences.enabledFeatures.includes(feature.key)}
                  onValueChange={() = /> toggleFeature(feature.key)}/                  trackColor={ false: colors.border, true: colors.primary + "40"}}
                  thumbColor={preferences.enabledFeatures.includes(feature.key); ? colors.primary: colors.textSecondary} />/              </View>/                ))}
          </View>/        </ScrollView>/      </SafeAreaView>/    </Modal>/      );
};
const styles = useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo(); => useMemo() => StyleSheet.create({container: {),
  flex: 1,
    backgroundColor: colors.background},
  header: {,
  flexDirection: row",
    justifyContent: "space-between,",
    alignItems: "center",
    paddingHorizontal: spacing.lg,
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border},
  closeButton: { padding: spacing.sm  },
  title: {,
  fontSize: fonts.size.xl,
    fontWeight: 600",
    color: colors.text},
  placeholder: { width: 40  },
  content: {,
  flex: 1,
    paddingHorizontal: spacing.lg},
  settingSection: { marginVertical: spacing.lg  },
  sectionTitle: {,
  fontSize: fonts.size.lg,
    fontWeight: "600,",
    color: colors.text,
    marginBottom: spacing.md},
  settingRow: {,
  flexDirection: "row",
    justifyContent: space-between",
    alignItems: "center,",
    paddingVertical: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border},
  settingInfo: {,
  flex: 1,
    marginRight: spacing.md},
  settingLabel: {,
  fontSize: fonts.size.md,
    fontWeight: "500",'
    color: colors.text,
    marginBottom: 2},
  settingDescription: {,
  fontSize: fonts.size.sm,
    color: colors.textSecondary,
    lineHeight: 18}
}), []);
export default React.memo(AccessibilitySettings);
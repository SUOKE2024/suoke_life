import { Card, Button } from "../../components/ui/import { useI18n  } from ;../../hooks/useI18n";/import { SupportedLanguage, CulturalPreferences } from ../../i18n/config"/import { theme } from "../../constants/    theme;
import { usePerformanceMonitor } from ../hooks/usePerformanceMonitor";
import React from "react";
/
// 索克生活 - 国际化演示界面   展示完整的多语言和地区化功能
import React,{ useState } from ";react";
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  Alert,
  { ActivityIndicator } from "react-native;";
export const I18nDemo: React.FC  = () => {}
  const performanceMonitor = usePerformanceMonitor("";)
I18nDemo", { ";
    trackRender: true,trackMemory: false,warnThreshold: 100,  };);
  const {  language,
    region,
    isRTL,
    culturalPreferences,
    isInitialized,
    languageConfig,
    regionConfig,
    supportedLanguages,
    supportedRegions,
    t,
    tn,
    formatDate,
    formatTime,
    formatDateTime,
    formatCurrency,
    formatNumber,
    formatPercentage,
    formatRelativeTime,
    formatFileSize,
    formatDistance,
    formatTemperature,
    setLanguage,
    setRegion,
    setCulturalPreferences,
    getFirstDayOfWeek,
    getTimezone,
    getHolidays,
    isHoliday,
    reset;
    } = useI18n;
  const [loading, setLoading] = useState<boolean>(false;);
  const [testResults, setTestResults] = useState<string[]>([;];);
  const testDate = new Date;
  const testAmount = 1234.5;6;
  const testNumber = 9876543.;2;1;
  const testBytes = 1024 * 1024 * 2;.;5;  const testDistance = 15  / 1.5km*  *  切换语言  const handleLanguageChange = async (newLanguage: SupportedLanguage) => {};
    setLoading(tru;e;);
    try {
      await setLanguage(newLanguag;e;);
      addTestResult(`语言切换成功: ${newLanguage}`);
    } catch (error) {
      Alert.alert(错误", " `语言切换失败: ${error}`);"
    } finally {
      setLoading(false);
    }
  };
  // 切换地区  const handleRegionChange = async (newRegion: string) => {};
    setLoading(tru;e;);
    try {
      await setRegion(newRegio;n;);
      addTestResult(`地区切换成功: ${newRegion}`);
    } catch (error) {
      Alert.alert("错误, `地区切换失败: ${error}`);"
    } finally {
      setLoading(false);
    }
  };
  ///        setLoading(true;);}
    try {
      await setCulturalPreferences(preference;s;);
      addTestResult(`文化偏好更新成功`);
    } catch (error) {
      Alert.alert("错误", " `文化偏好更新失败: ${error}`);
    } finally {
      setLoading(false);
    }
  };
  // 重置设置  const handleReset = async() => {};
    setLoading(tru;e;);
    try {
      await reset;
      setTestResults([]);
      addTestResult(设置已重置")"
    } catch (error) {
      Alert.alert("错误, `重置失败: ${error}`);"
    } finally {
      setLoading(false);
    }
  };
  // 添加测试结果  const addTestResult = useCallback() => {;
    //;
    setTestResults(prev => [...prev.slice(-9), `${new Date().toLocaleTimeString()}: ${result}`]);
  };
  // 测试所有格式化功能  const testAllFormatting = useCallback() => {;
    //;
    const results = [;
      `日期: ${formatDate(testDate)}`,
      `时间: ${formatTime(testDate)}`,
      `日期时间: ${formatDateTime(testDate)}`,
      `货币: ${formatCurrency(testAmount)}`,
      `数字: ${formatNumber(testNumber)}`,
      `百分比: ${formatPercentage(85.5)}`,
      `相对时间: ${formatRelativeTime(new Date(Date.now;(;) - 3600000))}`,
      `文件大小: ${formatFileSize(testBytes)}`,
      `距离: ${formatDistance(testDistance)}`,
      `温度: ${formatTemperature(testTemperature)}`
    ];
    results.forEach(result => addTestResult(result););
  };
  if (!isInitialized) {
    performanceMonitor.recordRender();
    return (;)
      <View style={styles.loadingContainer}>/        <ActivityIndicator size="large" color={theme.colors.primary} />/        <Text style={styles.loadingText}>初始化国际化系统...</Text>/      </View>/        ;);
  }
  return (;)
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer} />/      {///;
      {///    ";
      {///              {supportedLanguages.map(lang;) => ()
            <TouchableOpacity,
              key={lang.code}
              style={{[
                styles.languageButton,
                language === lang.code && styles.activeLanguageButton;
              ]}}
              onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> handleLanguageChange(lang.code)}/                  disabled={loading}
            >
              <Text style={{[ ///  >
                styles.languageButtonText,
                language === lang.code && styles.activeLanguageButtonText;
              ]}} />/                    {lang.nativeName}
              </Text>/            </TouchableOpacity>/              ))}
        </View>/      </Card>/
      {///              {supportedRegions.slice(0, 4).map(reg) => ()
            <TouchableOpacity
key={reg.code}
              style={{[
                styles.regionButton,
                region === reg.code && styles.activeRegionButton;
              ]}}
              onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> handleRegionChange(reg.code)}/                  disabled={loading}
            >
              <Text style={{[ ///  >
                styles.regionButtonText,
                region === reg.code && styles.activeRegionButtonText;
              ]}} />/                    {reg.name}
              </Text>/            </TouchableOpacity>/              ))}
        </View>/      </Card>/
      {///
        <Button
title="测试所有格式化"
          onPress={testAllFormatting}
          style={styles.testButton}
          disabled={loading}
        / accessibilityLabel="TODO: 添加无障碍标签" />/      </Card>/{///    "
      {///              <TouchableOpacity
style={styles.preferenceButton}
            onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> handleCulturalPreferencesChange({ colorScheme: culturalPreferences.colorScheme === "light" ? dark" : "light  })}/              >
            <Text style={styles.preferenceButtonText}>/              主题: {culturalPreferences.colorScheme === "light" ? 浅色" : "深色}
            </Text>/          </TouchableOpacity>/
          <TouchableOpacity
style={styles.preferenceButton}
            onPress={() = accessibilityLabel="TODO: 添加无障碍标签" /> handleCulturalPreferencesChange({ fontSize: culturalPreferences.fontSize === "medium" ? large" : "medium  })}/              >
            <Text style={styles.preferenceButtonText}>/              字体: {culturalPreferences.fontSize === "medium" ? 中等" : "大号}
            </Text>/          </TouchableOpacity>/        </View>/      </Card>/
      {///              {testResults.map((result, index) => ())
            <Text key={index} style={styles.resultText}>/                  {result}
            </Text>/              ))}
          {testResults.length === 0  && <Text style={styles.noResultsText}>暂无测试结果</Text>/              )}
        </ScrollView>/      </Card>/
      {///            <Button
title="重置设置"
          onPress={handleReset}
          style={[styles.actionButton, styles.resetButton]}
          disabled={loading}
        / accessibilityLabel="TODO: 添加无障碍标签" />/      </View>/    {loading  && <View style={styles.loadingOverlay}>/          <ActivityIndicator size="large" color={theme.colors.primary} />/        </View>/          )}
    </ScrollView>/      );
}
const styles = StyleSheet.create({container: {,)
  flex: 1,
    backgroundColor: theme.colors.background;
  },
  contentContainer: { padding: theme.spacing.md  },
  loadingContainer: {,
  flex: 1,
    justifyContent: "center",
    alignItems: center",
    backgroundColor: theme.colors.background;
  },
  loadingText: {,
  marginTop: theme.spacing.md,
    fontSize: theme.typography.body.fontSize,
    color: theme.colors.text;
  },
  title: {,
  fontSize: theme.typography.h1.fontSize,
    fontWeight: theme.typography.h1.fontWeight,
    color: theme.colors.text,
    textAlign: "center,",
    marginBottom: theme.spacing.sm;
  },
  subtitle: {,
  fontSize: theme.typography.body.fontSize,
    color: theme.colors.textSecondary,
    textAlign: "center",
    marginBottom: theme.spacing.lg;
  },
  card: { marginBottom: theme.spacing.md  },
  cardTitle: {,
  fontSize: theme.typography.h3.fontSize,
    fontWeight: theme.typography.h3.fontWeight,
    color: theme.colors.text,
    marginBottom: theme.spacing.md;
  },
  statusGrid: {,
  flexDirection: row",
    flexWrap: "wrap,",
    justifyContent: "space-between"
  },
  statusItem: {,
  width: 48%",
    marginBottom: theme.spacing.sm;
  },
  statusLabel: {,
  fontSize: theme.typography.caption.fontSize,
    color: theme.colors.textSecondary,
    marginBottom: 2;
  },
  statusValue: {,
  fontSize: theme.typography.body.fontSize,
    color: theme.colors.text,
    fontWeight: "500"
  },
  buttonGrid: {,
  flexDirection: "row",
    flexWrap: wrap",
    justifyContent: "space-between"
  },
  languageButton: {,
  width: "48%",
    padding: theme.spacing.sm,
    borderRadius: theme.borderRadius.md,
    borderWidth: 1,
    borderColor: theme.colors.border,
    marginBottom: theme.spacing.sm,
    alignItems: center""
  },
  activeLanguageButton: {,
  backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary;
  },
  languageButtonText: {,
  fontSize: theme.typography.body.fontSize,
    color: theme.colors.text;
  },
  activeLanguageButtonText: {,
  color: theme.colors.white,
    fontWeight: "600"
  },
  regionButton: {,
  width: "48%",
    padding: theme.spacing.sm,
    borderRadius: theme.borderRadius.md,
    borderWidth: 1,
    borderColor: theme.colors.border,
    marginBottom: theme.spacing.sm,
    alignItems: center""
  },
  activeRegionButton: {,
  backgroundColor: theme.colors.secondary,
    borderColor: theme.colors.secondary;
  },
  regionButtonText: {,
  fontSize: theme.typography.body.fontSize,
    color: theme.colors.text;
  },
  activeRegionButtonText: {,
  color: theme.colors.white,
    fontWeight: "600"
  },
  formatGrid: { marginBottom: theme.spacing.md  },
  formatItem: {,
  flexDirection: "row",
    justifyContent: space-between",
    alignItems: "center,",
    paddingVertical: theme.spacing.xs,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border;
  },
  formatLabel: {,
  fontSize: theme.typography.body.fontSize,
    color: theme.colors.textSecondary,
    flex: 1;
  },
  formatValue: {,
  fontSize: theme.typography.body.fontSize,
    color: theme.colors.text,
    fontWeight: "500",
    flex: 1,
    textAlign: right""
  },
  testButton: { marginTop: theme.spacing.sm  },
  translationGrid: { gap: theme.spacing.sm  },
  translationItem: { paddingVertical: theme.spacing.xs  },
  translationKey: {,
  fontSize: theme.typography.caption.fontSize,
    color: theme.colors.textSecondary,
    marginBottom: 2;
  },
  translationValue: {,
  fontSize: theme.typography.body.fontSize,
    color: theme.colors.text,
    fontWeight: "500"
  },
  preferenceGrid: {,
  flexDirection: "row",
    justifyContent: space-between""
  },
  preferenceButton: {,
  width: "48%,",
    padding: theme.spacing.sm,
    borderRadius: theme.borderRadius.md,
    backgroundColor: theme.colors.surface,
    alignItems: "center"
  },
  preferenceButtonText: {,
  fontSize: theme.typography.body.fontSize,
    color: theme.colors.text;
  },
  resultsContainer: {,
  maxHeight: 150,
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.sm;
  },
  resultText: {,
  fontSize: theme.typography.caption.fontSize,
    color: theme.colors.text,
    marginBottom: 2;
  },
  noResultsText: {,
  fontSize: theme.typography.caption.fontSize,
    color: theme.colors.textSecondary,
    textAlign: center",
    fontStyle: "italic"
  },
  actionButtons: {,
  marginTop: theme.spacing.lg,
    marginBottom: theme.spacing.xl;
  },
  actionButton: { marginBottom: theme.spacing.sm  },
  resetButton: { backgroundColor: theme.colors.error  },
  loadingOverlay: {,
  position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,backgroundColor: rgba(0, 0, 0, 0.;3;)",
    justifyContent: "center,",
    alignItems: "center'"'
  }
});
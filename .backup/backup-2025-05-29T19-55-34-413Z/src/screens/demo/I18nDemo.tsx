import {
import { Card, Button } from '../../components/ui';
import { useI18n } from '../../hooks/useI18n';
import { SupportedLanguage, CulturalPreferences } from '../../i18n/config';
import { theme } from '../../constants/theme';


/**
 * 索克生活 - 国际化演示界面
 * 展示完整的多语言和地区化功能
 */

import React, { useState } from 'react';
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  Alert,
  ActivityIndicator,
} from 'react-native';

export const I18nDemo: React.FC = () => {
  const {
    // 当前状态
    language,
    region,
    isRTL,
    culturalPreferences,
    isInitialized,
    
    // 配置信息
    languageConfig,
    regionConfig,
    supportedLanguages,
    supportedRegions,
    
    // 翻译函数
    t,
    tn,
    
    // 格式化函数
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
    
    // 设置函数
    setLanguage,
    setRegion,
    setCulturalPreferences,
    
    // 工具函数
    getFirstDayOfWeek,
    getTimezone,
    getHolidays,
    isHoliday,
    reset,
  } = useI18n();

  const [loading, setLoading] = useState(false);
  const [testResults, setTestResults] = useState<string[]>([]);

  // 测试数据
  const testDate = new Date();
  const testAmount = 1234.56;
  const testNumber = 9876543.21;
  const testBytes = 1024 * 1024 * 2.5; // 2.5MB
  const testDistance = 1500; // 1.5km
  const testTemperature = 25; // 25°C

  /**
   * 切换语言
   */
  const handleLanguageChange = async (newLanguage: SupportedLanguage) => {
    setLoading(true);
    try {
      await setLanguage(newLanguage);
      addTestResult(`语言切换成功: ${newLanguage}`);
    } catch (error) {
      Alert.alert('错误', `语言切换失败: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  /**
   * 切换地区
   */
  const handleRegionChange = async (newRegion: string) => {
    setLoading(true);
    try {
      await setRegion(newRegion);
      addTestResult(`地区切换成功: ${newRegion}`);
    } catch (error) {
      Alert.alert('错误', `地区切换失败: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  /**
   * 更新文化偏好
   */
  const handleCulturalPreferencesChange = async (preferences: Partial<CulturalPreferences>) => {
    setLoading(true);
    try {
      await setCulturalPreferences(preferences);
      addTestResult(`文化偏好更新成功`);
    } catch (error) {
      Alert.alert('错误', `文化偏好更新失败: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  /**
   * 重置设置
   */
  const handleReset = async () => {
    setLoading(true);
    try {
      await reset();
      setTestResults([]);
      addTestResult('设置已重置');
    } catch (error) {
      Alert.alert('错误', `重置失败: ${error}`);
    } finally {
      setLoading(false);
    }
  };

  /**
   * 添加测试结果
   */
  const addTestResult = useCallback( (result: string) => {, []);
    setTestResults(prev => [...prev.slice(-9), `${new Date().toLocaleTimeString()}: ${result}`]);
  };

  /**
   * 测试所有格式化功能
   */
  const testAllFormatting = useCallback( () => {, []);
    const results = [
      `日期: ${formatDate(testDate)}`,
      `时间: ${formatTime(testDate)}`,
      `日期时间: ${formatDateTime(testDate)}`,
      `货币: ${formatCurrency(testAmount)}`,
      `数字: ${formatNumber(testNumber)}`,
      `百分比: ${formatPercentage(85.5)}`,
      `相对时间: ${formatRelativeTime(new Date(Date.now() - 3600000))}`,
      `文件大小: ${formatFileSize(testBytes)}`,
      `距离: ${formatDistance(testDistance)}`,
      `温度: ${formatTemperature(testTemperature)}`,
    ];
    
    results.forEach(result => addTestResult(result));
  };

  if (!isInitialized) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color={theme.colors.primary} />
        <Text style={styles.loadingText}>初始化国际化系统...</Text>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.contentContainer}>
      {/* 标题 */}
      <Text style={styles.title}>🌍 国际化演示</Text>
      <Text style={styles.subtitle}>完整的多语言和地区化功能展示</Text>

      {/* 当前状态 */}
      <Card style={styles.card}>
        <Text style={styles.cardTitle}>📊 当前状态</Text>
        <View style={styles.statusGrid}>
          <View style={styles.statusItem}>
            <Text style={styles.statusLabel}>语言:</Text>
            <Text style={styles.statusValue}>{languageConfig.nativeName}</Text>
          </View>
          <View style={styles.statusItem}>
            <Text style={styles.statusLabel}>地区:</Text>
            <Text style={styles.statusValue}>{regionConfig.name}</Text>
          </View>
          <View style={styles.statusItem}>
            <Text style={styles.statusLabel}>RTL:</Text>
            <Text style={styles.statusValue}>{isRTL ? '是' : '否'}</Text>
          </View>
          <View style={styles.statusItem}>
            <Text style={styles.statusLabel}>时区:</Text>
            <Text style={styles.statusValue}>{getTimezone()}</Text>
          </View>
        </View>
      </Card>

      {/* 语言切换 */}
      <Card style={styles.card}>
        <Text style={styles.cardTitle}>🗣️ 语言切换</Text>
        <View style={styles.buttonGrid}>
          {supportedLanguages.map((lang) => (
            <TouchableOpacity
              key={lang.code}
              style={[
                styles.languageButton,
                language === lang.code && styles.activeLanguageButton,
              ]}
              onPress={() => handleLanguageChange(lang.code)}
              disabled={loading}
            >
              <Text style={[
                styles.languageButtonText,
                language === lang.code && styles.activeLanguageButtonText,
              ]}>
                {lang.nativeName}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </Card>

      {/* 地区切换 */}
      <Card style={styles.card}>
        <Text style={styles.cardTitle}>🌏 地区切换</Text>
        <View style={styles.buttonGrid}>
          {supportedRegions.slice(0, 4).map((reg) => (
            <TouchableOpacity
              key={reg.code}
              style={[
                styles.regionButton,
                region === reg.code && styles.activeRegionButton,
              ]}
              onPress={() => handleRegionChange(reg.code)}
              disabled={loading}
            >
              <Text style={[
                styles.regionButtonText,
                region === reg.code && styles.activeRegionButtonText,
              ]}>
                {reg.name}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </Card>

      {/* 格式化演示 */}
      <Card style={styles.card}>
        <Text style={styles.cardTitle}>📝 格式化演示</Text>
        <View style={styles.formatGrid}>
          <View style={styles.formatItem}>
            <Text style={styles.formatLabel}>日期:</Text>
            <Text style={styles.formatValue}>{formatDate(testDate)}</Text>
          </View>
          <View style={styles.formatItem}>
            <Text style={styles.formatLabel}>时间:</Text>
            <Text style={styles.formatValue}>{formatTime(testDate)}</Text>
          </View>
          <View style={styles.formatItem}>
            <Text style={styles.formatLabel}>货币:</Text>
            <Text style={styles.formatValue}>{formatCurrency(testAmount)}</Text>
          </View>
          <View style={styles.formatItem}>
            <Text style={styles.formatLabel}>数字:</Text>
            <Text style={styles.formatValue}>{formatNumber(testNumber)}</Text>
          </View>
          <View style={styles.formatItem}>
            <Text style={styles.formatLabel}>距离:</Text>
            <Text style={styles.formatValue}>{formatDistance(testDistance)}</Text>
          </View>
          <View style={styles.formatItem}>
            <Text style={styles.formatLabel}>温度:</Text>
            <Text style={styles.formatValue}>{formatTemperature(testTemperature)}</Text>
          </View>
        </View>
        
        <Button
          title="测试所有格式化"
          onPress={testAllFormatting}
          style={styles.testButton}
          disabled={loading}
        />
      </Card>

      {/* 翻译演示 */}
      <Card style={styles.card}>
        <Text style={styles.cardTitle}>🔤 翻译演示</Text>
        <View style={styles.translationGrid}>
          <View style={styles.translationItem}>
            <Text style={styles.translationKey}>common.welcome:</Text>
            <Text style={styles.translationValue}>{t('common.welcome')}</Text>
          </View>
          <View style={styles.translationItem}>
            <Text style={styles.translationKey}>common.loading:</Text>
            <Text style={styles.translationValue}>{t('common.loading')}</Text>
          </View>
          <View style={styles.translationItem}>
            <Text style={styles.translationKey}>复数测试:</Text>
            <Text style={styles.translationValue}>
              {tn('common.items', 1)} / {tn('common.items', 5)}
            </Text>
          </View>
        </View>
      </Card>

      {/* 文化偏好 */}
      <Card style={styles.card}>
        <Text style={styles.cardTitle}>🎨 文化偏好</Text>
        <View style={styles.preferenceGrid}>
          <TouchableOpacity
            style={styles.preferenceButton}
            onPress={() => handleCulturalPreferencesChange({ 
              colorScheme: culturalPreferences.colorScheme === 'light' ? 'dark' : 'light', 
            })}
          >
            <Text style={styles.preferenceButtonText}>
              主题: {culturalPreferences.colorScheme === 'light' ? '浅色' : '深色'}
            </Text>
          </TouchableOpacity>
          
          <TouchableOpacity
            style={styles.preferenceButton}
            onPress={() => handleCulturalPreferencesChange({ 
              fontSize: culturalPreferences.fontSize === 'medium' ? 'large' : 'medium', 
            })}
          >
            <Text style={styles.preferenceButtonText}>
              字体: {culturalPreferences.fontSize === 'medium' ? '中等' : '大号'}
            </Text>
          </TouchableOpacity>
        </View>
      </Card>

      {/* 测试结果 */}
      <Card style={styles.card}>
        <Text style={styles.cardTitle}>📋 测试结果</Text>
        <ScrollView style={styles.resultsContainer} nestedScrollEnabled>
          {testResults.map((result, index) => (
            <Text key={index} style={styles.resultText}>
              {result}
            </Text>
          ))}
          {testResults.length === 0 && (
            <Text style={styles.noResultsText}>暂无测试结果</Text>
          )}
        </ScrollView>
      </Card>

      {/* 操作按钮 */}
      <View style={styles.actionButtons}>
        <Button
          title="重置设置"
          onPress={handleReset}
          style={[styles.actionButton, styles.resetButton]}
          disabled={loading}
        />
      </View>

      {loading && (
        <View style={styles.loadingOverlay}>
          <ActivityIndicator size="large" color={theme.colors.primary} />
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: theme.colors.background,
  },
  contentContainer: {
    padding: theme.spacing.md,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: theme.colors.background,
  },
  loadingText: {
    marginTop: theme.spacing.md,
    fontSize: theme.typography.body.fontSize,
    color: theme.colors.text,
  },
  title: {
    fontSize: theme.typography.h1.fontSize,
    fontWeight: theme.typography.h1.fontWeight,
    color: theme.colors.text,
    textAlign: 'center',
    marginBottom: theme.spacing.sm,
  },
  subtitle: {
    fontSize: theme.typography.body.fontSize,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    marginBottom: theme.spacing.lg,
  },
  card: {
    marginBottom: theme.spacing.md,
  },
  cardTitle: {
    fontSize: theme.typography.h3.fontSize,
    fontWeight: theme.typography.h3.fontWeight,
    color: theme.colors.text,
    marginBottom: theme.spacing.md,
  },
  statusGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statusItem: {
    width: '48%',
    marginBottom: theme.spacing.sm,
  },
  statusLabel: {
    fontSize: theme.typography.caption.fontSize,
    color: theme.colors.textSecondary,
    marginBottom: 2,
  },
  statusValue: {
    fontSize: theme.typography.body.fontSize,
    color: theme.colors.text,
    fontWeight: '500',
  },
  buttonGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  languageButton: {
    width: '48%',
    padding: theme.spacing.sm,
    borderRadius: theme.borderRadius.md,
    borderWidth: 1,
    borderColor: theme.colors.border,
    marginBottom: theme.spacing.sm,
    alignItems: 'center',
  },
  activeLanguageButton: {
    backgroundColor: theme.colors.primary,
    borderColor: theme.colors.primary,
  },
  languageButtonText: {
    fontSize: theme.typography.body.fontSize,
    color: theme.colors.text,
  },
  activeLanguageButtonText: {
    color: theme.colors.white,
    fontWeight: '600',
  },
  regionButton: {
    width: '48%',
    padding: theme.spacing.sm,
    borderRadius: theme.borderRadius.md,
    borderWidth: 1,
    borderColor: theme.colors.border,
    marginBottom: theme.spacing.sm,
    alignItems: 'center',
  },
  activeRegionButton: {
    backgroundColor: theme.colors.secondary,
    borderColor: theme.colors.secondary,
  },
  regionButtonText: {
    fontSize: theme.typography.body.fontSize,
    color: theme.colors.text,
  },
  activeRegionButtonText: {
    color: theme.colors.white,
    fontWeight: '600',
  },
  formatGrid: {
    marginBottom: theme.spacing.md,
  },
  formatItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: theme.spacing.xs,
    borderBottomWidth: 1,
    borderBottomColor: theme.colors.border,
  },
  formatLabel: {
    fontSize: theme.typography.body.fontSize,
    color: theme.colors.textSecondary,
    flex: 1,
  },
  formatValue: {
    fontSize: theme.typography.body.fontSize,
    color: theme.colors.text,
    fontWeight: '500',
    flex: 1,
    textAlign: 'right',
  },
  testButton: {
    marginTop: theme.spacing.sm,
  },
  translationGrid: {
    gap: theme.spacing.sm,
  },
  translationItem: {
    paddingVertical: theme.spacing.xs,
  },
  translationKey: {
    fontSize: theme.typography.caption.fontSize,
    color: theme.colors.textSecondary,
    marginBottom: 2,
  },
  translationValue: {
    fontSize: theme.typography.body.fontSize,
    color: theme.colors.text,
    fontWeight: '500',
  },
  preferenceGrid: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  preferenceButton: {
    width: '48%',
    padding: theme.spacing.sm,
    borderRadius: theme.borderRadius.md,
    backgroundColor: theme.colors.surface,
    alignItems: 'center',
  },
  preferenceButtonText: {
    fontSize: theme.typography.body.fontSize,
    color: theme.colors.text,
  },
  resultsContainer: {
    maxHeight: 150,
    backgroundColor: theme.colors.surface,
    borderRadius: theme.borderRadius.md,
    padding: theme.spacing.sm,
  },
  resultText: {
    fontSize: theme.typography.caption.fontSize,
    color: theme.colors.text,
    marginBottom: 2,
  },
  noResultsText: {
    fontSize: theme.typography.caption.fontSize,
    color: theme.colors.textSecondary,
    textAlign: 'center',
    fontStyle: 'italic',
  },
  actionButtons: {
    marginTop: theme.spacing.lg,
    marginBottom: theme.spacing.xl,
  },
  actionButton: {
    marginBottom: theme.spacing.sm,
  },
  resetButton: {
    backgroundColor: theme.colors.error,
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.3)',
    justifyContent: 'center',
    alignItems: 'center',
  },
}); 
/**
 * 游戏设置模态框组件
 * Game Settings Modal Component
 */

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Modal,
  ScrollView,
  TouchableOpacity,
  Switch,
  Alert
} from 'react-native';
import Icon from 'react-native-vector-icons/MaterialIcons';
import { GameSettings, MazeDifficulty } from '../../types/maze';

interface GameSettingsModalProps {
  visible: boolean;
  settings: GameSettings | null;
  onClose: () => void;
  onSave: (settings: GameSettings) => void;
}

const GameSettingsModal: React.FC<GameSettingsModalProps> = ({
  visible,
  settings,
  onClose,
  onSave
}) => {
  const [localSettings, setLocalSettings] = useState<GameSettings>({
    soundEnabled: true,
    musicEnabled: true,
    vibrationEnabled: true,
    autoSave: true,
    difficulty: MazeDifficulty.NORMAL,
    showHints: true,
    animationSpeed: 'normal',
    colorScheme: 'auto'
  });

  /**
   * 初始化设置
   */
  useEffect(() => {
    if (settings) {
      setLocalSettings(settings);
    }
  }, [settings]);

  /**
   * 更新设置项
   */
  const updateSetting = <K extends keyof GameSettings>(
    key: K,
    value: GameSettings[K]
  ) => {
    setLocalSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  /**
   * 保存设置
   */
  const handleSave = () => {
    onSave(localSettings);
    onClose();
  };

  /**
   * 重置为默认设置
   */
  const handleReset = () => {
    Alert.alert(
      '重置设置',
      '确定要重置为默认设置吗？',
      [
        { text: '取消', style: 'cancel' },
        {
          text: '确定',
          onPress: () => {
            setLocalSettings({
              soundEnabled: true,
              musicEnabled: true,
              vibrationEnabled: true,
              autoSave: true,
              difficulty: MazeDifficulty.NORMAL,
              showHints: true,
              animationSpeed: 'normal',
              colorScheme: 'auto'
            });
          }
        }
      ]
    );
  };

  /**
   * 渲染开关设置项
   */
  const renderSwitchSetting = (
    title: string,
    description: string,
    value: boolean,
    onValueChange: (value: boolean) => void,
    iconName: string,
    iconColor: string = '#4CAF50'
  ) => (
    <View style={styles.settingItem}>
      <View style={styles.settingLeft}>
        <Icon name={iconName} size={24} color={iconColor} />
        <View style={styles.settingText}>
          <Text style={styles.settingTitle}>{title}</Text>
          <Text style={styles.settingDescription}>{description}</Text>
        </View>
      </View>
      <Switch
        value={value}
        onValueChange={onValueChange}
        trackColor={{ false: '#E0E0E0', true: '#C8E6C9' }}
        thumbColor={value ? '#4CAF50' : '#F5F5F5'}
      />
    </View>
  );

  /**
   * 渲染选择设置项
   */
  const renderSelectSetting = (
    title: string,
    description: string,
    value: string,
    options: { label: string; value: string }[],
    onValueChange: (value: string) => void,
    iconName: string,
    iconColor: string = '#4CAF50'
  ) => (
    <View style={styles.settingItem}>
      <View style={styles.settingLeft}>
        <Icon name={iconName} size={24} color={iconColor} />
        <View style={styles.settingText}>
          <Text style={styles.settingTitle}>{title}</Text>
          <Text style={styles.settingDescription}>{description}</Text>
        </View>
      </View>
      <View style={styles.selectContainer}>
        {options.map((option) => (
          <TouchableOpacity
            key={option.value}
            style={[
              styles.selectOption,
              value === option.value && styles.selectedOption
            ]}
            onPress={() => onValueChange(option.value)}
          >
            <Text style={[
              styles.selectOptionText,
              value === option.value && styles.selectedOptionText
            ]}>
              {option.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={onClose}
    >
      <View style={styles.container}>
        {/* 头部 */}
        <View style={styles.header}>
          <View style={styles.headerLeft}>
            <Icon name="settings" size={24} color="#4CAF50" />
            <Text style={styles.headerTitle}>游戏设置</Text>
          </View>
          <TouchableOpacity style={styles.closeButton} onPress={onClose}>
            <Icon name="close" size={24} color="#666" />
          </TouchableOpacity>
        </View>

        {/* 内容区域 */}
        <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
          {/* 音频设置 */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>音频设置</Text>
            
            {renderSwitchSetting(
              '音效',
              '开启游戏音效',
              localSettings.soundEnabled,
              (value) => updateSetting('soundEnabled', value),
              'volume-up',
              '#FF9800'
            )}

            {renderSwitchSetting(
              '背景音乐',
              '开启背景音乐',
              localSettings.musicEnabled,
              (value) => updateSetting('musicEnabled', value),
              'music-note',
              '#9C27B0'
            )}

            {renderSwitchSetting(
              '震动反馈',
              '开启触觉反馈',
              localSettings.vibrationEnabled,
              (value) => updateSetting('vibrationEnabled', value),
              'vibration',
              '#607D8B'
            )}
          </View>

          {/* 游戏设置 */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>游戏设置</Text>

            {renderSelectSetting(
              '难度等级',
              '选择游戏难度',
              localSettings.difficulty,
              [
                { label: '简单', value: MazeDifficulty.EASY },
                { label: '普通', value: MazeDifficulty.NORMAL },
                { label: '困难', value: MazeDifficulty.HARD },
                { label: '专家', value: MazeDifficulty.EXPERT }
              ],
              (value) => updateSetting('difficulty', value as MazeDifficulty),
              'trending-up',
              '#F44336'
            )}

            {renderSwitchSetting(
              '显示提示',
              '显示游戏提示信息',
              localSettings.showHints,
              (value) => updateSetting('showHints', value),
              'lightbulb-outline',
              '#FFC107'
            )}

            {renderSwitchSetting(
              '自动保存',
              '自动保存游戏进度',
              localSettings.autoSave,
              (value) => updateSetting('autoSave', value),
              'save',
              '#2196F3'
            )}
          </View>

          {/* 界面设置 */}
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>界面设置</Text>

            {renderSelectSetting(
              '动画速度',
              '调整动画播放速度',
              localSettings.animationSpeed,
              [
                { label: '慢速', value: 'slow' },
                { label: '正常', value: 'normal' },
                { label: '快速', value: 'fast' }
              ],
              (value) => updateSetting('animationSpeed', value as 'slow' | 'normal' | 'fast'),
              'speed',
              '#795548'
            )}

            {renderSelectSetting(
              '主题模式',
              '选择界面主题',
              localSettings.colorScheme,
              [
                { label: '浅色', value: 'light' },
                { label: '深色', value: 'dark' },
                { label: '自动', value: 'auto' }
              ],
              (value) => updateSetting('colorScheme', value as 'light' | 'dark' | 'auto'),
              'palette',
              '#673AB7'
            )}
          </View>

          {/* 底部间距 */}
          <View style={styles.bottomSpacing} />
        </ScrollView>

        {/* 底部操作栏 */}
        <View style={styles.footer}>
          <TouchableOpacity
            style={styles.resetButton}
            onPress={handleReset}
          >
            <Icon name="refresh" size={20} color="#FF5722" />
            <Text style={styles.resetButtonText}>重置</Text>
          </TouchableOpacity>

          <View style={styles.actionButtons}>
            <TouchableOpacity
              style={styles.cancelButton}
              onPress={onClose}
            >
              <Text style={styles.cancelButtonText}>取消</Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={styles.saveButton}
              onPress={handleSave}
            >
              <Icon name="check" size={20} color="#FFFFFF" />
              <Text style={styles.saveButtonText}>保存</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#E0E0E0',
    backgroundColor: '#F8F9FA',
  },
  headerLeft: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#4CAF50',
    marginLeft: 8,
  },
  closeButton: {
    padding: 8,
  },
  content: {
    flex: 1,
    paddingHorizontal: 16,
  },
  section: {
    marginVertical: 16,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#2E7D32',
    marginBottom: 12,
    paddingLeft: 4,
  },
  settingItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 16,
    paddingHorizontal: 16,
    backgroundColor: '#F8F9FA',
    borderRadius: 12,
    marginBottom: 8,
  },
  settingLeft: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
  },
  settingText: {
    marginLeft: 12,
    flex: 1,
  },
  settingTitle: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333',
    marginBottom: 2,
  },
  settingDescription: {
    fontSize: 14,
    color: '#666',
  },
  selectContainer: {
    flexDirection: 'row',
    marginLeft: 12,
  },
  selectOption: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    backgroundColor: '#E0E0E0',
    marginLeft: 4,
  },
  selectedOption: {
    backgroundColor: '#4CAF50',
  },
  selectOptionText: {
    fontSize: 12,
    color: '#666',
    fontWeight: '500',
  },
  selectedOptionText: {
    color: '#FFFFFF',
  },
  bottomSpacing: {
    height: 20,
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderTopWidth: 1,
    borderTopColor: '#E0E0E0',
    backgroundColor: '#F8F9FA',
  },
  resetButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#FF5722',
  },
  resetButtonText: {
    fontSize: 14,
    color: '#FF5722',
    marginLeft: 4,
    fontWeight: '500',
  },
  actionButtons: {
    flexDirection: 'row',
  },
  cancelButton: {
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
    marginRight: 8,
  },
  cancelButtonText: {
    fontSize: 16,
    color: '#666',
    fontWeight: '500',
  },
  saveButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 8,
    backgroundColor: '#4CAF50',
  },
  saveButtonText: {
    fontSize: 16,
    color: '#FFFFFF',
    marginLeft: 4,
    fontWeight: '500',
  },
});

export default GameSettingsModal; 
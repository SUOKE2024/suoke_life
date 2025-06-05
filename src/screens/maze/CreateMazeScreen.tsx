import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  Switch,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useNavigation } from '@react-navigation/native';
import Icon from '../../components/common/Icon';
import { colors } from '../../constants/theme';
import { cornMazeService } from '../../services/cornMazeService';
import {
  MazeTheme,
  MazeDifficulty,
  MazeTemplate,
  CreateMazeRequest,
} from '../../types/maze';

interface CreateMazeScreenProps {
  navigation: any;
}

const CreateMazeScreen: React.FC<CreateMazeScreenProps> = ({ navigation }) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [theme, setTheme] = useState<MazeTheme>(MazeTheme.HEALTH_PATH);
  const [difficulty, setDifficulty] = useState<MazeDifficulty>(MazeDifficulty.NORMAL);
  const [size, setSize] = useState(10);
  const [useTemplate, setUseTemplate] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<MazeTemplate | null>(null);
  const [templates, setTemplates] = useState<MazeTemplate[]>([]);
  const [loading, setLoading] = useState(false);

  // 主题配置
  const themeConfig = {
    [MazeTheme.HEALTH_PATH]: {
      name: '健康之路',
      color: '#4CAF50',
      icon: 'heart-pulse',
      description: '探索基础健康知识',
    },
    [MazeTheme.NUTRITION_GARDEN]: {
      name: '营养花园',
      color: '#FF9800',
      icon: 'food-apple',
      description: '学习营养学知识',
    },
    [MazeTheme.TCM_JOURNEY]: {
      name: '中医之旅',
      color: '#9C27B0',
      icon: 'leaf',
      description: '传统中医智慧',
    },
    [MazeTheme.BALANCED_LIFE]: {
      name: '平衡生活',
      color: '#2196F3',
      icon: 'scale-balance',
      description: '生活方式平衡',
    },
  };

  const difficultyConfig = {
    [MazeDifficulty.EASY]: { name: '简单', color: '#4CAF50', description: '适合初学者' },
    [MazeDifficulty.NORMAL]: { name: '普通', color: '#FF9800', description: '中等难度' },
    [MazeDifficulty.HARD]: { name: '困难', color: '#F44336', description: '具有挑战性' },
    [MazeDifficulty.EXPERT]: { name: '专家', color: '#9C27B0', description: '极具挑战性' },
  };

  // 加载模板
  useEffect(() => {
    const loadTemplates = async () => {
      try {
        const response = await cornMazeService.listMazeTemplates(undefined, undefined, 1, 50);
        setTemplates(response.templates);
      } catch (error) {
        console.error('加载模板失败:', error);
      }
    };

    if (useTemplate) {
      loadTemplates();
    }
  }, [useTemplate]);

  // 创建迷宫
  const createMaze = async () => {
    if (!name.trim()) {
      Alert.alert('错误', '请输入迷宫名称');
      return;
    }

    if (useTemplate && !selectedTemplate) {
      Alert.alert('错误', '请选择一个模板');
      return;
    }

    try {
      setLoading(true);
      
      const request: CreateMazeRequest = {
        name: name.trim(),
        description: description.trim() || undefined,
        theme,
        difficulty,
        size: useTemplate ? undefined : size,
        useTemplate,
        templateId: selectedTemplate?.templateId,
      };

      const maze = await cornMazeService.createMaze(request);
      
      Alert.alert(
        '创建成功',
        '迷宫已创建完成！',
        [
          { text: '返回列表', onPress: () => navigation.goBack() },
          { 
            text: '立即开始', 
            onPress: () => navigation.navigate('MazeGame', { 
              mazeId: maze.id, 
              userId: 'current-user' 
            })
          },
        ]
      );
    } catch (error) {
      console.error('创建迷宫失败:', error);
      Alert.alert('错误', '创建迷宫失败，请重试');
    } finally {
      setLoading(false);
    }
  };

  // 渲染主题选择
  const renderThemeSelector = () => (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>选择主题</Text>
      <View style={styles.optionGrid}>
        {Object.entries(themeConfig).map(([key, config]) => (
          <TouchableOpacity
            key={key}
            style={[
              styles.optionCard,
              theme === key && { borderColor: config.color, borderWidth: 2 }
            ]}
            onPress={() => setTheme(key as MazeTheme)}
          >
            <Icon name={config.icon} size={24} color={config.color} />
            <Text style={styles.optionName}>{config.name}</Text>
            <Text style={styles.optionDescription}>{config.description}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );

  // 渲染难度选择
  const renderDifficultySelector = () => (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>选择难度</Text>
      <View style={styles.optionGrid}>
        {Object.entries(difficultyConfig).map(([key, config]) => (
          <TouchableOpacity
            key={key}
            style={[
              styles.difficultyCard,
              difficulty === key && { borderColor: config.color, borderWidth: 2 }
            ]}
            onPress={() => setDifficulty(key as MazeDifficulty)}
          >
            <View style={[styles.difficultyIndicator, { backgroundColor: config.color }]} />
            <Text style={styles.difficultyName}>{config.name}</Text>
            <Text style={styles.difficultyDescription}>{config.description}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </View>
  );

  // 渲染模板选择
  const renderTemplateSelector = () => {
    if (!useTemplate) return null;

    const filteredTemplates = templates.filter(t => t.mazeType === theme);

    return (
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>选择模板</Text>
        {filteredTemplates.length > 0 ? (
          <ScrollView horizontal showsHorizontalScrollIndicator={false}>
            {filteredTemplates.map((template) => (
              <TouchableOpacity
                key={template.templateId}
                style={[
                  styles.templateCard,
                  selectedTemplate?.templateId === template.templateId && styles.selectedTemplate
                ]}
                onPress={() => setSelectedTemplate(template)}
              >
                <Text style={styles.templateName}>{template.name}</Text>
                <Text style={styles.templateDescription}>{template.description}</Text>
                <View style={styles.templateStats}>
                  <Text style={styles.templateStat}>{template.sizeX}×{template.sizeY}</Text>
                  <Text style={styles.templateStat}>{template.knowledgeNodeCount}知识点</Text>
                </View>
                {template.isPopular && (
                  <View style={styles.popularBadge}>
                    <Text style={styles.popularText}>热门</Text>
                  </View>
                )}
              </TouchableOpacity>
            ))}
          </ScrollView>
        ) : (
          <Text style={styles.noTemplatesText}>该主题暂无可用模板</Text>
        )}
      </View>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => navigation.goBack()}>
          <Icon name="arrow-left" size={24} color={colors.text} />
        </TouchableOpacity>
        <Text style={styles.title}>创建迷宫</Text>
        <View style={{ width: 24 }} />
      </View>

      <ScrollView style={styles.content}>
        {/* 基本信息 */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>基本信息</Text>
          
          <View style={styles.inputGroup}>
            <Text style={styles.inputLabel}>迷宫名称 *</Text>
            <TextInput
              style={styles.textInput}
              value={name}
              onChangeText={setName}
              placeholder="输入迷宫名称"
              placeholderTextColor={colors.textSecondary}
            />
          </View>

          <View style={styles.inputGroup}>
            <Text style={styles.inputLabel}>描述</Text>
            <TextInput
              style={[styles.textInput, styles.textArea]}
              value={description}
              onChangeText={setDescription}
              placeholder="输入迷宫描述（可选）"
              placeholderTextColor={colors.textSecondary}
              multiline
              numberOfLines={3}
            />
          </View>
        </View>

        {/* 使用模板开关 */}
        <View style={styles.section}>
          <View style={styles.switchRow}>
            <View>
              <Text style={styles.switchLabel}>使用模板</Text>
              <Text style={styles.switchDescription}>
                基于预设模板快速创建迷宫
              </Text>
            </View>
            <Switch
              value={useTemplate}
              onValueChange={setUseTemplate}
              trackColor={{ false: colors.border, true: colors.primary }}
              thumbColor={colors.white}
            />
          </View>
        </View>

        {/* 主题选择 */}
        {renderThemeSelector()}

        {/* 难度选择 */}
        {renderDifficultySelector()}

        {/* 模板选择 */}
        {renderTemplateSelector()}

        {/* 自定义大小 */}
        {!useTemplate && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>迷宫大小</Text>
            <View style={styles.sizeSelector}>
              {[8, 10, 12, 15, 20].map((sizeOption) => (
                <TouchableOpacity
                  key={sizeOption}
                  style={[
                    styles.sizeOption,
                    size === sizeOption && styles.selectedSize
                  ]}
                  onPress={() => setSize(sizeOption)}
                >
                  <Text style={[
                    styles.sizeText,
                    size === sizeOption && styles.selectedSizeText
                  ]}>
                    {sizeOption}×{sizeOption}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        )}
      </ScrollView>

      {/* 创建按钮 */}
      <View style={styles.footer}>
        <TouchableOpacity
          style={[styles.createButton, loading && styles.disabledButton]}
          onPress={createMaze}
          disabled={loading}
        >
          <Text style={styles.createButtonText}>
            {loading ? '创建中...' : '创建迷宫'}
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: colors.background,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  title: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.text,
  },
  content: {
    flex: 1,
    paddingHorizontal: 20,
  },
  section: {
    marginVertical: 16,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.text,
    marginBottom: 12,
  },
  inputGroup: {
    marginBottom: 16,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: colors.text,
    marginBottom: 8,
  },
  textInput: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 12,
    fontSize: 16,
    color: colors.text,
    backgroundColor: colors.surface,
  },
  textArea: {
    height: 80,
    textAlignVertical: 'top',
  },
  switchRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 8,
  },
  switchLabel: {
    fontSize: 16,
    fontWeight: '500',
    color: colors.text,
  },
  switchDescription: {
    fontSize: 14,
    color: colors.textSecondary,
    marginTop: 2,
  },
  optionGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  optionCard: {
    width: '48%',
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
  },
  optionName: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.text,
    marginTop: 8,
    textAlign: 'center',
  },
  optionDescription: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 4,
    textAlign: 'center',
  },
  difficultyCard: {
    width: '48%',
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: colors.border,
  },
  difficultyIndicator: {
    width: 20,
    height: 4,
    borderRadius: 2,
    marginBottom: 8,
  },
  difficultyName: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.text,
  },
  difficultyDescription: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 4,
  },
  templateCard: {
    width: 200,
    backgroundColor: colors.surface,
    borderRadius: 12,
    padding: 16,
    marginRight: 12,
    borderWidth: 1,
    borderColor: colors.border,
  },
  selectedTemplate: {
    borderColor: colors.primary,
    borderWidth: 2,
  },
  templateName: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.text,
  },
  templateDescription: {
    fontSize: 12,
    color: colors.textSecondary,
    marginTop: 4,
    lineHeight: 16,
  },
  templateStats: {
    marginTop: 8,
  },
  templateStat: {
    fontSize: 11,
    color: colors.textSecondary,
    marginTop: 2,
  },
  popularBadge: {
    position: 'absolute',
    top: 8,
    right: 8,
    backgroundColor: colors.warning,
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 8,
  },
  popularText: {
    fontSize: 10,
    fontWeight: '600',
    color: colors.white,
  },
  noTemplatesText: {
    fontSize: 14,
    color: colors.textSecondary,
    textAlign: 'center',
    paddingVertical: 20,
  },
  sizeSelector: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  sizeOption: {
    flex: 1,
    backgroundColor: colors.surface,
    borderRadius: 8,
    paddingVertical: 12,
    marginHorizontal: 4,
    alignItems: 'center',
    borderWidth: 1,
    borderColor: colors.border,
  },
  selectedSize: {
    borderColor: colors.primary,
    backgroundColor: colors.primary + '20',
  },
  sizeText: {
    fontSize: 14,
    fontWeight: '500',
    color: colors.text,
  },
  selectedSizeText: {
    color: colors.primary,
    fontWeight: '600',
  },
  footer: {
    paddingHorizontal: 20,
    paddingVertical: 16,
    borderTopWidth: 1,
    borderTopColor: colors.border,
  },
  createButton: {
    backgroundColor: colors.primary,
    borderRadius: 12,
    paddingVertical: 16,
    alignItems: 'center',
  },
  disabledButton: {
    opacity: 0.6,
  },
  createButtonText: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.white,
  },
});

export default CreateMazeScreen; 
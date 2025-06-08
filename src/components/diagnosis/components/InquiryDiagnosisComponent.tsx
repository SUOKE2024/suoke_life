import React, { useCallback, useState } from 'react';
import {
    ActivityIndicator,
    Alert,
    ScrollView,
    StyleSheet,
    Text,
    TextInput,
    TouchableOpacity,
    View,
} from 'react-native';
import { colors, spacing } from '../../../constants/theme';
import { DiagnosisComponentProps, InquiryDiagnosisData } from '../../../types/diagnosis';

interface Symptom {
  id: string;
  name: string;
  category: string;
  selected: boolean;
}

export const InquiryDiagnosisComponent: React.FC<DiagnosisComponentProps> = ({
  onComplete,
  onCancel,
}) => {
  const [currentSymptoms, setCurrentSymptoms] = useState<Symptom[]>([
    { id: '1', name: '头痛', category: '头部', selected: false },
    { id: '2', name: '头晕', category: '头部', selected: false },
    { id: '3', name: '失眠', category: '睡眠', selected: false },
    { id: '4', name: '疲劳', category: '全身', selected: false },
    { id: '5', name: '食欲不振', category: '消化', selected: false },
    { id: '6', name: '腹痛', category: '消化', selected: false },
    { id: '7', name: '咳嗽', category: '呼吸', selected: false },
    { id: '8', name: '胸闷', category: '呼吸', selected: false },
    { id: '9', name: '心悸', category: '心血管', selected: false },
    { id: '10', name: '腰痛', category: '骨骼肌肉', selected: false },
  ]);

  const [medicalHistory, setMedicalHistory] = useState('');
  const [lifestyle, setLifestyle] = useState({
    sleep: '',
    diet: '',
    exercise: '',
    stress: '',
  });
  const [painLevel, setPainLevel] = useState(0);
  const [symptomDuration, setSymptomDuration] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);

  const toggleSymptom = useCallback((symptomId: string) => {
    setCurrentSymptoms(prev => 
      prev.map(symptom => 
        symptom.id === symptomId 
          ? { ...symptom, selected: !symptom.selected }
          : symptom
      )
    );
  }, []);

  const analyzeInquiry = useCallback(async () => {
    const selectedSymptoms = currentSymptoms.filter(s => s.selected);
    if (selectedSymptoms.length === 0) {
      Alert.alert('提示', '请至少选择一个症状');
      return;
    }

    setIsAnalyzing(true);
    try {
      // 模拟问诊分析过程
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const mockResult = {
        symptomAnalysis: {
          primarySymptoms: selectedSymptoms.map(s => s.name),
          symptomPattern: '气虚血瘀',
          severity: painLevel > 5 ? '中重度' : '轻度',
          duration: symptomDuration || '未明确',
          confidence: 0.87,
        },
        syndromePattern: {
          pattern: '脾胃虚弱',
          description: '脾胃功能失调，气血生化不足',
          characteristics: ['消化不良', '精神疲倦', '食欲减退'],
          confidence: 0.82,
        },
        riskAssessment: {
          level: '低风险',
          factors: ['生活压力', '饮食不规律', '运动不足'],
          recommendations: [
            '调整作息时间',
            '改善饮食结构',
            '适当运动锻炼',
            '减轻精神压力',
          ],
        },
        overallAssessment: '问诊结果显示主要为功能性症状，建议调理生活方式',
      };

      setAnalysisResult(mockResult);
    } catch (error) {
      Alert.alert('错误', '问诊分析失败，请重试');
    } finally {
      setIsAnalyzing(false);
    }
  }, [currentSymptoms, painLevel, symptomDuration]);

  const handleComplete = useCallback(() => {
    const selectedSymptoms = currentSymptoms.filter(s => s.selected);
    const data: InquiryDiagnosisData = {
      symptoms: selectedSymptoms.map(s => s.name),
      medicalHistory: medicalHistory ? [medicalHistory] : [],
      lifestyle,
      currentSymptoms: selectedSymptoms.map(s => s.name),
      painLevel,
      duration: symptomDuration,
    };
    onComplete(data);
  }, [currentSymptoms, medicalHistory, lifestyle, painLevel, symptomDuration, onComplete]);

  const renderSymptomSection = () => {
    const categories = [...new Set(currentSymptoms.map(s => s.category))];
    
    return (
      <View style={styles.symptomSection}>
        <Text style={styles.sectionTitle}>当前症状</Text>
        <Text style={styles.sectionDescription}>请选择您目前的症状</Text>
        
        {categories.map(category => (
          <View key={category} style={styles.categoryContainer}>
            <Text style={styles.categoryTitle}>{category}</Text>
            <View style={styles.symptomGrid}>
              {currentSymptoms
                .filter(s => s.category === category)
                .map(symptom => (
                  <TouchableOpacity
                    key={symptom.id}
                    style={[
                      styles.symptomButton,
                      symptom.selected && styles.symptomButtonSelected
                    ]}
                    onPress={() => toggleSymptom(symptom.id)}
                  >
                    <Text style={[
                      styles.symptomText,
                      symptom.selected && styles.symptomTextSelected
                    ]}>
                      {symptom.name}
                    </Text>
                  </TouchableOpacity>
                ))}
            </View>
          </View>
        ))}
      </View>
    );
  };

  const renderPainLevelSection = () => (
    <View style={styles.painSection}>
      <Text style={styles.sectionTitle}>疼痛程度</Text>
      <Text style={styles.sectionDescription}>请选择您的疼痛程度（0-10分）</Text>
      <View style={styles.painLevelContainer}>
        {[...Array(11)].map((_, index) => (
          <TouchableOpacity
            key={index}
            style={[
              styles.painLevelButton,
              painLevel === index && styles.painLevelButtonSelected
            ]}
            onPress={() => setPainLevel(index)}
          >
            <Text style={[
              styles.painLevelText,
              painLevel === index && styles.painLevelTextSelected
            ]}>
              {index}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
      <View style={styles.painLevelLabels}>
        <Text style={styles.painLevelLabel}>无痛</Text>
        <Text style={styles.painLevelLabel}>剧痛</Text>
      </View>
    </View>
  );

  const renderLifestyleSection = () => (
    <View style={styles.lifestyleSection}>
      <Text style={styles.sectionTitle}>生活方式</Text>
      
      <View style={styles.inputGroup}>
        <Text style={styles.inputLabel}>睡眠情况</Text>
        <TextInput
          style={styles.textInput}
          placeholder="请描述您的睡眠质量和时间"
          value={lifestyle.sleep}
          onChangeText={(text) => setLifestyle(prev => ({ ...prev, sleep: text }))}
          multiline
        />
      </View>

      <View style={styles.inputGroup}>
        <Text style={styles.inputLabel}>饮食习惯</Text>
        <TextInput
          style={styles.textInput}
          placeholder="请描述您的饮食习惯"
          value={lifestyle.diet}
          onChangeText={(text) => setLifestyle(prev => ({ ...prev, diet: text }))}
          multiline
        />
      </View>

      <View style={styles.inputGroup}>
        <Text style={styles.inputLabel}>运动情况</Text>
        <TextInput
          style={styles.textInput}
          placeholder="请描述您的运动频率和强度"
          value={lifestyle.exercise}
          onChangeText={(text) => setLifestyle(prev => ({ ...prev, exercise: text }))}
          multiline
        />
      </View>

      <View style={styles.inputGroup}>
        <Text style={styles.inputLabel}>压力状况</Text>
        <TextInput
          style={styles.textInput}
          placeholder="请描述您的工作和生活压力"
          value={lifestyle.stress}
          onChangeText={(text) => setLifestyle(prev => ({ ...prev, stress: text }))}
          multiline
        />
      </View>
    </View>
  );

  const renderAnalysisResult = () => {
    if (!analysisResult) return null;

    return (
      <View style={styles.resultContainer}>
        <Text style={styles.resultTitle}>分析结果</Text>
        
        <View style={styles.analysisSection}>
          <Text style={styles.analysisTitle}>症状分析</Text>
          <Text style={styles.analysisText}>
            主要症状：{analysisResult.symptomAnalysis.primarySymptoms.join('、')}
          </Text>
          <Text style={styles.analysisText}>
            症状模式：{analysisResult.symptomAnalysis.symptomPattern}
          </Text>
          <Text style={styles.analysisText}>
            严重程度：{analysisResult.symptomAnalysis.severity}
          </Text>
          <Text style={styles.confidenceText}>
            置信度：{(analysisResult.symptomAnalysis.confidence * 100).toFixed(1)}%
          </Text>
        </View>

        <View style={styles.analysisSection}>
          <Text style={styles.analysisTitle}>证候分析</Text>
          <Text style={styles.analysisText}>
            证候：{analysisResult.syndromePattern.pattern}
          </Text>
          <Text style={styles.analysisText}>
            描述：{analysisResult.syndromePattern.description}
          </Text>
          <Text style={styles.confidenceText}>
            置信度：{(analysisResult.syndromePattern.confidence * 100).toFixed(1)}%
          </Text>
        </View>

        <View style={styles.recommendationSection}>
          <Text style={styles.analysisTitle}>建议</Text>
          {analysisResult.riskAssessment.recommendations.map((rec: string, index: number) => (
            <Text key={index} style={styles.recommendationText}>• {rec}</Text>
          ))}
        </View>
      </View>
    );
  };

  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <Text style={styles.title}>问诊分析</Text>
      <Text style={styles.subtitle}>
        通过询问症状、病史和生活方式，了解身体健康状况
      </Text>

      {renderSymptomSection()}
      {renderPainLevelSection()}

      <View style={styles.inputSection}>
        <Text style={styles.sectionTitle}>症状持续时间</Text>
        <TextInput
          style={styles.textInput}
          placeholder="请输入症状持续的时间，如：3天、1周、1个月等"
          value={symptomDuration}
          onChangeText={setSymptomDuration}
        />
      </View>

      <View style={styles.inputSection}>
        <Text style={styles.sectionTitle}>既往病史</Text>
        <TextInput
          style={[styles.textInput, styles.multilineInput]}
          placeholder="请描述您的既往疾病史、手术史、过敏史等"
          value={medicalHistory}
          onChangeText={setMedicalHistory}
          multiline
          numberOfLines={4}
        />
      </View>

      {renderLifestyleSection()}

      <View style={styles.actionContainer}>
        <TouchableOpacity
          style={[styles.button, styles.analyzeButton]}
          onPress={analyzeInquiry}
          disabled={isAnalyzing}
        >
          {isAnalyzing ? (
            <ActivityIndicator size="small" color={colors.white} />
          ) : (
            <Text style={styles.buttonText}>开始分析</Text>
          )}
        </TouchableOpacity>
      </View>

      {renderAnalysisResult()}

      {analysisResult && (
        <View style={styles.actionContainer}>
          <TouchableOpacity
            style={[styles.button, styles.completeButton]}
            onPress={handleComplete}
          >
            <Text style={styles.buttonText}>完成问诊</Text>
          </TouchableOpacity>
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: spacing.md,
  },
  title: {
    fontSize: 20,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  subtitle: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: spacing.lg,
    lineHeight: 20,
  },
  symptomSection: {
    marginBottom: spacing.lg,
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.xs,
  },
  sectionDescription: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: spacing.md,
  },
  categoryContainer: {
    marginBottom: spacing.md,
  },
  categoryTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  symptomGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  symptomButton: {
    paddingVertical: spacing.sm,
    paddingHorizontal: spacing.md,
    borderRadius: 20,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
  },
  symptomButtonSelected: {
    backgroundColor: colors.primary,
    borderColor: colors.primary,
  },
  symptomText: {
    fontSize: 14,
    color: colors.textSecondary,
  },
  symptomTextSelected: {
    color: colors.white,
    fontWeight: '600',
  },
  painSection: {
    marginBottom: spacing.lg,
    backgroundColor: colors.surface,
    borderRadius: 8,
    padding: spacing.md,
  },
  painLevelContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: spacing.sm,
  },
  painLevelButton: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: colors.border,
    justifyContent: 'center',
    alignItems: 'center',
  },
  painLevelButtonSelected: {
    backgroundColor: colors.primary,
  },
  painLevelText: {
    fontSize: 12,
    color: colors.textSecondary,
    fontWeight: '600',
  },
  painLevelTextSelected: {
    color: colors.white,
  },
  painLevelLabels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  painLevelLabel: {
    fontSize: 12,
    color: colors.textTertiary,
  },
  inputSection: {
    marginBottom: spacing.lg,
  },
  inputGroup: {
    marginBottom: spacing.md,
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  textInput: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: 8,
    paddingHorizontal: spacing.md,
    paddingVertical: spacing.sm,
    fontSize: 14,
    color: colors.textPrimary,
    backgroundColor: colors.surface,
  },
  multilineInput: {
    height: 80,
    textAlignVertical: 'top',
  },
  lifestyleSection: {
    marginBottom: spacing.lg,
  },
  actionContainer: {
    marginVertical: spacing.md,
  },
  button: {
    paddingVertical: spacing.md,
    paddingHorizontal: spacing.lg,
    borderRadius: 8,
    alignItems: 'center',
  },
  analyzeButton: {
    backgroundColor: colors.primary,
  },
  completeButton: {
    backgroundColor: colors.success,
  },
  buttonText: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.white,
  },
  resultContainer: {
    backgroundColor: colors.surface,
    borderRadius: 8,
    padding: spacing.md,
    marginTop: spacing.md,
  },
  resultTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.md,
  },
  analysisSection: {
    marginBottom: spacing.md,
    paddingBottom: spacing.md,
    borderBottomWidth: 1,
    borderBottomColor: colors.border,
  },
  analysisTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: colors.textPrimary,
    marginBottom: spacing.sm,
  },
  analysisText: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
  },
  confidenceText: {
    fontSize: 12,
    color: colors.primary,
    fontWeight: '500',
  },
  recommendationSection: {
    marginTop: spacing.sm,
  },
  recommendationText: {
    fontSize: 14,
    color: colors.textSecondary,
    marginBottom: spacing.xs,
    lineHeight: 20,
  },
}); 
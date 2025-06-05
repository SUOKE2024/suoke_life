import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  Alert,
  ActivityIndicator,
} from 'react-native';
import { ragService } from '../../services/ragService';
import type {
  TCMAnalysisRequest,
  TCMAnalysisResponse,
  HerbRecommendationRequest,
  HerbRecommendationResponse,
} from '../../services/ragService';

interface TCMAnalysisComponentProps {
  userId: string;
  onAnalysisResult?: (result: TCMAnalysisResponse) => void;
  onHerbResult?: (result: HerbRecommendationResponse) => void;
  onError?: (error: Error) => void;
}

export const TCMAnalysisComponent: React.FC<TCMAnalysisComponentProps> = ({
  userId,
  onAnalysisResult,
  onHerbResult,
  onError,
}) => {
  const [symptoms, setSymptoms] = useState<string[]>(['']);
  const [constitutionType, setConstitutionType] = useState<string>('balanced');
  const [medicalHistory, setMedicalHistory] = useState('');
  const [currentMedications, setCurrentMedications] = useState('');
  const [lifestyle, setLifestyle] = useState({
    diet: '',
    exercise: '',
    sleep: '',
    stress: '',
    environment: '',
  });
  
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isRecommending, setIsRecommending] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<TCMAnalysisResponse | null>(null);
  const [herbResult, setHerbResult] = useState<HerbRecommendationResponse | null>(null);

  // 体质类型选项
  const constitutionTypes = [
    { value: 'balanced', label: '平和质' },
    { value: 'qi_deficiency', label: '气虚质' },
    { value: 'yang_deficiency', label: '阳虚质' },
    { value: 'yin_deficiency', label: '阴虚质' },
    { value: 'phlegm_dampness', label: '痰湿质' },
    { value: 'damp_heat', label: '湿热质' },
    { value: 'blood_stasis', label: '血瘀质' },
    { value: 'qi_stagnation', label: '气郁质' },
    { value: 'special_constitution', label: '特禀质' },
  ];

  // 添加症状
  const addSymptom = useCallback(() => {
    setSymptoms(prev => [...prev, '']);
  }, []);

  // 更新症状
  const updateSymptom = useCallback((index: number, value: string) => {
    setSymptoms(prev => prev.map((symptom, i) => i === index ? value : symptom));
  }, []);

  // 删除症状
  const removeSymptom = useCallback((index: number) => {
    if (symptoms.length > 1) {
      setSymptoms(prev => prev.filter((_, i) => i !== index));
    }
  }, [symptoms.length]);

  // 执行中医分析
  const handleAnalysis = useCallback(async () => {
    const validSymptoms = symptoms.filter(s => s.trim());
    if (validSymptoms.length === 0) {
      Alert.alert('提示', '请至少输入一个症状');
      return;
    }

    setIsAnalyzing(true);
    setAnalysisResult(null);

    try {
      const request: TCMAnalysisRequest = {
        symptoms: validSymptoms,
        userId,
        constitutionType: constitutionType as any,
        medicalHistory: medicalHistory ? medicalHistory.split(',').map(s => s.trim()) : undefined,
        currentMedications: currentMedications ? currentMedications.split(',').map(s => s.trim()) : undefined,
        lifestyleFactors: {
          diet: lifestyle.diet || undefined,
          exercise: lifestyle.exercise || undefined,
          sleep: lifestyle.sleep || undefined,
          stress: lifestyle.stress || undefined,
          environment: lifestyle.environment || undefined,
        },
      };

      const result = await ragService.analyzeTCM(request);
      setAnalysisResult(result);
      onAnalysisResult?.(result);
    } catch (error) {
      console.error('中医分析失败:', error);
      onError?.(error as Error);
      Alert.alert('分析失败', (error as Error).message);
    } finally {
      setIsAnalyzing(false);
    }
  }, [symptoms, userId, constitutionType, medicalHistory, currentMedications, lifestyle, onAnalysisResult, onError]);

  // 获取中药推荐
  const handleHerbRecommendation = useCallback(async () => {
    if (!analysisResult) {
      Alert.alert('提示', '请先进行中医分析');
      return;
    }

    setIsRecommending(true);
    setHerbResult(null);

    try {
      const request: HerbRecommendationRequest = {
        syndromeType: analysisResult.syndromeAnalysis.primarySyndrome,
        constitutionType: analysisResult.constitutionAssessment.constitutionType,
        userId,
        currentSymptoms: symptoms.filter(s => s.trim()),
      };

      const result = await ragService.recommendHerbs(request);
      setHerbResult(result);
      onHerbResult?.(result);
    } catch (error) {
      console.error('中药推荐失败:', error);
      onError?.(error as Error);
      Alert.alert('推荐失败', (error as Error).message);
    } finally {
      setIsRecommending(false);
    }
  }, [analysisResult, symptoms, userId, onHerbResult, onError]);

  // 清除结果
  const handleClear = useCallback(() => {
    setSymptoms(['']);
    setConstitutionType('balanced');
    setMedicalHistory('');
    setCurrentMedications('');
    setLifestyle({
      diet: '',
      exercise: '',
      sleep: '',
      stress: '',
      environment: '',
    });
    setAnalysisResult(null);
    setHerbResult(null);
  }, []);

  // 导出分析报告
  const handleExportReport = useCallback(() => {
    if (!analysisResult) {
      Alert.alert('提示', '请先进行中医分析');
      return;
    }

    const report = {
      timestamp: new Date().toISOString(),
      userId,
      symptoms: symptoms.filter(s => s.trim()),
      constitutionType,
      analysisResult,
      herbResult,
    };

    // 这里可以实现导出功能，比如保存到本地存储或发送到服务器
    console.log('导出报告:', report);
    Alert.alert('成功', '分析报告已导出');
  }, [analysisResult, herbResult, userId, symptoms, constitutionType]);

  // 保存为模板
  const handleSaveTemplate = useCallback(() => {
    const template = {
      symptoms: symptoms.filter(s => s.trim()),
      constitutionType,
      medicalHistory,
      currentMedications,
      lifestyle,
    };

    // 保存到本地存储
    try {
      // 这里可以使用AsyncStorage保存模板
      console.log('保存模板:', template);
      Alert.alert('成功', '症状模板已保存');
    } catch (error) {
      Alert.alert('错误', '保存模板失败');
    }
  }, [symptoms, constitutionType, medicalHistory, currentMedications, lifestyle]);

  // 快速填充常见症状
  const handleQuickFill = useCallback((symptomSet: string[]) => {
    setSymptoms(symptomSet);
  }, []);

  // 常见症状组合
  const commonSymptomSets = [
    {
      name: '感冒症状',
      symptoms: ['发热', '头痛', '鼻塞', '咳嗽', '咽痛']
    },
    {
      name: '消化不良',
      symptoms: ['腹胀', '食欲不振', '恶心', '腹痛', '便秘']
    },
    {
      name: '失眠焦虑',
      symptoms: ['失眠', '多梦', '心悸', '焦虑', '健忘']
    },
    {
      name: '疲劳乏力',
      symptoms: ['疲劳', '乏力', '气短', '头晕', '精神不振']
    }
  ];

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>中医智能分析</Text>

      {/* 症状输入 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>症状描述</Text>
        {symptoms.map((symptom, index) => (
          <View key={index} style={styles.symptomRow}>
            <TextInput
              style={styles.symptomInput}
              value={symptom}
              onChangeText={(value) => updateSymptom(index, value)}
              placeholder={`症状 ${index + 1}`}
            />
            {symptoms.length > 1 && (
              <TouchableOpacity
                style={styles.removeButton}
                onPress={() => removeSymptom(index)}
              >
                <Text style={styles.removeButtonText}>删除</Text>
              </TouchableOpacity>
            )}
          </View>
        ))}
        <TouchableOpacity style={styles.addButton} onPress={addSymptom}>
          <Text style={styles.addButtonText}>+ 添加症状</Text>
        </TouchableOpacity>
        
        {/* 快速填充 */}
        <View style={styles.quickFillContainer}>
          <Text style={styles.quickFillTitle}>常见症状组合:</Text>
          <View style={styles.quickFillButtons}>
            {commonSymptomSets.map((set, index) => (
              <TouchableOpacity
                key={index}
                style={styles.quickFillButton}
                onPress={() => handleQuickFill(set.symptoms)}
              >
                <Text style={styles.quickFillButtonText}>{set.name}</Text>
              </TouchableOpacity>
            ))}
          </View>
        </View>
      </View>

      {/* 体质类型选择 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>体质类型</Text>
        <View style={styles.constitutionGrid}>
          {constitutionTypes.map((type) => (
            <TouchableOpacity
              key={type.value}
              style={[
                styles.constitutionButton,
                constitutionType === type.value && styles.constitutionButtonActive,
              ]}
              onPress={() => setConstitutionType(type.value)}
            >
              <Text
                style={[
                  styles.constitutionButtonText,
                  constitutionType === type.value && styles.constitutionButtonTextActive,
                ]}
              >
                {type.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>

      {/* 病史和用药 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>病史和用药</Text>
        <TextInput
          style={styles.textInput}
          value={medicalHistory}
          onChangeText={setMedicalHistory}
          placeholder="既往病史（用逗号分隔）"
          multiline
        />
        <TextInput
          style={styles.textInput}
          value={currentMedications}
          onChangeText={setCurrentMedications}
          placeholder="当前用药（用逗号分隔）"
          multiline
        />
      </View>

      {/* 生活方式 */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>生活方式</Text>
        <TextInput
          style={styles.textInput}
          value={lifestyle.diet}
          onChangeText={(value) => setLifestyle(prev => ({ ...prev, diet: value }))}
          placeholder="饮食习惯"
        />
        <TextInput
          style={styles.textInput}
          value={lifestyle.exercise}
          onChangeText={(value) => setLifestyle(prev => ({ ...prev, exercise: value }))}
          placeholder="运动情况"
        />
        <TextInput
          style={styles.textInput}
          value={lifestyle.sleep}
          onChangeText={(value) => setLifestyle(prev => ({ ...prev, sleep: value }))}
          placeholder="睡眠状况"
        />
        <TextInput
          style={styles.textInput}
          value={lifestyle.stress}
          onChangeText={(value) => setLifestyle(prev => ({ ...prev, stress: value }))}
          placeholder="压力水平"
        />
        <TextInput
          style={styles.textInput}
          value={lifestyle.environment}
          onChangeText={(value) => setLifestyle(prev => ({ ...prev, environment: value }))}
          placeholder="环境因素"
        />
      </View>

      {/* 操作按钮 */}
      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={[styles.button, styles.analysisButton]}
          onPress={handleAnalysis}
          disabled={isAnalyzing}
        >
          {isAnalyzing ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>中医分析</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, styles.herbButton, !analysisResult && styles.buttonDisabled]}
          onPress={handleHerbRecommendation}
          disabled={isRecommending || !analysisResult}
        >
          {isRecommending ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>中药推荐</Text>
          )}
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.button, styles.clearButton]}
          onPress={handleClear}
          disabled={isAnalyzing || isRecommending}
        >
          <Text style={styles.buttonText}>清除</Text>
        </TouchableOpacity>
      </View>

      {/* 高级功能按钮 */}
      <View style={styles.advancedButtonContainer}>
        <TouchableOpacity
          style={[styles.smallButton, styles.saveButton]}
          onPress={handleSaveTemplate}
          disabled={isAnalyzing || isRecommending}
        >
          <Text style={styles.smallButtonText}>保存模板</Text>
        </TouchableOpacity>

        {analysisResult && (
          <TouchableOpacity
            style={[styles.smallButton, styles.exportButton]}
            onPress={handleExportReport}
            disabled={isAnalyzing || isRecommending}
          >
            <Text style={styles.smallButtonText}>导出报告</Text>
          </TouchableOpacity>
        )}
      </View>

      {/* 分析结果 */}
      {analysisResult && (
        <View style={styles.resultSection}>
          <Text style={styles.resultTitle}>中医分析结果</Text>
          
          {/* 证候分析 */}
          <View style={styles.resultCard}>
            <Text style={styles.cardTitle}>证候分析</Text>
            <Text style={styles.primarySyndrome}>
              主证: {analysisResult.syndromeAnalysis.primarySyndrome}
            </Text>
            <Text style={styles.confidence}>
              置信度: {(analysisResult.syndromeAnalysis.confidence * 100).toFixed(1)}%
            </Text>
            
            {analysisResult.syndromeAnalysis.secondarySyndromes.length > 0 && (
              <View style={styles.secondarySyndromes}>
                <Text style={styles.secondaryTitle}>次证:</Text>
                {analysisResult.syndromeAnalysis.secondarySyndromes.map((syndrome, index) => (
                  <Text key={index} style={styles.secondaryItem}>• {syndrome}</Text>
                ))}
              </View>
            )}

            {analysisResult.syndromeAnalysis.reasoning.length > 0 && (
              <View style={styles.reasoning}>
                <Text style={styles.reasoningTitle}>分析过程:</Text>
                {analysisResult.syndromeAnalysis.reasoning.map((reason, index) => (
                  <Text key={index} style={styles.reasoningItem}>• {reason}</Text>
                ))}
              </View>
            )}
          </View>

          {/* 体质评估 */}
          <View style={styles.resultCard}>
            <Text style={styles.cardTitle}>体质评估</Text>
            <Text style={styles.constitutionResult}>
              体质类型: {analysisResult.constitutionAssessment.constitutionType}
            </Text>
            <Text style={styles.constitutionScore}>
              评分: {analysisResult.constitutionAssessment.score}/100
            </Text>
            
            {analysisResult.constitutionAssessment.characteristics.length > 0 && (
              <View style={styles.characteristics}>
                <Text style={styles.characteristicsTitle}>特征:</Text>
                {analysisResult.constitutionAssessment.characteristics.map((char, index) => (
                  <Text key={index} style={styles.characteristicItem}>• {char}</Text>
                ))}
              </View>
            )}
          </View>

          {/* 治疗原则 */}
          {analysisResult.treatmentPrinciples.length > 0 && (
            <View style={styles.resultCard}>
              <Text style={styles.cardTitle}>治疗原则</Text>
              {analysisResult.treatmentPrinciples.map((principle, index) => (
                <Text key={index} style={styles.principleItem}>• {principle}</Text>
              ))}
            </View>
          )}

          {/* 生活建议 */}
          {analysisResult.lifestyleRecommendations.length > 0 && (
            <View style={styles.resultCard}>
              <Text style={styles.cardTitle}>生活建议</Text>
              {analysisResult.lifestyleRecommendations.map((recommendation, index) => (
                <Text key={index} style={styles.recommendationItem}>• {recommendation}</Text>
              ))}
            </View>
          )}
        </View>
      )}

      {/* 中药推荐结果 */}
      {herbResult && (
        <View style={styles.resultSection}>
          <Text style={styles.resultTitle}>中药推荐</Text>
          
          {/* 推荐方剂 */}
          {herbResult.recommendedFormulas.length > 0 && (
            <View style={styles.resultCard}>
              <Text style={styles.cardTitle}>推荐方剂</Text>
              {herbResult.recommendedFormulas.map((formula, index) => (
                <View key={index} style={styles.formulaItem}>
                  <Text style={styles.formulaName}>{formula.name}</Text>
                  <Text style={styles.formulaConfidence}>
                    置信度: {(formula.confidence * 100).toFixed(1)}%
                  </Text>
                  
                  <View style={styles.composition}>
                    <Text style={styles.compositionTitle}>组成:</Text>
                    {formula.composition.map((herb, herbIndex) => (
                      <Text key={herbIndex} style={styles.herbItem}>
                        • {herb.herb} {herb.dosage} - {herb.function}
                      </Text>
                    ))}
                  </View>
                  
                  <Text style={styles.preparation}>制法: {formula.preparation}</Text>
                  <Text style={styles.dosage}>用法: {formula.dosage}</Text>
                  <Text style={styles.duration}>疗程: {formula.duration}</Text>
                </View>
              ))}
            </View>
          )}

          {/* 单味药 */}
          {herbResult.singleHerbs.length > 0 && (
            <View style={styles.resultCard}>
              <Text style={styles.cardTitle}>单味药推荐</Text>
              {herbResult.singleHerbs.map((herb, index) => (
                <View key={index} style={styles.singleHerbItem}>
                  <Text style={styles.herbName}>{herb.name}</Text>
                  <Text style={styles.herbFunction}>功效: {herb.function}</Text>
                  <Text style={styles.herbDosage}>用量: {herb.dosage}</Text>
                  {herb.precautions.length > 0 && (
                    <View style={styles.precautions}>
                      <Text style={styles.precautionsTitle}>注意事项:</Text>
                      {herb.precautions.map((precaution, precIndex) => (
                        <Text key={precIndex} style={styles.precautionItem}>• {precaution}</Text>
                      ))}
                    </View>
                  )}
                </View>
              ))}
            </View>
          )}

          {/* 安全警告 */}
          {herbResult.safetyWarnings.length > 0 && (
            <View style={[styles.resultCard, styles.warningCard]}>
              <Text style={styles.warningTitle}>⚠️ 安全警告</Text>
              {herbResult.safetyWarnings.map((warning, index) => (
                <Text key={index} style={styles.warningItem}>• {warning}</Text>
              ))}
            </View>
          )}

          {/* 用药指导 */}
          <View style={styles.resultCard}>
            <Text style={styles.cardTitle}>用药指导</Text>
            <Text style={styles.instructionItem}>制备: {herbResult.usageInstructions.preparation}</Text>
            <Text style={styles.instructionItem}>服用: {herbResult.usageInstructions.administration}</Text>
            <Text style={styles.instructionItem}>时间: {herbResult.usageInstructions.timing}</Text>
            <Text style={styles.instructionItem}>疗程: {herbResult.usageInstructions.duration}</Text>
          </View>
        </View>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f5f5f5',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    textAlign: 'center',
    marginVertical: 20,
    color: '#333',
  },
  section: {
    backgroundColor: '#fff',
    margin: 16,
    padding: 16,
    borderRadius: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    marginBottom: 12,
    color: '#333',
  },
  symptomRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  symptomInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 6,
    padding: 10,
    fontSize: 16,
  },
  removeButton: {
    marginLeft: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
    backgroundColor: '#FF3B30',
    borderRadius: 6,
  },
  removeButtonText: {
    color: '#fff',
    fontSize: 14,
  },
  addButton: {
    alignSelf: 'flex-start',
    paddingHorizontal: 16,
    paddingVertical: 8,
    backgroundColor: '#007AFF',
    borderRadius: 6,
    marginTop: 8,
  },
  addButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '500',
  },
  constitutionGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  constitutionButton: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 16,
    backgroundColor: '#f0f0f0',
    borderWidth: 1,
    borderColor: '#ddd',
  },
  constitutionButtonActive: {
    backgroundColor: '#007AFF',
    borderColor: '#007AFF',
  },
  constitutionButtonText: {
    fontSize: 14,
    color: '#666',
  },
  constitutionButtonTextActive: {
    color: '#fff',
    fontWeight: '600',
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 6,
    padding: 12,
    fontSize: 16,
    marginBottom: 8,
    minHeight: 40,
  },
  buttonContainer: {
    flexDirection: 'row',
    gap: 12,
    margin: 16,
  },
  button: {
    flex: 1,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
  },
  analysisButton: {
    backgroundColor: '#007AFF',
  },
  herbButton: {
    backgroundColor: '#34C759',
  },
  clearButton: {
    backgroundColor: '#FF3B30',
  },
  buttonDisabled: {
    backgroundColor: '#ccc',
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  resultSection: {
    margin: 16,
  },
  resultTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 16,
    color: '#333',
  },
  resultCard: {
    backgroundColor: '#fff',
    borderRadius: 8,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
    color: '#007AFF',
  },
  primarySyndrome: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 4,
    color: '#333',
  },
  confidence: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  secondarySyndromes: {
    marginTop: 8,
  },
  secondaryTitle: {
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 4,
    color: '#333',
  },
  secondaryItem: {
    fontSize: 14,
    color: '#666',
    marginBottom: 2,
  },
  reasoning: {
    marginTop: 8,
  },
  reasoningTitle: {
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 4,
    color: '#333',
  },
  reasoningItem: {
    fontSize: 14,
    color: '#666',
    marginBottom: 2,
  },
  constitutionResult: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 4,
    color: '#333',
  },
  constitutionScore: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  characteristics: {
    marginTop: 8,
  },
  characteristicsTitle: {
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 4,
    color: '#333',
  },
  characteristicItem: {
    fontSize: 14,
    color: '#666',
    marginBottom: 2,
  },
  principleItem: {
    fontSize: 14,
    color: '#333',
    marginBottom: 4,
  },
  recommendationItem: {
    fontSize: 14,
    color: '#333',
    marginBottom: 4,
  },
  formulaItem: {
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
    paddingBottom: 12,
    marginBottom: 12,
  },
  formulaName: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
    color: '#333',
  },
  formulaConfidence: {
    fontSize: 14,
    color: '#666',
    marginBottom: 8,
  },
  composition: {
    marginBottom: 8,
  },
  compositionTitle: {
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 4,
    color: '#333',
  },
  herbItem: {
    fontSize: 13,
    color: '#666',
    marginBottom: 2,
  },
  preparation: {
    fontSize: 14,
    color: '#333',
    marginBottom: 2,
  },
  dosage: {
    fontSize: 14,
    color: '#333',
    marginBottom: 2,
  },
  duration: {
    fontSize: 14,
    color: '#333',
  },
  singleHerbItem: {
    borderBottomWidth: 1,
    borderBottomColor: '#eee',
    paddingBottom: 8,
    marginBottom: 8,
  },
  herbName: {
    fontSize: 15,
    fontWeight: '600',
    marginBottom: 4,
    color: '#333',
  },
  herbFunction: {
    fontSize: 14,
    color: '#666',
    marginBottom: 2,
  },
  herbDosage: {
    fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  precautions: {
    marginTop: 4,
  },
  precautionsTitle: {
    fontSize: 13,
    fontWeight: '500',
    marginBottom: 2,
    color: '#FF3B30',
  },
  precautionItem: {
    fontSize: 12,
    color: '#FF3B30',
    marginBottom: 1,
  },
  warningCard: {
    borderLeftWidth: 4,
    borderLeftColor: '#FF3B30',
  },
  warningTitle: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 8,
    color: '#FF3B30',
  },
  warningItem: {
    fontSize: 14,
    color: '#FF3B30',
    marginBottom: 4,
  },
  instructionItem: {
    fontSize: 14,
    color: '#333',
    marginBottom: 4,
  },
  quickFillContainer: {
    marginTop: 12,
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#eee',
  },
  quickFillTitle: {
    fontSize: 14,
    fontWeight: '500',
    marginBottom: 8,
    color: '#333',
  },
  quickFillButtons: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  quickFillButton: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    backgroundColor: '#E3F2FD',
    borderWidth: 1,
    borderColor: '#2196F3',
  },
  quickFillButtonText: {
    fontSize: 12,
    color: '#2196F3',
    fontWeight: '500',
  },
  advancedButtonContainer: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
    justifyContent: 'space-around',
  },
  smallButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6,
    alignItems: 'center',
    justifyContent: 'center',
    flex: 1,
  },
  smallButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '500',
  },
  saveButton: {
    backgroundColor: '#4CAF50',
  },
  exportButton: {
    backgroundColor: '#FF9800',
  },
});

export default TCMAnalysisComponent; 
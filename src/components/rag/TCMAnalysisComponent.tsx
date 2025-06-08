import React, { useState, useCallback } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
  Alert,
  ActivityIndicator;
} from 'react-native';
// 简化的类型定义
interface TCMAnalysisRequest {
  symptoms: string[];
  userId: string;
  constitutionType: string;
  medicalHistory?: string[];
  currentMedications?: string[];
  lifestyleFactors?: {
    diet?: string;
    exercise?: string;
    sleep?: string;
    stress?: string;
    environment?: string;
};
}
interface TCMAnalysisResponse {
  syndromeAnalysis: {;
  primarySyndrome: string;
    secondarySyndromes: string[];
  confidence: number;
};
  constitutionAssessment: {,
  constitutionType: string;
    characteristics: string[];
  };
  recommendations: {,
  lifestyle: string[];
    dietary: string[],
  exercise: string[];
  };
}
interface HerbRecommendationRequest {
  syndromeType: string;
  constitutionType: string;
  userId: string;
  currentSymptoms: string[];
}
interface HerbRecommendationResponse {
  formula: {;
  name: string;
    herbs: Array<{;
  name: string;
      dosage: string;
  function: string;
}>;
  };
  instructions: string[],
  precautions: string[];
}
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
  onError;
}) => {
  const [symptoms, setSymptoms] = useState<string[]>(['']);
  const [constitutionType, setConstitutionType] = useState<string>('balanced');
  const [medicalHistory, setMedicalHistory] = useState('');
  const [currentMedications, setCurrentMedications] = useState('');
  const [lifestyle, setLifestyle] = useState({
      diet: "",
      exercise: '',
    sleep: '',
    stress: '',
    environment: ''
  });
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isRecommending, setIsRecommending] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<TCMAnalysisResponse | null>(null);
  const [herbResult, setHerbResult] = useState<HerbRecommendationResponse | null>(null);
  // 体质类型选项
  const constitutionTypes = [
    {
      value: "balanced",
      label: '平和质' },
    {
      value: "qi_deficiency",
      label: '气虚质' },
    {
      value: "yang_deficiency",
      label: '阳虚质' },
    {
      value: "yin_deficiency",
      label: '阴虚质' },
    {
      value: "phlegm_dampness",
      label: '痰湿质' },
    {
      value: "damp_heat",
      label: '湿热质' },
    {
      value: "blood_stasis",
      label: '血瘀质' },
    {
      value: "qi_stagnation",
      label: '气郁质' },
    {
      value: "special_constitution",
      label: '特禀质' }
  ];
  // 添加症状
  const addSymptom = useCallback() => {
    setSymptoms(prev => [...prev, '']);
  }, []);
  // 更新症状
  const updateSymptom = useCallback(index: number, value: string) => {
    setSymptoms(prev => prev.map((symptom, i) => i === index ? value : symptom));
  }, []);
  // 删除症状
  const removeSymptom = useCallback(index: number) => {
    if (symptoms.length > 1) {
      setSymptoms(prev => prev.filter(_, i) => i !== index));
    }
  }, [symptoms.length]);
  // 执行中医分析
  const handleAnalysis = useCallback(async () => {
    const validSymptoms = symptoms.filter(s => s.trim());
    if (validSymptoms.length === 0) {
      Alert.alert("提示", "请至少输入一个症状');
      return;
    }
    setIsAnalyzing(true);
    setAnalysisResult(null);
    try {
      // 模拟分析结果
      const mockResult: TCMAnalysisResponse = {,
  syndromeAnalysis: {
      primarySyndrome: "气虚血瘀",
      secondarySyndromes: ["脾胃虚弱", "肝气郁结'],
          confidence: 0.85;
        },
        constitutionAssessment: {,
  constitutionType: constitutionType,
          characteristics: ["气虚", "血瘀', '脾胃虚弱']
        },
        recommendations: {,
  lifestyle: ["规律作息", "适量运动', '保持心情愉悦'],
          dietary: ["温补脾胃", "活血化瘀', '避免生冷'],
          exercise: ["太极拳", "八段锦', '散步']
        }
      };
      setAnalysisResult(mockResult);
      onAnalysisResult?.(mockResult);
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
      Alert.alert("提示", "请先进行中医分析');
      return;
    }
    setIsRecommending(true);
    setHerbResult(null);
    try {
      // 模拟中药推荐结果
      const mockHerbResult: HerbRecommendationResponse = {,
  formula: {
      name: "补中益气汤加减",
      herbs: [
            {
      name: "黄芪", "
      dosage: '30g', function: '补气升阳' },
            {
      name: "党参", "
      dosage: '15g', function: '补中益气' },
            {
      name: "白术", "
      dosage: '12g', function: '健脾燥湿' },
            {
      name: "当归", "
      dosage: '10g', function: '补血活血' }
          ]
        },
        instructions: ["水煎服，每日一剂", "饭后30分钟服用', '连服7-14天'],
        precautions: ["孕妇慎用", "感冒发热时停服', '服药期间忌食生冷']
      };
      setHerbResult(mockHerbResult);
      onHerbResult?.(mockHerbResult);
    } catch (error) {
      console.error('中药推荐失败:', error);
      onError?.(error as Error);
      Alert.alert('推荐失败', (error as Error).message);
    } finally {
      setIsRecommending(false);
    }
  }, [analysisResult, symptoms, userId, onHerbResult, onError]);
  // 清除结果
  const handleClear = useCallback() => {
    setSymptoms(['']);
    setConstitutionType('balanced');
    setMedicalHistory('');
    setCurrentMedications('');
    setLifestyle({
      diet: "",
      exercise: '',
      sleep: '',
      stress: '',
      environment: ''
    });
    setAnalysisResult(null);
    setHerbResult(null);
  }, []);
  return (
  <ScrollView style={styles.container}>
      <Text style={styles.title}>中医智能分析</Text>
      {}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>症状描述</Text>
        {symptoms.map((symptom, index) => ())
          <View key={index} style={styles.symptomRow}>
            <TextInput
              style={styles.symptomInput}
              value={symptom}
              onChangeText={(value) => updateSymptom(index, value)}
              placeholder={`症状 ${index + 1}`}
            />
            {symptoms.length > 1  && <TouchableOpacity
                style={styles.removeButton}
                onPress={() => removeSymptom(index)}
              >
                <Text style={styles.removeButtonText}>删除</Text>
              </TouchableOpacity>
            )}
          </View>
        ))}
        <TouchableOpacity style={styles.addButton} onPress={addSymptom}>
          <Text style={styles.addButtonText}>添加症状</Text>
        </TouchableOpacity>
      </View>
      {}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>体质类型</Text>
        <View style={styles.constitutionGrid}>
          {constitutionTypes.map(type) => ()
            <TouchableOpacity
              key={type.value}
              style={{[
                styles.constitutionButton,
                constitutionType === type.value && styles.constitutionButtonActive;
              ]}}
              onPress={() => setConstitutionType(type.value)}
            >
              <Text
                style={{[
                  styles.constitutionButtonText,
                  constitutionType === type.value && styles.constitutionButtonTextActive;
                ]}}
              >
                {type.label}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </View>
      {}
      <View style={styles.buttonContainer}>
        <TouchableOpacity
          style={[styles.button, styles.primaryButton]}
          onPress={handleAnalysis}
          disabled={isAnalyzing}
        >
          {isAnalyzing ? ()
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.buttonText}>开始分析</Text>
          )}
        </TouchableOpacity>
        {analysisResult  && <TouchableOpacity
            style={[styles.button, styles.secondaryButton]}
            onPress={handleHerbRecommendation}
            disabled={isRecommending}
          >
            {isRecommending ? ()
              <ActivityIndicator color="#007AFF" />
            ) : (
              <Text style={[styles.buttonText, styles.secondaryButtonText]}>中药推荐</Text>
            )}
          </TouchableOpacity>
        )}
        <TouchableOpacity
          style={[styles.button, styles.clearButton]}
          onPress={handleClear}
        >
          <Text style={[styles.buttonText, styles.clearButtonText]}>清除</Text>
        </TouchableOpacity>
      </View>
      {}
      {analysisResult  && <View style={styles.resultSection}>
          <Text style={styles.resultTitle}>分析结果</Text>
          <View style={styles.resultCard}>
            <Text style={styles.resultLabel}>主要证型：</Text>
            <Text style={styles.resultValue}>{analysisResult.syndromeAnalysis.primarySyndrome}</Text>
                        <Text style={styles.resultLabel}>体质评估：</Text>
            <Text style={styles.resultValue}>{analysisResult.constitutionAssessment.constitutionType}</Text>
                        <Text style={styles.resultLabel}>生活建议：</Text>
            {analysisResult.recommendations.lifestyle.map((item, index) => ())
              <Text key={index} style={styles.recommendationItem}>• {item}</Text>
            ))}
          </View>
        </View>
      )}
      {}
      {herbResult  && <View style={styles.resultSection}>
          <Text style={styles.resultTitle}>中药推荐</Text>
          <View style={styles.resultCard}>
            <Text style={styles.resultLabel}>方剂名称：</Text>
            <Text style={styles.resultValue}>{herbResult.formula.name}</Text>
                        <Text style={styles.resultLabel}>药物组成：</Text>
            {herbResult.formula.herbs.map((herb, index) => ())
              <Text key={index} style={styles.herbItem}>
                {herb.name} {herb.dosage} - {herb.function}
              </Text>
            ))}
                        <Text style={styles.resultLabel}>服用方法：</Text>
            {herbResult.instructions.map((instruction, index) => ())
              <Text key={index} style={styles.instructionItem}>• {instruction}</Text>
            ))}
          </View>
        </View>
      )}
    </ScrollView>
  );
};
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#f5f5f5',
    padding: 16,
  },
  title: {,
  fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 24,
  },
  section: {,
  backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  sectionTitle: {,
  fontSize: 18,
    fontWeight: '600',
    color: '#333',
    marginBottom: 12,
  },
  symptomRow: {,
  flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  symptomInput: {,
  flex: 1,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
  },
  removeButton: {,
  marginLeft: 8,
    backgroundColor: '#FF3B30',
    borderRadius: 6,
    paddingHorizontal: 12,
    paddingVertical: 8,
  },
  removeButtonText: {,
  color: '#fff',
    fontSize: 14,
  },
  addButton: {,
  backgroundColor: '#007AFF',
    borderRadius: 8,
    padding: 12,
    alignItems: 'center',
    marginTop: 8,
  },
  addButtonText: {,
  color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  constitutionGrid: {,
  flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
  },
  constitutionButton: {,
  backgroundColor: '#f0f0f0',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 8,
    marginBottom: 8,
  },
  constitutionButtonActive: {,
  backgroundColor: '#007AFF',
  },
  constitutionButtonText: {,
  fontSize: 14,
    color: '#666',
  },
  constitutionButtonTextActive: {,
  color: '#fff',
  },
  buttonContainer: {,
  gap: 12,
    marginBottom: 24,
  },
  button: {,
  borderRadius: 12,
    padding: 16,
    alignItems: 'center',
  },
  primaryButton: {,
  backgroundColor: '#007AFF',
  },
  secondaryButton: {,
  backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#007AFF',
  },
  clearButton: {,
  backgroundColor: '#fff',
    borderWidth: 1,
    borderColor: '#FF3B30',
  },
  buttonText: {,
  fontSize: 16,
    fontWeight: '600',
    color: '#fff',
  },
  secondaryButtonText: {,
  color: '#007AFF',
  },
  clearButtonText: {,
  color: '#FF3B30',
  },
  resultSection: {,
  marginBottom: 24,
  },
  resultTitle: {,
  fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 12,
  },
  resultCard: {,
  backgroundColor: '#fff',
    borderRadius: 12,
    padding: 16,
  },
  resultLabel: {,
  fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginTop: 12,
    marginBottom: 4,
  },
  resultValue: {,
  fontSize: 16,
    color: '#666',
    marginBottom: 8,
  },
  recommendationItem: {,
  fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
  herbItem: {,
  fontSize: 14,
    color: '#666',
    marginBottom: 4,
    paddingLeft: 8,
  },
  instructionItem: {,
  fontSize: 14,
    color: '#666',
    marginBottom: 4,
  },
});
export default TCMAnalysisComponent;
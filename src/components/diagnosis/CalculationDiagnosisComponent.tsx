import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  Alert,
  ActivityIndicator,
  Dimensions,
  Platform,
} from 'react-native';
import { Picker } from '@react-native-picker/picker';
import DateTimePicker from '@react-native-community/datetimepicker';
import { fiveDiagnosisService, CalculationDiagnosisData } from '../../services/fiveDiagnosisService';
interface CalculationDiagnosisProps {
  onComplete: (data: CalculationDiagnosisData) => void;
  onCancel: () => void;
}
interface PersonalInfo {
  birthYear: number;
  birthMonth: number;
  birthDay: number;
  birthHour: number;
  gender: string;
  location: string;
}
interface AnalysisTypes {
  ziwuLiuzhu: boolean;
  constitution: boolean;
  bagua: boolean;
  wuyunLiuqi: boolean;
  comprehensive: boolean;
}
const { width: screenWidth } = Dimensions.get('window');
export default React.memo(function CalculationDiagnosisComponent({
  onComplete,
  onCancel,
}: CalculationDiagnosisProps) {
  const [personalInfo, setPersonalInfo] = useState<PersonalInfo>({
    birthYear: new Date().getFullYear() - 30,
    birthMonth: 1,
    birthDay: 1,
    birthHour: 12,
    gender: '男',
    location: '北京',
  });
  const [analysisTypes, setAnalysisTypes] = useState<AnalysisTypes>({
    ziwuLiuzhu: true,
    constitution: true,
    bagua: false,
    wuyunLiuqi: false,
    comprehensive: true,
  });
  const [healthConcerns, setHealthConcerns] = useState<string[]>([]);
  const [newConcern, setNewConcern] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [showTimePicker, setShowTimePicker] = useState(false);
  // 预定义的健康关注点
  const predefinedConcerns = [
    "体质调理",养生保健',
    "睡眠质量",消化系统',
    "情绪调节",免疫力提升',
    "慢性疲劳",亚健康状态',
  ];
  // 城市列表
  const cities = [
    "北京",上海', "广州",深圳', "杭州",南京', "苏州",成都',
    "重庆",武汉', "西安",天津', "青岛",大连', "厦门",长沙',
  ];
  // 时辰对应表
  const timeHours = [
    {
      label: "子时 (23:00-01:00)",
      value: 0 },
    {
      label: "丑时 (01:00-03:00)",
      value: 2 },
    {
      label: "寅时 (03:00-05:00)",
      value: 4 },
    {
      label: "卯时 (05:00-07:00)",
      value: 6 },
    {
      label: "辰时 (07:00-09:00)",
      value: 8 },
    {
      label: "巳时 (09:00-11:00)",
      value: 10 },
    {
      label: "午时 (11:00-13:00)",
      value: 12 },
    {
      label: "未时 (13:00-15:00)",
      value: 14 },
    {
      label: "申时 (15:00-17:00)",
      value: 16 },
    {
      label: "酉时 (17:00-19:00)",
      value: 18 },
    {
      label: "戌时 (19:00-21:00)",
      value: 20 },
    {
      label: "亥时 (21:00-23:00)",
      value: 22 },
  ];
  // 添加健康关注点
  const addHealthConcern = useCallback(concern: string) => {
    if (concern.trim() && !healthConcerns.includes(concern.trim())) {
      setHealthConcerns(prev => [...prev, concern.trim()]);
      setNewConcern('');
    }
  }, [healthConcerns]);
  // 移除健康关注点
  const removeHealthConcern = useCallback(concern: string) => {
    setHealthConcerns(prev => prev.filter(c => c !== concern));
  }, []);
  // 切换分析类型
  const toggleAnalysisType = useCallback(type: keyof AnalysisTypes) => {
    setAnalysisTypes(prev => ({
      ...prev,
      [type]: !prev[type],
    }));
  }, []);
  // 验证输入数据
  const validateInput = (): boolean => {
    if (personalInfo.birthYear < 1900 || personalInfo.birthYear > new Date().getFullYear()) {
      Alert.alert("输入错误",请输入有效的出生年份');
      return false;
    }
    if (personalInfo.birthMonth < 1 || personalInfo.birthMonth > 12) {
      Alert.alert("输入错误",请输入有效的出生月份');
      return false;
    }
    if (personalInfo.birthDay < 1 || personalInfo.birthDay > 31) {
      Alert.alert("输入错误",请输入有效的出生日期');
      return false;
    }
    if (!Object.values(analysisTypes).some(Boolean)) {
      Alert.alert("选择错误",请至少选择一种算诊分析类型');
      return false;
    }
    return true;
  };
  // 提交算诊数据
  const handleSubmit = useCallback(async () => {
    if (!validateInput()) {
      return;
    }
    setIsProcessing(true);
    try {
      const calculationData: CalculationDiagnosisData = {
        personalInfo,
        analysisTypes,
        currentTime: new Date().toISOString(),
        healthConcerns,
      };
      // 可以在这里调用算诊分析API进行预处理
      await new Promise(resolve => setTimeout(resolve, 1000)); // 模拟处理时间
      onComplete(calculationData);
    } catch (error) {
      console.error('算诊数据处理失败:', error);
      Alert.alert("处理失败",算诊数据处理失败，请重试');
    } finally {
      setIsProcessing(false);
    }
  }, [personalInfo, analysisTypes, healthConcerns, onComplete]);
  // 渲染个人信息输入
  const renderPersonalInfoSection = () => (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>个人信息</Text>
      <View style={styles.inputGroup}>
        <Text style={styles.inputLabel}>出生年份</Text>
        <TextInput;
          style={styles.textInput}
          value={personalInfo.birthYear.toString()}
          onChangeText={(text) => {
            const year = parseInt(text) || new Date().getFullYear() - 30;
            setPersonalInfo(prev => ({ ...prev, birthYear: year }));
          }}
          keyboardType="numeric"
          placeholder="例如：1990"
        />
      </View>
      <View style={styles.inputRow}>
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>出生月份</Text>
          <View style={styles.pickerContainer}>
            <Picker;
              selectedValue={personalInfo.birthMonth}
              onValueChange={(value) => setPersonalInfo(prev => ({ ...prev, birthMonth: value }))}
              style={styles.picker}
            >
              {Array.from({ length: 12 }, (_, i) => (
                <Picker.Item key={i + 1} label={`${i + 1}月`} value={i + 1} />
              ))}
            </Picker>
          </View>
        </View>
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>出生日期</Text>
          <View style={styles.pickerContainer}>
            <Picker;
              selectedValue={personalInfo.birthDay}
              onValueChange={(value) => setPersonalInfo(prev => ({ ...prev, birthDay: value }))}
              style={styles.picker}
            >
              {Array.from({ length: 31 }, (_, i) => (
                <Picker.Item key={i + 1} label={`${i + 1}日`} value={i + 1} />
              ))}
            </Picker>
          </View>
        </View>
      </View>
      <View style={styles.inputGroup}>
        <Text style={styles.inputLabel}>出生时辰</Text>
        <View style={styles.pickerContainer}>
          <Picker;
            selectedValue={personalInfo.birthHour}
            onValueChange={(value) => setPersonalInfo(prev => ({ ...prev, birthHour: value }))}
            style={styles.picker}
          >
            {timeHours.map(time) => (
              <Picker.Item key={time.value} label={time.label} value={time.value} />
            ))}
          </Picker>
        </View>
      </View>
      <View style={styles.inputRow}>
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>性别</Text>
          <View style={styles.pickerContainer}>
            <Picker;
              selectedValue={personalInfo.gender}
              onValueChange={(value) => setPersonalInfo(prev => ({ ...prev, gender: value }))}
              style={styles.picker}
            >
              <Picker.Item label="男" value="男" />
              <Picker.Item label="女" value="女" />
            </Picker>
          </View>
        </View>
        <View style={styles.inputGroup}>
          <Text style={styles.inputLabel}>出生地</Text>
          <View style={styles.pickerContainer}>
            <Picker;
              selectedValue={personalInfo.location}
              onValueChange={(value) => setPersonalInfo(prev => ({ ...prev, location: value }))}
              style={styles.picker}
            >
              {cities.map(city) => (
                <Picker.Item key={city} label={city} value={city} />
              ))}
            </Picker>
          </View>
        </View>
      </View>
    </View>
  );
  // 渲染分析类型选择
  const renderAnalysisTypesSection = () => (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>算诊分析类型</Text>
      <TouchableOpacity;
        style={[styles.analysisOption, analysisTypes.ziwuLiuzhu && styles.analysisOptionSelected]}
        onPress={() => toggleAnalysisType('ziwuLiuzhu')}
      >
        <Text style={styles.analysisOptionIcon}>🕐</Text>
        <View style={styles.analysisOptionContent}>
          <Text style={[styles.analysisOptionTitle, analysisTypes.ziwuLiuzhu && styles.analysisOptionTitleSelected]}>
            子午流注分析
          </Text>
          <Text style={styles.analysisOptionDescription}>
            根据十二时辰经络流注规律，分析最佳养生时机
          </Text>
        </View>
        <View style={[styles.checkbox, analysisTypes.ziwuLiuzhu && styles.checkboxSelected]}>
          {analysisTypes.ziwuLiuzhu && <Text style={styles.checkmark}>✓</Text>}
        </View>
      </TouchableOpacity>
      <TouchableOpacity;
        style={[styles.analysisOption, analysisTypes.constitution && styles.analysisOptionSelected]}
        onPress={() => toggleAnalysisType('constitution')}
      >
        <Text style={styles.analysisOptionIcon}>🎭</Text>
        <View style={styles.analysisOptionContent}>
          <Text style={[styles.analysisOptionTitle, analysisTypes.constitution && styles.analysisOptionTitleSelected]}>
            八字体质分析
          </Text>
          <Text style={styles.analysisOptionDescription}>
            基于出生八字分析先天体质特征和健康倾向
          </Text>
        </View>
        <View style={[styles.checkbox, analysisTypes.constitution && styles.checkboxSelected]}>
          {analysisTypes.constitution && <Text style={styles.checkmark}>✓</Text>}
        </View>
      </TouchableOpacity>
      <TouchableOpacity;
        style={[styles.analysisOption, analysisTypes.bagua && styles.analysisOptionSelected]}
        onPress={() => toggleAnalysisType('bagua')}
      >
        <Text style={styles.analysisOptionIcon}>☯️</Text>
        <View style={styles.analysisOptionContent}>
          <Text style={[styles.analysisOptionTitle, analysisTypes.bagua && styles.analysisOptionTitleSelected]}>
            八卦配属分析
          </Text>
          <Text style={styles.analysisOptionDescription}>
            运用八卦理论分析个人五行属性和健康调理方向
          </Text>
        </View>
        <View style={[styles.checkbox, analysisTypes.bagua && styles.checkboxSelected]}>
          {analysisTypes.bagua && <Text style={styles.checkmark}>✓</Text>}
        </View>
      </TouchableOpacity>
      <TouchableOpacity;
        style={[styles.analysisOption, analysisTypes.wuyunLiuqi && styles.analysisOptionSelected]}
        onPress={() => toggleAnalysisType('wuyunLiuqi')}
      >
        <Text style={styles.analysisOptionIcon}>🌊</Text>
        <View style={styles.analysisOptionContent}>
          <Text style={[styles.analysisOptionTitle, analysisTypes.wuyunLiuqi && styles.analysisOptionTitleSelected]}>
            五运六气分析
          </Text>
          <Text style={styles.analysisOptionDescription}>
            结合当前时令分析气候对健康的影响和调养建议
          </Text>
        </View>
        <View style={[styles.checkbox, analysisTypes.wuyunLiuqi && styles.checkboxSelected]}>
          {analysisTypes.wuyunLiuqi && <Text style={styles.checkmark}>✓</Text>}
        </View>
      </TouchableOpacity>
      <TouchableOpacity;
        style={[styles.analysisOption, analysisTypes.comprehensive && styles.analysisOptionSelected]}
        onPress={() => toggleAnalysisType('comprehensive')}
      >
        <Text style={styles.analysisOptionIcon}>🧮</Text>
        <View style={styles.analysisOptionContent}>
          <Text style={[styles.analysisOptionTitle, analysisTypes.comprehensive && styles.analysisOptionTitleSelected]}>
            综合算诊分析
          </Text>
          <Text style={styles.analysisOptionDescription}>
            整合多种算诊方法，提供全面的健康分析报告
          </Text>
        </View>
        <View style={[styles.checkbox, analysisTypes.comprehensive && styles.checkboxSelected]}>
          {analysisTypes.comprehensive && <Text style={styles.checkmark}>✓</Text>}
        </View>
      </TouchableOpacity>
    </View>
  );
  // 渲染健康关注点
  const renderHealthConcernsSection = () => (
    <View style={styles.section}>
      <Text style={styles.sectionTitle}>健康关注点</Text>
      <View style={styles.concernsContainer}>
        {predefinedConcerns.map(concern) => (
          <TouchableOpacity;
            key={concern}
            style={[
              styles.concernChip,
              healthConcerns.includes(concern) && styles.concernChipSelected,
            ]}
            onPress={() => {
              if (healthConcerns.includes(concern)) {
                removeHealthConcern(concern);
              } else {
                addHealthConcern(concern);
              }
            }}
          >
            <Text style={[
              styles.concernChipText,
              healthConcerns.includes(concern) && styles.concernChipTextSelected,
            ]}>
              {concern}
            </Text>
          </TouchableOpacity>
        ))}
      </View>
      <View style={styles.customConcernContainer}>
        <TextInput;
          style={styles.customConcernInput}
          value={newConcern}
          onChangeText={setNewConcern}
          placeholder="添加自定义关注点..."
          onSubmitEditing={() => addHealthConcern(newConcern)}
        />
        <TouchableOpacity;
          style={styles.addConcernButton}
          onPress={() => addHealthConcern(newConcern)}
          disabled={!newConcern.trim()}
        >
          <Text style={styles.addConcernButtonText}>添加</Text>
        </TouchableOpacity>
      </View>
      {healthConcerns.length > 0 && (
        <View style={styles.selectedConcerns}>
          <Text style={styles.selectedConcernsTitle}>已选择的关注点：</Text>
          <View style={styles.selectedConcernsList}>
            {healthConcerns.map(concern) => (
              <View key={concern} style={styles.selectedConcernItem}>
                <Text style={styles.selectedConcernText}>{concern}</Text>
                <TouchableOpacity;
                  style={styles.removeConcernButton}
                  onPress={() => removeHealthConcern(concern)}
                >
                  <Text style={styles.removeConcernButtonText}>×</Text>
                </TouchableOpacity>
              </View>
            ))}
          </View>
        </View>
      )}
    </View>
  );
  return (
    <ScrollView style={styles.container} showsVerticalScrollIndicator={false}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>算诊分析</Text>
        <Text style={styles.headerSubtitle}>传统中医数字化算诊系统</Text>
      </View>
      {renderPersonalInfoSection()}
      {renderAnalysisTypesSection()}
      {renderHealthConcernsSection()}
      <View style={styles.actionContainer}>
        <TouchableOpacity;
          style={styles.cancelButton}
          onPress={onCancel}
          disabled={isProcessing}
        >
          <Text style={styles.cancelButtonText}>取消</Text>
        </TouchableOpacity>
        <TouchableOpacity;
          style={[styles.submitButton, isProcessing && styles.submitButtonDisabled]}
          onPress={handleSubmit}
          disabled={isProcessing}
        >
          {isProcessing ? (
            <ActivityIndicator size="small" color="#ffffff" />
          ) : (
            <Text style={styles.submitButtonText}>开始算诊</Text>
          )}
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
});
const styles = StyleSheet.create({
  container: {,
  flex: 1,
    backgroundColor: '#f8f9fa',
  },
  header: {,
  backgroundColor: '#ffffff',
    padding: 20,
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
  },
  headerTitle: {,
  fontSize: 24,
    fontWeight: '700',
    color: '#1a1a1a',
    marginBottom: 5,
  },
  headerSubtitle: {,
  fontSize: 16,
    color: '#6c757d',
  },
  section: {,
  backgroundColor: '#ffffff',
    margin: 15,
    borderRadius: 12,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: {,
  width: 0,
      height: 2,
    },
    shadowOpacity: 0.1,
    shadowRadius: 3.84,
    elevation: 5,
  },
  sectionTitle: {,
  fontSize: 18,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 15,
  },
  inputGroup: {,
  marginBottom: 15,
  },
  inputRow: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
  },
  inputLabel: {,
  fontSize: 16,
    fontWeight: '500',
    color: '#1a1a1a',
    marginBottom: 8,
  },
  textInput: {,
  borderWidth: 1,
    borderColor: '#e9ecef',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    backgroundColor: '#ffffff',
  },
  pickerContainer: {,
  borderWidth: 1,
    borderColor: '#e9ecef',
    borderRadius: 8,
    backgroundColor: '#ffffff',
  },
  picker: {,
  height: 50,
  },
  analysisOption: {,
  flexDirection: 'row',
    alignItems: 'center',
    padding: 15,
    borderWidth: 1,
    borderColor: '#e9ecef',
    borderRadius: 8,
    marginBottom: 10,
    backgroundColor: '#f8f9fa',
  },
  analysisOptionSelected: {,
  borderColor: '#007AFF',
    backgroundColor: '#e3f2fd',
  },
  analysisOptionIcon: {,
  fontSize: 24,
    marginRight: 15,
  },
  analysisOptionContent: {,
  flex: 1,
  },
  analysisOptionTitle: {,
  fontSize: 16,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 4,
  },
  analysisOptionTitleSelected: {,
  color: '#007AFF',
  },
  analysisOptionDescription: {,
  fontSize: 14,
    color: '#6c757d',
    lineHeight: 20,
  },
  checkbox: {,
  width: 24,
    height: 24,
    borderWidth: 2,
    borderColor: '#e9ecef',
    borderRadius: 4,
    justifyContent: 'center',
    alignItems: 'center',
  },
  checkboxSelected: {,
  borderColor: '#007AFF',
    backgroundColor: '#007AFF',
  },
  checkmark: {,
  color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  concernsContainer: {,
  flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 15,
  },
  concernChip: {,
  backgroundColor: '#e9ecef',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    margin: 4,
  },
  concernChipSelected: {,
  backgroundColor: '#007AFF',
  },
  concernChipText: {,
  fontSize: 14,
    color: '#6c757d',
  },
  concernChipTextSelected: {,
  color: '#ffffff',
  },
  customConcernContainer: {,
  flexDirection: 'row',
    marginBottom: 15,
  },
  customConcernInput: {,
  flex: 1,
    borderWidth: 1,
    borderColor: '#e9ecef',
    borderRadius: 8,
    padding: 12,
    fontSize: 16,
    marginRight: 10,
  },
  addConcernButton: {,
  backgroundColor: '#007AFF',
    paddingHorizontal: 20,
    paddingVertical: 12,
    borderRadius: 8,
    justifyContent: 'center',
  },
  addConcernButtonText: {,
  color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  selectedConcerns: {,
  marginTop: 15,
  },
  selectedConcernsTitle: {,
  fontSize: 16,
    fontWeight: '500',
    color: '#1a1a1a',
    marginBottom: 10,
  },
  selectedConcernsList: {,
  flexDirection: 'row',
    flexWrap: 'wrap',
  },
  selectedConcernItem: {,
  flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#28a745',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 16,
    margin: 2,
  },
  selectedConcernText: {,
  color: '#ffffff',
    fontSize: 14,
    marginRight: 8,
  },
  removeConcernButton: {,
  width: 20,
    height: 20,
    borderRadius: 10,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  removeConcernButtonText: {,
  color: '#ffffff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  actionContainer: {,
  flexDirection: 'row',
    justifyContent: 'space-between',
    padding: 20,
    paddingBottom: 40,
  },
  cancelButton: {,
  flex: 1,
    backgroundColor: '#6c757d',
    paddingVertical: 15,
    borderRadius: 8,
    marginRight: 10,
    alignItems: 'center',
  },
  cancelButtonText: {,
  color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  submitButton: {,
  flex: 2,
    backgroundColor: '#007AFF',
    paddingVertical: 15,
    borderRadius: 8,
    marginLeft: 10,
    alignItems: 'center',
  },
  submitButtonDisabled: {,
  backgroundColor: '#adb5bd',
  },
  submitButtonText: {,
  color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
});
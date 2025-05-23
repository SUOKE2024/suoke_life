import React, { useState, useEffect } from 'react';
import { View, StyleSheet, ScrollView, Image, TouchableOpacity } from 'react-native';
import { Text, Card, Button, Divider, Avatar, Title, Paragraph, List, Chip, SegmentedButtons, ActivityIndicator } from 'react-native-paper';
import { useTheme } from 'react-native-paper';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import Slider from '@react-native-community/slider';
import { palpationService } from '../../services/diagnostic';

interface PalpationDiagnosisProps {
  onComplete: (results: any) => void;
  onCancel: () => void;
}

// 脉象位置类型
type PulsePosition = 'leftCun' | 'leftGuan' | 'leftChi' | 'rightCun' | 'rightGuan' | 'rightChi';

// 脉象数据类型
interface PulsePointData {
  strength: number;
  rhythm: string;
  characteristic: string;
}

// 所有脉象数据类型
type PulseData = Record<PulsePosition, PulsePointData>;

const PalpationDiagnosis: React.FC<PalpationDiagnosisProps> = ({ onComplete, onCancel }) => {
  const theme = useTheme();
  const [currentStep, setCurrentStep] = useState(0);
  const [pulseData, setPulseData] = useState<PulseData>({
    leftCun: { strength: 0.5, rhythm: 'normal', characteristic: '' },
    leftGuan: { strength: 0.5, rhythm: 'normal', characteristic: '' },
    leftChi: { strength: 0.5, rhythm: 'normal', characteristic: '' },
    rightCun: { strength: 0.5, rhythm: 'normal', characteristic: '' },
    rightGuan: { strength: 0.5, rhythm: 'normal', characteristic: '' },
    rightChi: { strength: 0.5, rhythm: 'normal', characteristic: '' },
  });
  const [selectedPulseCharacteristic, setSelectedPulseCharacteristic] = useState('');
  const [bodyPoints, setBodyPoints] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [apiError, setApiError] = useState('');
  const [pulseReferences, setPulseReferences] = useState<any[]>([]);
  const [isLoadingReferences, setIsLoadingReferences] = useState(false);
  
  // 获取脉诊参考资料
  useEffect(() => {
    fetchPulseReferences();
  }, []);
  
  // 从API获取脉诊参考资料
  const fetchPulseReferences = async () => {
    setIsLoadingReferences(true);
    
    try {
      const response = await palpationService.getPulseReferences();
      
      if (response.success) {
        setPulseReferences(response.data);
      }
    } catch (error) {
      console.error('Error fetching pulse references:', error);
    } finally {
      setIsLoadingReferences(false);
    }
  };
  
  // 切诊步骤
  const steps = [
    { title: '脉诊', description: '检测双手寸关尺六脉' },
    { title: '腹诊', description: '腹部触诊检查' },
    { title: '分析结果', description: '综合分析切诊结果' }
  ];
  
  // 脉象特征选项
  const pulseCharacteristics = [
    { value: 'fu', label: '浮脉 (表证)' },
    { value: 'chen', label: '沉脉 (里证)' },
    { value: 'chi', label: '迟脉 (寒证)' },
    { value: 'shu', label: '数脉 (热证)' },
    { value: 'xu', label: '虚脉 (虚证)' },
    { value: 'shi', label: '实脉 (实证)' },
    { value: 'hua', label: '滑脉 (痰湿)' },
    { value: 'se', label: '涩脉 (血虚)' },
    { value: 'xian', label: '弦脉 (肝胆)' },
    { value: 'hong', label: '洪脉 (阳盛)' }
  ];
  
  // 处理脉搏强度变化
  const handlePulseStrengthChange = (position: PulsePosition, value: number) => {
    setPulseData({
      ...pulseData,
      [position]: {
        ...pulseData[position],
        strength: value
      }
    });
  };
  
  // 处理脉搏特征选择
  const handlePulseCharacteristicSelect = (position: PulsePosition, value: string) => {
    setPulseData({
      ...pulseData,
      [position]: {
        ...pulseData[position],
        characteristic: value
      }
    });
    setSelectedPulseCharacteristic(value);
  };
  
  // 提交切诊数据到API
  const submitToApi = async () => {
    const diagnosisData = {
      pulse_data: pulseData,
      body_points: bodyPoints
    };
    
    setIsLoading(true);
    setApiError('');
    
    try {
      const response = await palpationService.submitDiagnosis(diagnosisData);
      
      if (response.success) {
        // 成功响应，获取分析结果
        const finalResult = {
          ...diagnosisData,
          analysis: response.data.analysis || getAnalysisResult()
        };
        
        onComplete(finalResult);
      } else {
        // API调用成功但处理失败
        setApiError(response.message || '分析失败，已使用本地分析结果');
        
        // 依然使用本地分析结果继续
        const fallbackResult = {
          ...diagnosisData,
          analysis: getAnalysisResult(),
          api_error: response.message
        };
        
        onComplete(fallbackResult);
      }
    } catch (error) {
      console.error('Palpation diagnosis error:', error);
      setApiError('服务连接失败，已使用本地分析结果');
      
      // 使用本地分析结果作为备选
      const fallbackResult = {
        ...diagnosisData,
        analysis: getAnalysisResult(),
        api_error: '服务连接失败'
      };
      
      onComplete(fallbackResult);
    } finally {
      setIsLoading(false);
    }
  };
  
  // 下一步
  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      // 完成所有步骤，提交API
      submitToApi();
    }
  };
  
  // 上一步
  const handlePrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    } else {
      onCancel();
    }
  };
  
  // 检查当前步骤是否完成
  const isStepComplete = () => {
    switch (currentStep) {
      case 0:
        // 脉诊至少需要填写一个位置的特征
        return Object.values(pulseData).some(data => data.characteristic !== '');
      case 1:
        return true; // 腹诊可以为空
      case 2:
        return true; // 分析结果总是可以完成
      default:
        return false;
    }
  };
  
  // 生成分析结果
  const getAnalysisResult = () => {
    // 这里应该有更复杂的分析逻辑
    // 目前只是一个简单的演示
    
    let constitution = '';
    let recommendation = '';
    
    // 检查是否有多个脉位显示相同特征
    const characteristics = Object.values(pulseData).map(data => data.characteristic);
    const uniqueCharacteristics = [...new Set(characteristics.filter(c => c !== ''))];
    
    if (uniqueCharacteristics.includes('fu')) {
      constitution = '表证';
      recommendation = '建议解表';
    } else if (uniqueCharacteristics.includes('chen')) {
      constitution = '里证';
      recommendation = '建议温里';
    } else if (uniqueCharacteristics.includes('chi')) {
      constitution = '寒证';
      recommendation = '建议温阳';
    } else if (uniqueCharacteristics.includes('shu')) {
      constitution = '热证';
      recommendation = '建议清热';
    } else if (uniqueCharacteristics.includes('xu')) {
      constitution = '虚证';
      recommendation = '建议补益';
    } else if (uniqueCharacteristics.includes('shi')) {
      constitution = '实证';
      recommendation = '建议泻实';
    } else if (uniqueCharacteristics.includes('hua')) {
      constitution = '痰湿体质';
      recommendation = '建议化痰祛湿';
    } else if (uniqueCharacteristics.includes('se')) {
      constitution = '血虚体质';
      recommendation = '建议补血养血';
    } else if (uniqueCharacteristics.includes('xian')) {
      constitution = '肝胆郁热';
      recommendation = '建议疏肝利胆';
    } else if (uniqueCharacteristics.includes('hong')) {
      constitution = '阳盛体质';
      recommendation = '建议滋阴降火';
    } else {
      constitution = '未定体质';
      recommendation = '需结合其他诊法进一步确定';
    }
    
    return {
      constitution,
      recommendation
    };
  };
  
  // 渲染当前步骤内容
  const renderStepContent = () => {
    const step = steps[currentStep];
    
    return (
      <Card style={styles.stepCard}>
        <Card.Title
          title={step.title}
          subtitle={step.description}
          left={(props) => <Avatar.Icon {...props} icon="hand" color="#fff" style={{ backgroundColor: theme.colors.primary }} />}
        />
        <Divider />
        <Card.Content style={styles.cardContent}>
          {currentStep === 0 && (
            <ScrollView>
              <Title style={styles.sectionTitle}>脉象检测</Title>
              <Paragraph style={styles.instruction}>
                通过检测双手腕部的寸关尺六脉，可以判断全身脏腑功能状态。
              </Paragraph>
              
              {isLoadingReferences ? (
                <View style={styles.loadingContainer}>
                  <ActivityIndicator size="small" color={theme.colors.primary} />
                  <Text style={styles.loadingText}>加载脉诊参考资料...</Text>
                </View>
              ) : pulseReferences.length > 0 && (
                <Card style={styles.referencesCard}>
                  <Card.Title title="脉诊参考资料" />
                  <Card.Content>
                    <ScrollView horizontal showsHorizontalScrollIndicator={false}>
                      {pulseReferences.map((reference, index) => (
                        <Card key={index} style={styles.referenceItemCard}>
                          <Card.Cover source={{ uri: reference.image_url }} style={styles.referenceImage} />
                          <Card.Content>
                            <Title style={styles.referenceTitle}>{reference.name}</Title>
                            <Paragraph>{reference.description}</Paragraph>
                          </Card.Content>
                        </Card>
                      ))}
                    </ScrollView>
                  </Card.Content>
                </Card>
              )}
              
              <View style={styles.pulseImageContainer}>
                <View style={styles.pulseImagePlaceholder}>
                  <Icon name="hand-pointing-right" size={80} color={theme.colors.primary} />
                  <Text style={styles.pulseImageText}>脉位示意图</Text>
                </View>
              </View>
              
              <Title style={styles.subsectionTitle}>左手脉象</Title>
              
              {/* 左寸 */}
              <Card style={styles.pulseCard}>
                <Card.Title title="左寸" subtitle="对应心、小肠" />
                <Card.Content>
                  <Text style={styles.sliderLabel}>脉搏强度</Text>
                  <Slider
                    value={pulseData.leftCun.strength}
                    onValueChange={(value) => handlePulseStrengthChange('leftCun', value)}
                    minimumValue={0}
                    maximumValue={1}
                    step={0.1}
                    minimumTrackTintColor={theme.colors.primary}
                    thumbTintColor={theme.colors.primary}
                  />
                  <View style={styles.sliderLabels}>
                    <Text>弱</Text>
                    <Text>中</Text>
                    <Text>强</Text>
                  </View>
                  
                  <Divider style={styles.divider} />
                  
                  <Text style={styles.sliderLabel}>脉象特征</Text>
                  <View style={styles.pulseCharacteristicsContainer}>
                    {pulseCharacteristics.slice(0, 5).map((characteristic) => (
                      <Chip
                        key={characteristic.value}
                        selected={pulseData.leftCun.characteristic === characteristic.value}
                        onPress={() => handlePulseCharacteristicSelect('leftCun', characteristic.value)}
                        style={styles.pulseChip}
                      >
                        {characteristic.label}
                      </Chip>
                    ))}
                  </View>
                  <View style={styles.pulseCharacteristicsContainer}>
                    {pulseCharacteristics.slice(5).map((characteristic) => (
                      <Chip
                        key={characteristic.value}
                        selected={pulseData.leftCun.characteristic === characteristic.value}
                        onPress={() => handlePulseCharacteristicSelect('leftCun', characteristic.value)}
                        style={styles.pulseChip}
                      >
                        {characteristic.label}
                      </Chip>
                    ))}
                  </View>
                </Card.Content>
              </Card>
              
              {/* 左关 */}
              <Card style={styles.pulseCard}>
                <Card.Title title="左关" subtitle="对应肝、胆" />
                <Card.Content>
                  <Text style={styles.sliderLabel}>脉搏强度</Text>
                  <Slider
                    value={pulseData.leftGuan.strength}
                    onValueChange={(value) => handlePulseStrengthChange('leftGuan', value)}
                    minimumValue={0}
                    maximumValue={1}
                    step={0.1}
                    minimumTrackTintColor={theme.colors.primary}
                    thumbTintColor={theme.colors.primary}
                  />
                  <View style={styles.sliderLabels}>
                    <Text>弱</Text>
                    <Text>中</Text>
                    <Text>强</Text>
                  </View>
                  
                  <Divider style={styles.divider} />
                  
                  <Text style={styles.sliderLabel}>脉象特征</Text>
                  <View style={styles.pulseCharacteristicsContainer}>
                    {pulseCharacteristics.slice(0, 5).map((characteristic) => (
                      <Chip
                        key={characteristic.value}
                        selected={pulseData.leftGuan.characteristic === characteristic.value}
                        onPress={() => handlePulseCharacteristicSelect('leftGuan', characteristic.value)}
                        style={styles.pulseChip}
                      >
                        {characteristic.label}
                      </Chip>
                    ))}
                  </View>
                  <View style={styles.pulseCharacteristicsContainer}>
                    {pulseCharacteristics.slice(5).map((characteristic) => (
                      <Chip
                        key={characteristic.value}
                        selected={pulseData.leftGuan.characteristic === characteristic.value}
                        onPress={() => handlePulseCharacteristicSelect('leftGuan', characteristic.value)}
                        style={styles.pulseChip}
                      >
                        {characteristic.label}
                      </Chip>
                    ))}
                  </View>
                </Card.Content>
              </Card>
              
              {/* 左尺 */}
              <Card style={styles.pulseCard}>
                <Card.Title title="左尺" subtitle="对应肾、膀胱" />
                <Card.Content>
                  <Text style={styles.sliderLabel}>脉搏强度</Text>
                  <Slider
                    value={pulseData.leftChi.strength}
                    onValueChange={(value) => handlePulseStrengthChange('leftChi', value)}
                    minimumValue={0}
                    maximumValue={1}
                    step={0.1}
                    minimumTrackTintColor={theme.colors.primary}
                    thumbTintColor={theme.colors.primary}
                  />
                  <View style={styles.sliderLabels}>
                    <Text>弱</Text>
                    <Text>中</Text>
                    <Text>强</Text>
                  </View>
                  
                  <Divider style={styles.divider} />
                  
                  <Text style={styles.sliderLabel}>脉象特征</Text>
                  <View style={styles.pulseCharacteristicsContainer}>
                    {pulseCharacteristics.slice(0, 5).map((characteristic) => (
                      <Chip
                        key={characteristic.value}
                        selected={pulseData.leftChi.characteristic === characteristic.value}
                        onPress={() => handlePulseCharacteristicSelect('leftChi', characteristic.value)}
                        style={styles.pulseChip}
                      >
                        {characteristic.label}
                      </Chip>
                    ))}
                  </View>
                  <View style={styles.pulseCharacteristicsContainer}>
                    {pulseCharacteristics.slice(5).map((characteristic) => (
                      <Chip
                        key={characteristic.value}
                        selected={pulseData.leftChi.characteristic === characteristic.value}
                        onPress={() => handlePulseCharacteristicSelect('leftChi', characteristic.value)}
                        style={styles.pulseChip}
                      >
                        {characteristic.label}
                      </Chip>
                    ))}
                  </View>
                </Card.Content>
              </Card>
              
              <Title style={styles.subsectionTitle}>右手脉象</Title>
              
              {/* 右寸 */}
              <Card style={styles.pulseCard}>
                <Card.Title title="右寸" subtitle="对应肺、大肠" />
                <Card.Content>
                  <Text style={styles.sliderLabel}>脉搏强度</Text>
                  <Slider
                    value={pulseData.rightCun.strength}
                    onValueChange={(value) => handlePulseStrengthChange('rightCun', value)}
                    minimumValue={0}
                    maximumValue={1}
                    step={0.1}
                    minimumTrackTintColor={theme.colors.primary}
                    thumbTintColor={theme.colors.primary}
                  />
                  <View style={styles.sliderLabels}>
                    <Text>弱</Text>
                    <Text>中</Text>
                    <Text>强</Text>
                  </View>
                  
                  <Divider style={styles.divider} />
                  
                  <Text style={styles.sliderLabel}>脉象特征</Text>
                  <View style={styles.pulseCharacteristicsContainer}>
                    {pulseCharacteristics.slice(0, 5).map((characteristic) => (
                      <Chip
                        key={characteristic.value}
                        selected={pulseData.rightCun.characteristic === characteristic.value}
                        onPress={() => handlePulseCharacteristicSelect('rightCun', characteristic.value)}
                        style={styles.pulseChip}
                      >
                        {characteristic.label}
                      </Chip>
                    ))}
                  </View>
                  <View style={styles.pulseCharacteristicsContainer}>
                    {pulseCharacteristics.slice(5).map((characteristic) => (
                      <Chip
                        key={characteristic.value}
                        selected={pulseData.rightCun.characteristic === characteristic.value}
                        onPress={() => handlePulseCharacteristicSelect('rightCun', characteristic.value)}
                        style={styles.pulseChip}
                      >
                        {characteristic.label}
                      </Chip>
                    ))}
                  </View>
                </Card.Content>
              </Card>
              
              {/* 其他脉位可以类似实现 */}
              <Paragraph style={styles.note}>
                注: 实际操作中应由专业中医执行脉诊，此处仅作示例演示。
              </Paragraph>
            </ScrollView>
          )}
          
          {currentStep === 1 && (
            <View>
              <Title style={styles.sectionTitle}>腹诊</Title>
              <Paragraph style={styles.instruction}>
                腹诊是中医切诊的重要组成部分，通过对腹部的按压检查，了解脏腑功能状态和病变情况。
              </Paragraph>
              
              <View style={styles.abdominalImageContainer}>
                <View style={styles.abdominalImagePlaceholder}>
                  <Icon name="stomach" size={80} color={theme.colors.primary} />
                  <Text style={styles.abdominalImageText}>腹诊示意图</Text>
                </View>
              </View>
              
              <Paragraph style={styles.noteText}>
                由于腹诊需要专业人员进行，此处仅做展示，实际操作请咨询专业中医师。
              </Paragraph>
            </View>
          )}
          
          {currentStep === 2 && (
            <View>
              <Title style={styles.sectionTitle}>切诊分析结果</Title>
              
              {Object.values(pulseData).some(data => data.characteristic !== '') ? (
                <List.Section>
                  <List.Item
                    title="脉象分析"
                    description="以下是基于您的脉象信息的初步分析"
                    left={props => <List.Icon {...props} icon="heart-pulse" />}
                  />
                  <Divider style={styles.divider} />
                  
                  <List.Item
                    title="体质判断"
                    description={getAnalysisResult().constitution}
                    left={props => <List.Icon {...props} icon="account-cog" />}
                  />
                  
                  <List.Item
                    title="调理建议"
                    description={getAnalysisResult().recommendation}
                    left={props => <List.Icon {...props} icon="medical-bag" />}
                  />
                  
                  <Chip icon="information" style={styles.chip}>
                    切诊结果应结合望、闻、问三诊共同分析，形成完整诊断。
                  </Chip>
                  
                  {apiError ? (
                    <Chip icon="alert" style={styles.errorChip}>
                      {apiError}
                    </Chip>
                  ) : null}
                </List.Section>
              ) : (
                <Paragraph style={styles.warningText}>
                  未录入足够的脉象信息，无法提供分析结果。请返回脉诊步骤录入数据。
                </Paragraph>
              )}
            </View>
          )}
        </Card.Content>
        <Card.Actions style={styles.cardActions}>
          <Button 
            mode="outlined" 
            onPress={handlePrevious}
            icon="arrow-left"
          >
            {currentStep === 0 ? '取消' : '上一步'}
          </Button>
          <Button 
            mode="contained" 
            onPress={handleNext}
            icon={currentStep === steps.length - 1 ? "check" : "arrow-right"}
            disabled={!isStepComplete() || isLoading}
            loading={isLoading}
          >
            {currentStep === steps.length - 1 ? '完成' : '下一步'}
          </Button>
        </Card.Actions>
      </Card>
    );
  };
  
  // 渲染进度指示器
  const renderProgress = () => {
    return (
      <View style={styles.progressContainer}>
        {steps.map((step, index) => (
          <React.Fragment key={index}>
            <View 
              style={[
                styles.progressStep, 
                { 
                  backgroundColor: index <= currentStep 
                    ? theme.colors.primary 
                    : theme.colors.backdrop 
                }
              ]}
            >
              <Text style={styles.progressStepText}>{index + 1}</Text>
            </View>
            {index < steps.length - 1 && (
              <View 
                style={[
                  styles.progressLine, 
                  { 
                    backgroundColor: index < currentStep 
                      ? theme.colors.primary 
                      : theme.colors.backdrop 
                  }
                ]} 
              />
            )}
          </React.Fragment>
        ))}
      </View>
    );
  };
  
  return (
    <ScrollView style={styles.container}>
      <Title style={styles.mainTitle}>切诊</Title>
      <Paragraph style={styles.description}>
        切诊是中医四诊之一，包括脉诊和按压诊断，通过触摸和按压了解人体内脏的状态和疾病的变化。
      </Paragraph>
      
      {renderProgress()}
      {renderStepContent()}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 16
  },
  mainTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 8
  },
  description: {
    marginBottom: 24
  },
  progressContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 24
  },
  progressStep: {
    width: 30,
    height: 30,
    borderRadius: 15,
    alignItems: 'center',
    justifyContent: 'center'
  },
  progressStepText: {
    color: 'white',
    fontWeight: 'bold'
  },
  progressLine: {
    flex: 1,
    height: 3,
    marginHorizontal: 8
  },
  stepCard: {
    marginBottom: 24
  },
  cardContent: {
    padding: 16
  },
  cardActions: {
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingBottom: 16
  },
  sectionTitle: {
    fontSize: 18,
    marginBottom: 8
  },
  subsectionTitle: {
    fontSize: 16,
    marginTop: 16,
    marginBottom: 8
  },
  instruction: {
    marginBottom: 16
  },
  pulseImageContainer: {
    alignItems: 'center',
    marginVertical: 16
  },
  pulseImage: {
    width: '100%',
    height: 150
  },
  pulseImagePlaceholder: {
    width: '100%',
    height: 150,
    backgroundColor: '#f5f5f5',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  pulseImageText: {
    marginTop: 10,
    fontSize: 16,
    color: '#35bb78',
    fontWeight: '600',
  },
  abdominalImageContainer: {
    alignItems: 'center',
    marginVertical: 16
  },
  abdominalImage: {
    width: '100%',
    height: 200
  },
  abdominalImagePlaceholder: {
    width: '100%',
    height: 200,
    backgroundColor: '#f5f5f5',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
  },
  abdominalImageText: {
    marginTop: 10,
    fontSize: 16,
    color: '#35bb78',
    fontWeight: '600',
  },
  pulseCard: {
    marginBottom: 16
  },
  sliderLabel: {
    marginBottom: 8
  },
  sliderLabels: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8
  },
  divider: {
    marginVertical: 16
  },
  pulseCharacteristicsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginBottom: 8
  },
  pulseChip: {
    margin: 4
  },
  note: {
    fontStyle: 'italic',
    marginTop: 16,
    opacity: 0.7
  },
  noteText: {
    fontStyle: 'italic',
    fontSize: 14,
    opacity: 0.7,
    marginTop: 16
  },
  warningText: {
    color: 'orange',
    fontStyle: 'italic',
    marginVertical: 8
  },
  chip: {
    marginTop: 16
  },
  errorChip: {
    marginTop: 8,
    backgroundColor: '#ffebee'
  },
  loadingContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 16
  },
  loadingText: {
    marginTop: 8,
    fontSize: 14,
    color: '#666'
  },
  referencesCard: {
    marginVertical: 16
  },
  referenceItemCard: {
    width: 200,
    marginRight: 8
  },
  referenceImage: {
    height: 120
  },
  referenceTitle: {
    fontSize: 14
  }
});

export default PalpationDiagnosis; 
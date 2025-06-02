/**
 * 中医诊断界面
 * 整合舌脉象分析和传感器数据采集功能
 */

import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  Alert,
  ActivityIndicator,
  Dimensions,
  { Modal, } from 'react-native';
import { Camera, CameraType } from 'expo-camera';
import { Audio } from 'expo-av';
import { LinearGradient } from 'expo-linear-gradient';
import { Ionicons, MaterialIcons } from '@expo/vector-icons';

// 类型定义
interface TongueAnalysisResult {
  color: string;
  coating: string;
  texture: string;
  moisture: number;
  thickness: number;
  color_confidence: number;
  coating_confidence: number;
  abnormal_areas: string[];
  timestamp: string;
}

interface PulseAnalysisResult {
  pulse_type: string;
  rate: number;
  rhythm: string;
  strength: number;
  depth: number;
  width: number;
  confidence: number;
  waveform_features: Record<string, any>;
  timestamp: string;
}

interface DiagnosisResult {
  tongue_analysis: TongueAnalysisResult;
  pulse_analysis: PulseAnalysisResult;
  syndrome_classification: {
    primary_syndrome: string;
    primary_score: number;
    secondary_syndromes: Array<{
      syndrome: string;
      score: number;
    }>;
  };
  recommendations: Array<{
    type: string;
    content: string;
    priority: number;
  }>;
  timestamp: string;
}

const { width, height } = Dimensions.get('window');

const TCMDiagnosisScreen: React.FC = () => {
  // 状态管理
  const [currentStep, setCurrentStep] = useState<'tongue' | 'pulse' | 'result'>('tongue');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [tongueImage, setTongueImage] = useState<string | null>(null);
  const [pulseData, setPulseData] = useState<number[] | null>(null);
  const [diagnosisResult, setDiagnosisResult] = useState<DiagnosisResult | null>(null);
  const [cameraPermission, setCameraPermission] = useState<boolean | null>(null);
  const [showCamera, setShowCamera] = useState(false);
  const [isRecordingPulse, setIsRecordingPulse] = useState(false);
  const [pulseRecordingTime, setPulseRecordingTime] = useState(0);
  const [sensorConnected, setSensorConnected] = useState(false);

  const cameraRef = useRef<Camera>(null);
  const pulseTimerRef = useRef<NodeJS.Timeout | null>(null);

  // 权限检查
  useEffect(() => {
    checkCameraPermission();
  }, []);

  const checkCameraPermission = async () => {
    const { status } = await Camera.requestCameraPermissionsAsync();
    setCameraPermission(status === 'granted');
  };

  // 拍摄舌象照片
  const takeTonguePhoto = async () => {
    if (cameraRef.current) {
      try {
        const photo = await cameraRef.current.takePictureAsync({
          quality: 0.8,
          base64: true,
        });
        setTongueImage(photo.uri);
        setShowCamera(false);
        
        // 分析舌象
        await analyzeTongueImage(photo.base64!);
      } catch (error) {
        console.error('拍照失败:', error);
        Alert.alert('错误', '拍照失败，请重试');
      }
    }
  };

  // 分析舌象图像
  const analyzeTongueImage = async (base64Image: string) => {
    setIsAnalyzing(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/diagnosis/tongue-analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          image_data: base64Image,
          image_format: 'base64',
        }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('舌象分析结果:', result);
        // 这里可以保存结果到状态
      } else {
        throw new Error('舌象分析失败');
      }
    } catch (error) {
      console.error('舌象分析错误:', error);
      Alert.alert('错误', '舌象分析失败，请重试');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // 开始脉象采集
  const startPulseRecording = async () => {
    try {
      // 检查传感器连接
      const sensorResponse = await fetch('http://localhost:8001/api/v1/sensors');
      const sensors = await sensorResponse.json();
      
      if (sensors.length === 0) {
        Alert.alert('提示', '请先连接脉象传感器');
        return;
      }

      setIsRecordingPulse(true);
      setPulseRecordingTime(0);
      
      // 启动数据流
      const streamResponse = await fetch('http://localhost:8001/api/v1/data-stream/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sensors: [sensors[0].device_id],
          duration: 30, // 30秒采集
          buffer_size: 1000,
          quality_filter: true,
        }),
      });

      if (streamResponse.ok) {
        const streamResult = await streamResponse.json();
        
        // 开始计时器
        pulseTimerRef.current = setInterval(() => {
          setPulseRecordingTime(prev => {
            if (prev >= 30) {
              stopPulseRecording();
              return 30;
            }
            return prev + 1;
          });
        }, 1000);
        
        // 30秒后自动停止
        setTimeout(() => {
          stopPulseRecording();
        }, 30000);
      }
    } catch (error) {
      console.error('脉象采集启动失败:', error);
      Alert.alert('错误', '脉象采集启动失败');
      setIsRecordingPulse(false);
    }
  };

  // 停止脉象采集
  const stopPulseRecording = async () => {
    setIsRecordingPulse(false);
    if (pulseTimerRef.current) {
      clearInterval(pulseTimerRef.current);
      pulseTimerRef.current = null;
    }
    
    // 这里应该获取采集到的脉象数据并进行分析
    // 模拟脉象数据
    const mockPulseData = Array.from({ length: 30000 }, (_, i) => 
      Math.sin(2 * Math.PI * 1.25 * i / 1000) + 0.1 * Math.random()
    );
    setPulseData(mockPulseData);
    
    await analyzePulseData(mockPulseData);
  };

  // 分析脉象数据
  const analyzePulseData = async (waveformData: number[]) => {
    setIsAnalyzing(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/diagnosis/pulse-analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          waveform_data: waveformData,
          duration: 30.0,
          sampling_rate: 1000,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        console.log('脉象分析结果:', result);
      } else {
        throw new Error('脉象分析失败');
      }
    } catch (error) {
      console.error('脉象分析错误:', error);
      Alert.alert('错误', '脉象分析失败，请重试');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // 综合诊断
  const performComprehensiveDiagnosis = async () => {
    if (!tongueImage || !pulseData) {
      Alert.alert('提示', '请先完成舌象拍摄和脉象采集');
      return;
    }

    setIsAnalyzing(true);
    try {
      const response = await fetch('http://localhost:8000/api/v1/diagnosis/comprehensive', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tongue_image: tongueImage,
          pulse_waveform: pulseData,
          pulse_duration: 30.0,
          symptoms: [], // 可以添加症状输入
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setDiagnosisResult(result);
        setCurrentStep('result');
      } else {
        throw new Error('综合诊断失败');
      }
    } catch (error) {
      console.error('综合诊断错误:', error);
      Alert.alert('错误', '综合诊断失败，请重试');
    } finally {
      setIsAnalyzing(false);
    }
  };

  // 渲染舌象采集界面
  const renderTongueCapture = () => (
    <View style={styles.stepContainer}>
      <Text style={styles.stepTitle}>舌象采集</Text>
      <Text style={styles.stepDescription}>
        请将舌头自然伸出，保持良好的光线条件
      </Text>
      
      {tongueImage ? (
        <View style={styles.imageContainer}>
          <Image source={{ uri: tongueImage }} style={styles.tongueImage} />
          <TouchableOpacity
            style={styles.retakeButton}
            onPress={() => setShowCamera(true)}
          >
            <Ionicons name="camera" size={20} color="#fff" />
            <Text style={styles.retakeButtonText}>重新拍摄</Text>
          </TouchableOpacity>
        </View>
      ) : (
        <TouchableOpacity
          style={styles.captureButton}
          onPress={() => setShowCamera(true)}
        >
          <Ionicons name="camera" size={40} color="#fff" />
          <Text style={styles.captureButtonText}>拍摄舌象</Text>
        </TouchableOpacity>
      )}

      {tongueImage && (
        <TouchableOpacity
          style={styles.nextButton}
          onPress={() => setCurrentStep('pulse')}
        >
          <Text style={styles.nextButtonText}>下一步：脉象采集</Text>
        </TouchableOpacity>
      )}
    </View>
  );

  // 渲染脉象采集界面
  const renderPulseCapture = () => (
    <View style={styles.stepContainer}>
      <Text style={styles.stepTitle}>脉象采集</Text>
      <Text style={styles.stepDescription}>
        请将手腕放在传感器上，保持放松状态
      </Text>
      
      <View style={styles.pulseContainer}>
        {isRecordingPulse ? (
          <View style={styles.recordingContainer}>
            <View style={styles.pulseWave}>
              <Text style={styles.recordingText}>正在采集脉象...</Text>
              <Text style={styles.timerText}>{pulseRecordingTime}/30 秒</Text>
            </View>
            <TouchableOpacity
              style={styles.stopButton}
              onPress={stopPulseRecording}
            >
              <MaterialIcons name="stop" size={30} color="#fff" />
            </TouchableOpacity>
          </View>
        ) : pulseData ? (
          <View style={styles.pulseResultContainer}>
            <Ionicons name="pulse" size={60} color="#4CAF50" />
            <Text style={styles.pulseCompleteText}>脉象采集完成</Text>
            <TouchableOpacity
              style={styles.retakeButton}
              onPress={startPulseRecording}
            >
              <MaterialIcons name="refresh" size={20} color="#fff" />
              <Text style={styles.retakeButtonText}>重新采集</Text>
            </TouchableOpacity>
          </View>
        ) : (
          <TouchableOpacity
            style={styles.startPulseButton}
            onPress={startPulseRecording}
          >
            <Ionicons name="pulse" size={40} color="#fff" />
            <Text style={styles.startPulseButtonText}>开始脉象采集</Text>
          </TouchableOpacity>
        )}
      </View>

      {pulseData && (
        <TouchableOpacity
          style={styles.diagnoseButton}
          onPress={performComprehensiveDiagnosis}
          disabled={isAnalyzing}
        >
          {isAnalyzing ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.diagnoseButtonText}>开始综合诊断</Text>
          )}
        </TouchableOpacity>
      )}
    </View>
  );

  // 渲染诊断结果界面
  const renderDiagnosisResult = () => {
    if (!diagnosisResult) return null;

    return (
      <ScrollView style={styles.resultContainer}>
        <Text style={styles.resultTitle}>诊断结果</Text>
        
        {/* 舌诊结果 */}
        <View style={styles.resultSection}>
          <Text style={styles.sectionTitle}>舌诊分析</Text>
          <View style={styles.resultItem}>
            <Text style={styles.resultLabel}>舌色：</Text>
            <Text style={styles.resultValue}>{diagnosisResult.tongue_analysis.color}</Text>
          </View>
          <View style={styles.resultItem}>
            <Text style={styles.resultLabel}>舌苔：</Text>
            <Text style={styles.resultValue}>{diagnosisResult.tongue_analysis.coating}</Text>
          </View>
          <View style={styles.resultItem}>
            <Text style={styles.resultLabel}>置信度：</Text>
            <Text style={styles.resultValue}>
              {(diagnosisResult.tongue_analysis.color_confidence * 100).toFixed(1)}%
            </Text>
          </View>
        </View>

        {/* 脉诊结果 */}
        <View style={styles.resultSection}>
          <Text style={styles.sectionTitle}>脉诊分析</Text>
          <View style={styles.resultItem}>
            <Text style={styles.resultLabel}>脉型：</Text>
            <Text style={styles.resultValue}>{diagnosisResult.pulse_analysis.pulse_type}</Text>
          </View>
          <View style={styles.resultItem}>
            <Text style={styles.resultLabel}>脉率：</Text>
            <Text style={styles.resultValue}>{diagnosisResult.pulse_analysis.rate} 次/分</Text>
          </View>
          <View style={styles.resultItem}>
            <Text style={styles.resultLabel}>置信度：</Text>
            <Text style={styles.resultValue}>
              {(diagnosisResult.pulse_analysis.confidence * 100).toFixed(1)}%
            </Text>
          </View>
        </View>

        {/* 证候分类 */}
        <View style={styles.resultSection}>
          <Text style={styles.sectionTitle}>证候分类</Text>
          <View style={styles.syndromeContainer}>
            <Text style={styles.primarySyndrome}>
              {diagnosisResult.syndrome_classification.primary_syndrome}
            </Text>
            <Text style={styles.syndromeScore}>
              匹配度：{(diagnosisResult.syndrome_classification.primary_score * 100).toFixed(1)}%
            </Text>
          </View>
        </View>

        {/* 治疗建议 */}
        <View style={styles.resultSection}>
          <Text style={styles.sectionTitle}>治疗建议</Text>
          {diagnosisResult.recommendations.map((rec, index) => (
            <View key={index} style={styles.recommendationItem}>
              <Text style={styles.recommendationType}>{rec.type}</Text>
              <Text style={styles.recommendationContent}>{rec.content}</Text>
            </View>
          ))}
        </View>

        <TouchableOpacity
          style={styles.newDiagnosisButton}
          onPress={() => {
            setCurrentStep('tongue');
            setTongueImage(null);
            setPulseData(null);
            setDiagnosisResult(null);
          }}
        >
          <Text style={styles.newDiagnosisButtonText}>新的诊断</Text>
        </TouchableOpacity>
      </ScrollView>
    );
  };

  // 相机模态框
  const renderCameraModal = () => (
    <Modal visible={showCamera} animationType="slide">
      <View style={styles.cameraContainer}>
        {cameraPermission ? (
          <Camera
            ref={cameraRef}
            style={styles.camera}
            type={CameraType.back}
            flashMode="off"
          >
            <View style={styles.cameraOverlay}>
              <TouchableOpacity
                style={styles.closeButton}
                onPress={() => setShowCamera(false)}
              >
                <Ionicons name="close" size={30} color="#fff" />
              </TouchableOpacity>
              
              <View style={styles.tongueGuide}>
                <Text style={styles.guideText}>请将舌头放在圆圈内</Text>
              </View>
              
              <TouchableOpacity
                style={styles.shutterButton}
                onPress={takeTonguePhoto}
              >
                <View style={styles.shutterInner} />
              </TouchableOpacity>
            </View>
          </Camera>
        ) : (
          <View style={styles.permissionContainer}>
            <Text style={styles.permissionText}>需要相机权限才能拍摄舌象</Text>
            <TouchableOpacity
              style={styles.permissionButton}
              onPress={checkCameraPermission}
            >
              <Text style={styles.permissionButtonText}>授权相机</Text>
            </TouchableOpacity>
          </View>
        )}
      </View>
    </Modal>
  );

  return (
    <LinearGradient
      colors={['#667eea', '#764ba2']}
      style={styles.container}
    >
      <View style={styles.header}>
        <Text style={styles.headerTitle}>中医智能诊断</Text>
        <View style={styles.stepIndicator}>
          <View style={[styles.step, currentStep === 'tongue' && styles.activeStep]}>
            <Text style={styles.stepText}>舌诊</Text>
          </View>
          <View style={[styles.step, currentStep === 'pulse' && styles.activeStep]}>
            <Text style={styles.stepText}>脉诊</Text>
          </View>
          <View style={[styles.step, currentStep === 'result' && styles.activeStep]}>
            <Text style={styles.stepText}>结果</Text>
          </View>
        </View>
      </View>

      <View style={styles.content}>
        {currentStep === 'tongue' && renderTongueCapture()}
        {currentStep === 'pulse' && renderPulseCapture()}
        {currentStep === 'result' && renderDiagnosisResult()}
      </View>

      {renderCameraModal()}
    </LinearGradient>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    paddingTop: 50,
    paddingHorizontal: 20,
    paddingBottom: 20,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    textAlign: 'center',
    marginBottom: 20,
  },
  stepIndicator: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  step: {
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 20,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
  },
  activeStep: {
    backgroundColor: 'rgba(255, 255, 255, 0.8)',
  },
  stepText: {
    color: '#fff',
    fontWeight: '600',
  },
  content: {
    flex: 1,
    backgroundColor: '#fff',
    borderTopLeftRadius: 30,
    borderTopRightRadius: 30,
    paddingTop: 30,
  },
  stepContainer: {
    flex: 1,
    paddingHorizontal: 20,
    alignItems: 'center',
  },
  stepTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 10,
  },
  stepDescription: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginBottom: 30,
  },
  imageContainer: {
    alignItems: 'center',
    marginBottom: 30,
  },
  tongueImage: {
    width: 200,
    height: 200,
    borderRadius: 100,
    marginBottom: 15,
  },
  captureButton: {
    width: 200,
    height: 200,
    borderRadius: 100,
    backgroundColor: '#667eea',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 30,
  },
  captureButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginTop: 10,
  },
  retakeButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FF9800',
    paddingHorizontal: 15,
    paddingVertical: 8,
    borderRadius: 20,
  },
  retakeButtonText: {
    color: '#fff',
    marginLeft: 5,
    fontWeight: '600',
  },
  nextButton: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 25,
  },
  nextButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  pulseContainer: {
    alignItems: 'center',
    marginBottom: 30,
  },
  recordingContainer: {
    alignItems: 'center',
  },
  pulseWave: {
    alignItems: 'center',
    marginBottom: 20,
  },
  recordingText: {
    fontSize: 18,
    color: '#333',
    marginBottom: 10,
  },
  timerText: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#667eea',
  },
  stopButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#F44336',
    justifyContent: 'center',
    alignItems: 'center',
  },
  pulseResultContainer: {
    alignItems: 'center',
  },
  pulseCompleteText: {
    fontSize: 18,
    color: '#4CAF50',
    marginTop: 10,
    marginBottom: 15,
  },
  startPulseButton: {
    width: 200,
    height: 200,
    borderRadius: 100,
    backgroundColor: '#667eea',
    justifyContent: 'center',
    alignItems: 'center',
  },
  startPulseButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    marginTop: 10,
  },
  diagnoseButton: {
    backgroundColor: '#4CAF50',
    paddingHorizontal: 30,
    paddingVertical: 15,
    borderRadius: 25,
  },
  diagnoseButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
  resultContainer: {
    flex: 1,
    paddingHorizontal: 20,
  },
  resultTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#333',
    textAlign: 'center',
    marginBottom: 30,
  },
  resultSection: {
    backgroundColor: '#f8f9fa',
    borderRadius: 15,
    padding: 20,
    marginBottom: 20,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#333',
    marginBottom: 15,
  },
  resultItem: {
    flexDirection: 'row',
    marginBottom: 10,
  },
  resultLabel: {
    fontSize: 16,
    color: '#666',
    width: 80,
  },
  resultValue: {
    fontSize: 16,
    color: '#333',
    fontWeight: '600',
    flex: 1,
  },
  syndromeContainer: {
    alignItems: 'center',
  },
  primarySyndrome: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#667eea',
    marginBottom: 5,
  },
  syndromeScore: {
    fontSize: 14,
    color: '#666',
  },
  recommendationItem: {
    marginBottom: 15,
  },
  recommendationType: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#667eea',
    marginBottom: 5,
  },
  recommendationContent: {
    fontSize: 14,
    color: '#333',
    lineHeight: 20,
  },
  newDiagnosisButton: {
    backgroundColor: '#667eea',
    paddingVertical: 15,
    borderRadius: 25,
    marginTop: 20,
    marginBottom: 30,
  },
  newDiagnosisButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
    textAlign: 'center',
  },
  cameraContainer: {
    flex: 1,
  },
  camera: {
    flex: 1,
  },
  cameraOverlay: {
    flex: 1,
    backgroundColor: 'transparent',
    justifyContent: 'space-between',
    paddingVertical: 50,
    paddingHorizontal: 20,
  },
  closeButton: {
    alignSelf: 'flex-end',
  },
  tongueGuide: {
    alignItems: 'center',
    flex: 1,
    justifyContent: 'center',
  },
  guideText: {
    color: '#fff',
    fontSize: 16,
    textAlign: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
  },
  shutterButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    justifyContent: 'center',
    alignItems: 'center',
    alignSelf: 'center',
  },
  shutterInner: {
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#fff',
  },
  permissionContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#000',
  },
  permissionText: {
    color: '#fff',
    fontSize: 16,
    textAlign: 'center',
    marginBottom: 20,
  },
  permissionButton: {
    backgroundColor: '#667eea',
    paddingHorizontal: 20,
    paddingVertical: 10,
    borderRadius: 20,
  },
  permissionButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '600',
  },
});

export default TCMDiagnosisScreen; 
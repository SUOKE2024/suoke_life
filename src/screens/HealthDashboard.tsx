import React, { useState } from 'react';
import {
    ActivityIndicator,
    Alert,
    Dimensions,
    ScrollView,
    StyleSheet,
    Text,
    TouchableOpacity,
    View,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

// 导入AI模块
import { AICoordinator } from '../ai';
import type {
    HealthAnalysisRequest,
    HealthAnalysisResult
} from '../ai/types/AITypes';

const { width } = Dimensions.get('window');

interface AgentStatus {
    id: string;
    name: string;
    status: 'idle' | 'working' | 'completed' | 'error';
    message: string;
    avatar: string;
}

const HealthDashboard: React.FC = () => {
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysisResult, setAnalysisResult] = useState<HealthAnalysisResult | null>(null);
    const [agents, setAgents] = useState<AgentStatus[]>([
        { id: 'xiaoai', name: '小艾', status: 'idle', message: '等待健康数据...', avatar: '🤖' },
        { id: 'xiaoke', name: '小克', status: 'idle', message: '准备中医诊断...', avatar: '🏥' },
        { id: 'laoke', name: '老克', status: 'idle', message: '准备西医分析...', avatar: '⚕️' },
        { id: 'soer', name: '索儿', status: 'idle', message: '等待综合建议...', avatar: '🌟' },
    ]);

    const updateAgentStatus = (agentId: string, status: AgentStatus['status'], message: string) => {
        setAgents(prev => prev.map(agent =>
            agent.id === agentId ? { ...agent, status, message } : agent
        ));
    };

    const simulateHealthAnalysis = async () => {
        setIsAnalyzing(true);
        setAnalysisResult(null);

        try {
            // 模拟健康数据
            const healthRequest: HealthAnalysisRequest = {
                symptoms: ['轻微头痛', '疲劳', '睡眠质量差'],
                vitalSigns: {
                    heartRate: 78,
                    bloodPressure: { systolic: 125, diastolic: 82 },
                    temperature: 36.7,
                    respiratoryRate: 18
                },
                lifestyle: {
                    sleepHours: 6,
                    exerciseMinutes: 15,
                    stressLevel: 7
                },
                preferences: {
                    preferredLanguage: 'zh-CN',
                    treatmentPreference: 'integrated'
                }
            };

            // 小艾 - 数据收集和预处理
            updateAgentStatus('xiaoai', 'working', '正在收集和分析健康数据...');
            await new Promise(resolve => setTimeout(resolve, 1500));
            updateAgentStatus('xiaoai', 'completed', '健康数据收集完成，发现压力过大');

            // 小克 - 中医诊断
            updateAgentStatus('xiaoke', 'working', '正在进行中医辨证论治...');
            await new Promise(resolve => setTimeout(resolve, 2000));
            updateAgentStatus('xiaoke', 'completed', '中医诊断：肝郁气滞，心神不宁');

            // 老克 - 西医分析
            updateAgentStatus('laoke', 'working', '正在进行西医临床分析...');
            await new Promise(resolve => setTimeout(resolve, 1800));
            updateAgentStatus('laoke', 'completed', '西医分析：轻度焦虑状态，建议调整作息');

            // 索儿 - 综合建议
            updateAgentStatus('soer', 'working', '正在生成个性化健康方案...');
            await new Promise(resolve => setTimeout(resolve, 2200));

            // 获取AI协调器实例并执行分析
            const coordinator = AICoordinator.getInstance();
            const result = await coordinator.analyzeHealth(healthRequest);

            if (result.success && result.data) {
                setAnalysisResult(result.data);
                updateAgentStatus('soer', 'completed', '个性化健康方案已生成');
            } else {
                throw new Error('分析失败');
            }

        } catch (error) {
            console.error('健康分析失败:', error);
            agents.forEach(agent => {
                if (agent.status === 'working') {
                    updateAgentStatus(agent.id, 'error', '分析失败，请重试');
                }
            });
            Alert.alert('错误', '健康分析失败，请检查网络连接后重试');
        } finally {
            setIsAnalyzing(false);
        }
    };

    const renderAgent = (agent: AgentStatus) => {
        const getStatusColor = () => {
            switch (agent.status) {
                case 'working': return '#FF9800';
                case 'completed': return '#4CAF50';
                case 'error': return '#F44336';
                default: return '#9E9E9E';
            }
        };

        return (
            <View key={agent.id} style={styles.agentCard}>
                <View style={styles.agentHeader}>
                    <Text style={styles.agentAvatar}>{agent.avatar}</Text>
                    <View style={styles.agentInfo}>
                        <Text style={styles.agentName}>{agent.name}</Text>
                        <View style={[styles.statusIndicator, { backgroundColor: getStatusColor() }]} />
                    </View>
                    {agent.status === 'working' && (
                        <ActivityIndicator size="small" color="#FF9800" />
                    )}
                </View>
                <Text style={styles.agentMessage}>{agent.message}</Text>
            </View>
        );
    };

    const renderAnalysisResult = () => {
        if (!analysisResult) return null;

        return (
            <View style={styles.resultContainer}>
                <Text style={styles.resultTitle}>🎯 AI健康分析报告</Text>

                {/* 中医诊断 */}
                {analysisResult.tcmDiagnosis && (
                    <View style={styles.diagnosisCard}>
                        <Text style={styles.diagnosisTitle}>🏥 中医诊断</Text>
                        <Text style={styles.diagnosisText}>
                            证型：{analysisResult.tcmDiagnosis.syndrome}
                        </Text>
                        <Text style={styles.diagnosisText}>
                            病机：{analysisResult.tcmDiagnosis.pathogenesis}
                        </Text>
                    </View>
                )}

                {/* 西医分析 */}
                {analysisResult.westernDiagnosis && (
                    <View style={styles.diagnosisCard}>
                        <Text style={styles.diagnosisTitle}>⚕️ 西医分析</Text>
                        <Text style={styles.diagnosisText}>
                            诊断：{analysisResult.westernDiagnosis.diagnosis}
                        </Text>
                        <Text style={styles.diagnosisText}>
                            风险评估：{analysisResult.westernDiagnosis.riskAssessment}
                        </Text>
                    </View>
                )}

                {/* 健康建议 */}
                <View style={styles.recommendationsCard}>
                    <Text style={styles.diagnosisTitle}>💡 个性化建议</Text>
                    {analysisResult.recommendations.slice(0, 3).map((rec, index) => (
                        <View key={index} style={styles.recommendationItem}>
                            <Text style={styles.recommendationType}>{rec.type}</Text>
                            <Text style={styles.recommendationDesc}>{rec.description}</Text>
                        </View>
                    ))}
                </View>

                {/* 健康评分 */}
                <View style={styles.scoreCard}>
                    <Text style={styles.scoreTitle}>健康评分</Text>
                    <Text style={styles.scoreValue}>{analysisResult.healthScore}/100</Text>
                    <Text style={styles.scoreDesc}>
                        {analysisResult.healthScore >= 80 ? '健康状态良好' :
                            analysisResult.healthScore >= 60 ? '需要关注' : '建议就医'}
                    </Text>
                </View>
            </View>
        );
    };

    return (
        <SafeAreaView style={styles.container}>
            <ScrollView style={styles.scrollView}>
                <View style={styles.header}>
                    <Text style={styles.title}>🌟 索克生活 - AI健康管理</Text>
                    <Text style={styles.subtitle}>四大智能体协同健康分析</Text>
                </View>

                {/* AI智能体状态 */}
                <View style={styles.agentsContainer}>
                    <Text style={styles.sectionTitle}>🤖 AI智能体状态</Text>
                    {agents.map(renderAgent)}
                </View>

                {/* 开始分析按钮 */}
                <TouchableOpacity
                    style={[styles.analyzeButton, isAnalyzing && styles.analyzeButtonDisabled]}
                    onPress={simulateHealthAnalysis}
                    disabled={isAnalyzing}
                >
                    {isAnalyzing ? (
                        <ActivityIndicator color="#fff" />
                    ) : (
                        <Text style={styles.analyzeButtonText}>开始AI健康分析</Text>
                    )}
                </TouchableOpacity>

                {/* 分析结果 */}
                {renderAnalysisResult()}
            </ScrollView>
        </SafeAreaView>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#f8f9fa',
    },
    scrollView: {
        flex: 1,
    },
    header: {
        padding: 20,
        alignItems: 'center',
        backgroundColor: '#fff',
        borderBottomWidth: 1,
        borderBottomColor: '#e0e0e0',
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        color: '#2196F3',
        marginBottom: 8,
    },
    subtitle: {
        fontSize: 16,
        color: '#666',
    },
    agentsContainer: {
        padding: 16,
    },
    sectionTitle: {
        fontSize: 18,
        fontWeight: 'bold',
        marginBottom: 16,
        color: '#333',
    },
    agentCard: {
        backgroundColor: '#fff',
        borderRadius: 12,
        padding: 16,
        marginBottom: 12,
        elevation: 2,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
    },
    agentHeader: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 8,
    },
    agentAvatar: {
        fontSize: 24,
        marginRight: 12,
    },
    agentInfo: {
        flex: 1,
        flexDirection: 'row',
        alignItems: 'center',
    },
    agentName: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#333',
        marginRight: 8,
    },
    statusIndicator: {
        width: 8,
        height: 8,
        borderRadius: 4,
    },
    agentMessage: {
        fontSize: 14,
        color: '#666',
        lineHeight: 20,
    },
    analyzeButton: {
        backgroundColor: '#2196F3',
        margin: 16,
        padding: 16,
        borderRadius: 12,
        alignItems: 'center',
    },
    analyzeButtonDisabled: {
        backgroundColor: '#ccc',
    },
    analyzeButtonText: {
        color: '#fff',
        fontSize: 16,
        fontWeight: 'bold',
    },
    resultContainer: {
        padding: 16,
    },
    resultTitle: {
        fontSize: 20,
        fontWeight: 'bold',
        marginBottom: 16,
        color: '#333',
    },
    diagnosisCard: {
        backgroundColor: '#fff',
        borderRadius: 12,
        padding: 16,
        marginBottom: 12,
        elevation: 2,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
    },
    diagnosisTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        marginBottom: 8,
        color: '#333',
    },
    diagnosisText: {
        fontSize: 14,
        color: '#666',
        marginBottom: 4,
    },
    recommendationsCard: {
        backgroundColor: '#fff',
        borderRadius: 12,
        padding: 16,
        marginBottom: 12,
        elevation: 2,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
    },
    recommendationItem: {
        marginBottom: 12,
    },
    recommendationType: {
        fontSize: 14,
        fontWeight: 'bold',
        color: '#2196F3',
        marginBottom: 4,
    },
    recommendationDesc: {
        fontSize: 14,
        color: '#666',
        lineHeight: 20,
    },
    scoreCard: {
        backgroundColor: '#fff',
        borderRadius: 12,
        padding: 16,
        alignItems: 'center',
        elevation: 2,
        shadowColor: '#000',
        shadowOffset: { width: 0, height: 2 },
        shadowOpacity: 0.1,
        shadowRadius: 4,
    },
    scoreTitle: {
        fontSize: 16,
        fontWeight: 'bold',
        color: '#333',
        marginBottom: 8,
    },
    scoreValue: {
        fontSize: 36,
        fontWeight: 'bold',
        color: '#4CAF50',
        marginBottom: 4,
    },
    scoreDesc: {
        fontSize: 14,
        color: '#666',
    },
});

export default HealthDashboard; 
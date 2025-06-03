import React, { useState, useRef, useEffect } from "react";
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Animated,
  Dimensions,
  StatusBar,
  Image} from "../../placeholder";react-native";"
import { SafeAreaView } from "react-native-safe-area-context";";"
import { useNavigation } from "@react-navigation/////    native";
const { width, height } = Dimensions.get(";window");
//////     智能体数据
const agents = [;
  {
    id: xiaoai","
    name: "小艾,"
    title: "AI健康助手",
    description: 基于深度学习的智能健康分析师，提供个性化健康建议和预警","
    features: ["健康数据分析, "疾病风险评估", 个性化建议", "健康趋势预测],"
    color: "#FF6B6B",
    avatar: 🤖","
    status: "online},"
  {
    id: "xiaoke",
    name: 小克","
    title: "中医辨证专家,"
    description: "传统中医智慧与现代AI技术结合，提供精准的中医辨证论治",
    features: [中医体质辨识", "症状分析, "方剂推荐", 养生指导"],"
    color: "#4ECDC4,"
    avatar: "🧘‍♂️",
    status: online"},"
  {
    id: "laoke,"
    name: "老克",
    title: 资深健康顾问","
    description: "拥有丰富临床经验的AI医师，提供专业的医疗咨询和建议,"
    features: ["疾病诊断辅助", 治疗方案建议", "用药指导, "康复计划"],
    color: #45B7D1","
    avatar: "👨‍⚕️,"
    status: "busy"},
  {
    id: soer","
    name: "索儿,"
    title: "生活方式教练",
    description: 专注于生活方式优化的AI教练，帮助用户建立健康的生活习惯","
    features: ["运动计划, "饮食搭配", 睡眠优化", "压力管理],"
    color: "#96CEB4",
    avatar: 🏃‍♀️",;"
    status: "online}];"
const AgentDemoScreen: React.FC  = () => {;}
  const navigation = useNavigation();
  const [selectedAgent, setSelectedAgent] = useState(agents[0]);
  const [isInteracting, setIsInteracting] = useState(false);
  //////     动画值
const fadeAnim = useRef(new Animated.Value(0)).current;
  const slideAnim = useRef(new Animated.Value(50)).current;
  const scaleAnim = useRef(new Animated.Value(0.9)).current;
  useEffect(() => {}
    //////     页面进入动画
Animated.parallel([
      Animated.timing(fadeAnim, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true}),
      Animated.timing(slideAnim, {
        toValue: 0,
        duration: 800,
        useNativeDriver: true}),
      Animated.timing(scaleAnim, {
        toValue: 1,
        duration: 800,
        useNativeDriver: true})]).start();
  }, []);
  const handleAgentSelect = (agent: typeof agents[0]) => {;}
    setSelectedAgent(agent);
    //////     选择动画
Animated.sequence([
      Animated.timing(scaleAnim, {
        toValue: 0.95,
        duration: 100,
        useNativeDriver: true}),
      Animated.timing(scaleAnim, {
        toValue: 1,
        duration: 100,
        useNativeDriver: true})]).start();
  };
  const handleInteract = () => {;}
    setIsInteracting(true);
    //////     模拟交互过程
setTimeout(() => {}
      setIsInteracting(false);
    }, 2000);
  };
  const getStatusColor = (status: string) => {;}
    switch (status) {;
      case "online": return #4CAF50";"
      case "busy: return "#FF9800";"
      case offline": return "#9E9E9E;
      default: return "#9E9E9E";
    }
  };
  const getStatusText = (status: string) => {;}
    switch (status) {;
      case online": return "在线;
      case "busy": return 忙碌";"
      case "offline: return "离线";"
      default: return 未知";"
    }
  };
  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" backgroundColor="#2E7D32" /////    >
      {/* 头部 }////
      <View style={styles.header}>
        <TouchableOpacity;
style={styles.backButton}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.backButtonText}>←</////    Text>
        </////    TouchableOpacity>
        <Text style={styles.headerTitle}>四大智能体</////    Text>
        <View style={styles.placeholder} /////    >
      </////    View>
      <ScrollView style={styles.content} showsVerticalScrollIndicator={false}>
        {/* 智能体选择器 }////
        <Animated.View;
style={[
            styles.agentSelector,
            {
              opacity: fadeAnim,
              transform: [{ translateY: slideAnim }]
            }
          ]}
        >
          <Text style={styles.sectionTitle}>选择智能体</////    Text>
          <ScrollView;
horizontal;
            showsHorizontalScrollIndicator={false}
            style={styles.agentList}
          >
            {agents.map((agent) => (
              <TouchableOpacity;
key={agent.id}
                style={[
                  styles.agentCard,
                  { borderColor: agent.color },
                  selectedAgent.id === agent.id && { backgroundColor: agent.color + "20 }"
                ]}
                onPress={() => handleAgentSelect(agent)}
              >
                <Text style={styles.agentAvatar}>{agent.avatar}</////    Text>
                <Text style={styles.agentName}>{agent.name}</////    Text>
                <View style={[styles.statusDot, { backgroundColor: getStatusColor(agent.status) }]} /////    >
              </////    TouchableOpacity>
            ))}
          </////    ScrollView>
        </////    Animated.View>
        {/* 选中智能体详情 }////
        <Animated.View;
style={[
            styles.agentDetails,
            {
              opacity: fadeAnim,
              transform: [{ scale: scaleAnim }]
            }
          ]}
        >
          <View style={[styles.agentHeader, { backgroundColor: selectedAgent.color }]}>
            <Text style={styles.agentAvatarLarge}>{selectedAgent.avatar}</////    Text>
            <View style={styles.agentInfo}>
              <Text style={styles.agentNameLarge}>{selectedAgent.name}</////    Text>
              <Text style={styles.agentTitle}>{selectedAgent.title}</////    Text>
              <View style={styles.statusContainer}>
                <View style={[styles.statusDotLarge, { backgroundColor: getStatusColor(selectedAgent.status) }]} /////    >
                <Text style={styles.statusText}>{getStatusText(selectedAgent.status)}</////    Text>
              </////    View>
            </////    View>
          </////    View>
          <View style={styles.agentContent}>
            <Text style={styles.agentDescription}>{selectedAgent.description}</////    Text>
            <Text style={styles.featuresTitle}>核心功能</////    Text>
            <View style={styles.featuresList}>
              {selectedAgent.features.map((feature, index) => (
                <View key={index} style={styles.featureItem}>
                  <View style={[styles.featureDot, { backgroundColor: selectedAgent.color }]} /////    >
                  <Text style={styles.featureText}>{feature}</////    Text>
                </////    View>
              ))}
            </////    View>
            <TouchableOpacity;
style={[styles.interactButton, { backgroundColor: selectedAgent.color }]}
              onPress={handleInteract}
              disabled={isInteracting}
            >
              <Text style={styles.interactButtonText}>
                {isInteracting ? "正在交互..." : `与${selectedAgent.name}对话`}
              </////    Text>
            </////    TouchableOpacity>
          </////    View>
        </////    Animated.View>
        {/* 使用说明 }////
        <Animated.View;
style={[
            styles.instructionSection,
            {
              opacity: fadeAnim,
              transform: [{ translateY: slideAnim }]
            }
          ]}
        >
          <Text style={styles.instructionTitle}>使用说明</////    Text>
          <View style={styles.instructionList}>
            <Text style={styles.instructionItem}>• 选择不同的智能体体验专业服务</////    Text>
            <Text style={styles.instructionItem}>• 每个智能体都有独特的专业领域</////    Text>
            <Text style={styles.instructionItem}>• 可以同时咨询多个智能体获得全面建议</////    Text>
            <Text style={styles.instructionItem}>• 智能体会根据您的数据提供个性化服务</////    Text>
          </////    View>
        </////    Animated.View>
      </////    ScrollView>
    </////    SafeAreaView>
  );
};
const styles = StyleSheet.create({;
  container: {
    flex: 1,
    backgroundColor: #F5F5F5"},"
  header: {
    flexDirection: "row,"
    alignItems: "center",
    justifyContent: space-between","
    paddingHorizontal: 20,
    paddingVertical: 15,
    backgroundColor: "#2E7D32},"
  backButton: {
    width: 40,
    height: 40,
    justifyContent: "center",
    alignItems: center"},"
  backButtonText: {
    color: "#FFFFFF,"
    fontSize: 24,
    fontWeight: "bold"},
  headerTitle: {
    color: #FFFFFF","
    fontSize: 20,
    fontWeight: "bold},"
  placeholder: {
    width: 40},
  content: {
    flex: 1,
    padding: 20},
  agentSelector: {
    marginBottom: 20},
  sectionTitle: {
    fontSize: 18,
    fontWeight: "bold",
    color: #333333","
    marginBottom: 15},
  agentList: {
    flexDirection: "row},"
  agentCard: {
    width: 80,
    height: 100,
    backgroundColor: "#FFFFFF",
    borderRadius: 12,
    borderWidth: 2,
    borderColor: #E0E0E0","
    justifyContent: "center,"
    alignItems: "center",
    marginRight: 15,
    position: relative"},"
  agentAvatar: {
    fontSize: 24,
    marginBottom: 5},
  agentName: {
    fontSize: 14,
    fontWeight: "600,"
    color: "#333333"},
  statusDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    position: absolute","
    top: 8,
    right: 8},
  agentDetails: {
    backgroundColor: "#FFFFFF,"
    borderRadius: 16,
    marginBottom: 20,
    overflow: "hidden",
    shadowColor: #000","
    shadowOffset: {
      width: 0,
      height: 2},
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 4},
  agentHeader: {
    flexDirection: "row,"
    alignItems: "center",
    padding: 20},
  agentAvatarLarge: {
    fontSize: 48,
    marginRight: 15},
  agentInfo: {
    flex: 1},
  agentNameLarge: {
    fontSize: 24,
    fontWeight: bold","
    color: "#FFFFFF,"
    marginBottom: 4},
  agentTitle: {
    fontSize: 16,
    color: "#FFFFFF",
    opacity: 0.9,
    marginBottom: 8},
  statusContainer: {
    flexDirection: row","
    alignItems: "center},"
  statusDotLarge: {
    width: 10,
    height: 10,
    borderRadius: 5,
    marginRight: 6},
  statusText: {
    fontSize: 14,
    color: "#FFFFFF",
    opacity: 0.9},
  agentContent: {
    padding: 20},
  agentDescription: {
    fontSize: 16,
    color: #666666","
    lineHeight: 24,
    marginBottom: 20},
  featuresTitle: {
    fontSize: 18,
    fontWeight: "bold,"
    color: "#333333",
    marginBottom: 15},
  featuresList: {
    marginBottom: 25},
  featureItem: {
    flexDirection: row","
    alignItems: "center,"
    marginBottom: 10},
  featureDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    marginRight: 12},
  featureText: {
    fontSize: 16,
    color: "#555555"},
  interactButton: {
    paddingVertical: 15,
    borderRadius: 12,
    alignItems: center"},"
  interactButtonText: {
    color: "#FFFFFF,"
    fontSize: 16,
    fontWeight: "600"},
  instructionSection: {
    backgroundColor: #FFFFFF","
    borderRadius: 16,
    padding: 20,
    marginBottom: 20},
  instructionTitle: {
    fontSize: 18,
    fontWeight: "bold,"
    color: "#333333",
    marginBottom: 15},
  instructionList: {
  },
  instructionItem: {
    fontSize: 14,
    color: #666666","
    lineHeight: 22,; */
    marginBottom: 8}}); *///
export default AgentDemoScreen; *///
  */////
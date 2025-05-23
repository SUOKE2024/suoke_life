import React, { useEffect } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl, TouchableOpacity } from 'react-native';
import { Text, Card, Button, Avatar, Title, Paragraph, useTheme, ActivityIndicator, Surface } from 'react-native-paper';
import { useSelector } from 'react-redux';
import { useAppDispatch } from '../../hooks/redux';
import { useTranslation } from 'react-i18next';
import { SafeAreaView } from 'react-native-safe-area-context';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';
import { useNavigation } from '@react-navigation/native';
import { fetchAgents } from '../../store/slices/agentSlice';
import { RootState } from '../../store';

const HomeScreen = () => {
  const theme = useTheme();
  const { t } = useTranslation();
  const dispatch = useAppDispatch();
  const navigation = useNavigation<any>();
  const [refreshing, setRefreshing] = React.useState(false);
  
  const { currentUser } = useSelector((state: RootState) => state.user);
  const { agents, isLoading } = useSelector((state: RootState) => state.agent);
  
  // 加载智能体信息
  useEffect(() => {
    dispatch(fetchAgents());
  }, [dispatch]);
  
  // 下拉刷新
  const onRefresh = React.useCallback(() => {
    setRefreshing(true);
    dispatch(fetchAgents()).then(() => {
      setRefreshing(false);
    });
  }, [dispatch]);

  // 导航到智能体专区
  const navigateToAgents = () => {
    navigation.navigate('AgentSelection');
  };
  
  return (
    <SafeAreaView style={styles.container}>
      <ScrollView
        contentContainerStyle={styles.scrollContent}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
      >
        {/* 欢迎横幅 */}
        <Card style={styles.welcomeCard}>
          <Card.Content style={styles.welcomeCardContent}>
            <View style={styles.welcomeTextContainer}>
              <Title style={styles.welcomeTitle}>
                {t('common.welcome')}
              </Title>
              <Paragraph style={styles.welcomeSubtitle}>
                {currentUser?.username || t('auth.login')}
              </Paragraph>
            </View>
            <Avatar.Image 
              size={60} 
              source={{ uri: currentUser?.avatar || 'https://www.suoke.life/default-avatar.png' }} 
            />
          </Card.Content>
        </Card>
        
        {/* 智能体卡片 */}
        <View style={styles.sectionHeader}>
          <Title style={styles.sectionTitle}>{t('agents.title')}</Title>
          <TouchableOpacity onPress={navigateToAgents}>
            <Text style={styles.viewAllText}>{t('common.view_all')}</Text>
          </TouchableOpacity>
        </View>
        
        {isLoading ? (
          <View style={styles.loadingContainer}>
            <ActivityIndicator animating={true} color={theme.colors.primary} />
            <Text style={styles.loadingText}>{t('common.loading')}</Text>
          </View>
        ) : (
          <View style={styles.agentsContainer}>
            {/* 小艾智能体 */}
            <TouchableOpacity onPress={navigateToAgents}>
              <Surface style={[styles.agentCard, { backgroundColor: theme.colors.primaryContainer }]}>
                <View style={styles.agentIconContainer}>
                  <Icon name="medical-bag" size={32} color={theme.colors.primary} />
                </View>
                <Text style={styles.agentName}>{t('agents.xiaoai')}</Text>
                <Text style={styles.agentDescription}>{t('agents.xiaoai_desc')}</Text>
              </Surface>
            </TouchableOpacity>
            
            {/* 小克智能体 */}
            <TouchableOpacity onPress={navigateToAgents}>
              <Surface style={[styles.agentCard, { backgroundColor: theme.colors.secondaryContainer }]}>
                <View style={styles.agentIconContainer}>
                  <Icon name="food-apple" size={32} color={theme.colors.secondary} />
                </View>
                <Text style={styles.agentName}>{t('agents.xiaoke')}</Text>
                <Text style={styles.agentDescription}>{t('agents.xiaoke_desc')}</Text>
              </Surface>
            </TouchableOpacity>
            
            {/* 老克智能体 */}
            <TouchableOpacity onPress={navigateToAgents}>
              <Surface style={[styles.agentCard, { backgroundColor: '#F0F4F8' }]}>
                <View style={styles.agentIconContainer}>
                  <Icon name="book-open-variant" size={32} color="#324D61" />
                </View>
                <Text style={styles.agentName}>{t('agents.laoke')}</Text>
                <Text style={styles.agentDescription}>{t('agents.laoke_desc')}</Text>
              </Surface>
            </TouchableOpacity>
            
            {/* 索儿智能体 */}
            <TouchableOpacity onPress={navigateToAgents}>
              <Surface style={[styles.agentCard, { backgroundColor: '#FFF3E0' }]}>
                <View style={styles.agentIconContainer}>
                  <Icon name="sprout" size={32} color="#FF9800" />
                </View>
                <Text style={styles.agentName}>{t('agents.soer')}</Text>
                <Text style={styles.agentDescription}>{t('agents.soer_desc')}</Text>
              </Surface>
            </TouchableOpacity>
          </View>
        )}
        
        {/* 智能体协同 */}
        <Card style={styles.collaborationCard} onPress={() => navigation.navigate('AgentCollaboration')}>
          <Card.Content>
            <View style={styles.collaborationContent}>
              <View style={styles.collaborationTextContainer}>
                <Text style={styles.collaborationTitle}>{t('agents.collaboration')}</Text>
                <Text style={styles.collaborationDescription}>
                  {t('agents.collaboration_desc')}
                </Text>
              </View>
              <Icon name="arrow-right-circle" size={36} color={theme.colors.onSurface} />
            </View>
          </Card.Content>
        </Card>
        
        {/* 快速入口区域 */}
        <Title style={styles.sectionTitle}>{t('home.quick_access')}</Title>
        <View style={styles.quickAccessContainer}>
          <Button
            mode="outlined"
            icon="stethoscope"
            style={styles.quickAccessButton}
            contentStyle={styles.quickAccessButtonContent}
            onPress={() => navigation.navigate('XiaoaiFourDiagnosis')}
          >
            {t('diagnosis.title')}
          </Button>
          
          <Button
            mode="outlined"
            icon="chart-line"
            style={styles.quickAccessButton}
            contentStyle={styles.quickAccessButtonContent}
            onPress={() => navigation.navigate('XiaoaiHealthRecords')}
          >
            {t('home.health_data')}
          </Button>
          
          <Button
            mode="outlined"
            icon="calendar-check"
            style={styles.quickAccessButton}
            contentStyle={styles.quickAccessButtonContent}
            onPress={() => navigation.navigate('SoerHealthPlan')}
          >
            {t('home.health_plan')}
          </Button>
          
          <Button
            mode="outlined"
            icon="book-open-page-variant"
            style={styles.quickAccessButton}
            contentStyle={styles.quickAccessButtonContent}
            onPress={() => navigation.navigate('LaokeKnowledge')}
          >
            {t('home.knowledge')}
          </Button>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  scrollContent: {
    padding: 16,
  },
  welcomeCard: {
    marginBottom: 24,
    elevation: 4,
  },
  welcomeCardContent: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  welcomeTextContainer: {
    flex: 1,
  },
  welcomeTitle: {
    fontSize: 22,
    fontWeight: 'bold',
  },
  welcomeSubtitle: {
    fontSize: 16,
    opacity: 0.7,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    marginBottom: 0,
  },
  viewAllText: {
    fontSize: 14,
    color: '#007AFF',
  },
  loadingContainer: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 24,
  },
  loadingText: {
    marginTop: 8,
    fontSize: 14,
    opacity: 0.6,
  },
  agentsContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  agentCard: {
    width: '100%',
    padding: 16,
    marginBottom: 16,
    borderRadius: 12,
    elevation: 2,
  },
  agentIconContainer: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: 'white',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12,
  },
  agentName: {
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  agentDescription: {
    fontSize: 12,
    opacity: 0.7,
  },
  collaborationCard: {
    marginBottom: 24,
  },
  collaborationContent: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
  },
  collaborationTextContainer: {
    flex: 1,
    marginRight: 16,
  },
  collaborationTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  collaborationDescription: {
    fontSize: 14,
    opacity: 0.7,
  },
  quickAccessContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  quickAccessButton: {
    width: '48%',
    marginBottom: 12,
  },
  quickAccessButtonContent: {
    height: 48,
  },
});

export default HomeScreen;
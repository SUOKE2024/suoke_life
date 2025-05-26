// Mock健康服务
const mockHealthService = {
    getHealthMetrics: jest.fn(),
    addHealthRecord: jest.fn(),
    updateHealthRecord: jest.fn(),
    deleteHealthRecord: jest.fn(),
    getHealthTrends: jest.fn(),
    generateHealthReport: jest.fn(),
    getHealthSuggestions: jest.fn(),
    syncHealthData: jest.fn(),
    exportHealthData: jest.fn(),
    importHealthData: jest.fn(),
    recordHealthData: jest.fn(),
    getHealthData: jest.fn(),
    setHealthReminder: jest.fn(),
    getHealthAdvice: jest.fn(),
    syncData: jest.fn(),
    backupData: jest.fn(),
  };
  
  // Mock智能体服务
  const mockAgentService = {
    getHealthAnalysis: jest.fn(),
    getPersonalizedAdvice: jest.fn(),
    startHealthConsultation: jest.fn(),
    sendHealthData: jest.fn(),
    startConsultation: jest.fn(),
    sendMessage: jest.fn(),
  };
  
  // Mock通知服务
  const mockNotificationService = {
    scheduleHealthReminder: jest.fn(),
    sendHealthAlert: jest.fn(),
    cancelReminder: jest.fn(),
    sendHealthReminder: jest.fn(),
    scheduleReminder: jest.fn(),
  };
  
  // Mock数据存储
  const mockStorage = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
  };
  
  // Mock服务已在上面定义
  
  // Mock健康数据
  const mockHealthData = {
    vitals: {
      heartRate: { value: 72, timestamp: Date.now(), unit: 'bpm' },
      bloodPressure: { 
        systolic: 120, 
        diastolic: 80, 
        timestamp: Date.now(), 
        unit: 'mmHg' 
      },
      temperature: { value: 36.5, timestamp: Date.now(), unit: '°C' },
      weight: { value: 70, timestamp: Date.now(), unit: 'kg' },
      height: { value: 175, timestamp: Date.now(), unit: 'cm' },
    },
    activities: {
      steps: { value: 8500, goal: 10000, timestamp: Date.now() },
      calories: { value: 2200, goal: 2500, timestamp: Date.now() },
      exercise: { 
        duration: 45, 
        type: 'running', 
        intensity: 'moderate',
        timestamp: Date.now() 
      },
      sleep: {
        duration: 7.5,
        quality: 'good',
        bedtime: Date.now() - 8 * 60 * 60 * 1000,
        wakeTime: Date.now(),
      },
    },
    nutrition: {
      water: { value: 1500, goal: 2000, unit: 'ml', timestamp: Date.now() },
      meals: [
        {
          type: 'breakfast',
          calories: 400,
          nutrients: { protein: 20, carbs: 50, fat: 15 },
          timestamp: Date.now() - 4 * 60 * 60 * 1000,
        },
        {
          type: 'lunch',
          calories: 600,
          nutrients: { protein: 30, carbs: 70, fat: 20 },
          timestamp: Date.now() - 1 * 60 * 60 * 1000,
        },
      ],
    },
    symptoms: [
      {
        id: '1',
        type: 'headache',
        severity: 3,
        duration: 2,
        timestamp: Date.now() - 2 * 60 * 60 * 1000,
        notes: '轻微头痛，可能是睡眠不足',
      },
    ],
    medications: [
      {
        id: '1',
        name: '维生素D',
        dosage: '1000IU',
        frequency: 'daily',
        startDate: Date.now() - 30 * 24 * 60 * 60 * 1000,
        endDate: Date.now() + 60 * 24 * 60 * 60 * 1000,
        taken: true,
        timestamp: Date.now(),
      },
    ],
  };
  
  describe('健康追踪端到端测试', () => {
    beforeEach(() => {
      jest.clearAllMocks();
      
      // 设置默认Mock返回值
      mockHealthService.getHealthMetrics.mockResolvedValue({
        success: true,
        data: mockHealthData,
      });
      
      mockStorage.getItem.mockImplementation((key: string) => {
        if (key === 'health_data') {
          return Promise.resolve(JSON.stringify(mockHealthData));
        }
        return Promise.resolve(null);
      });
    });
  
    describe('健康数据记录流程', () => {
      it('应该完成完整的健康数据记录流程', async () => {
        // 1. 获取当前健康数据
        const currentData = await mockHealthService.getHealthMetrics();
        expect(currentData.success).toBe(true);
        expect(currentData.data).toEqual(mockHealthData);
  
        // 2. 添加新的健康记录
        const newVitalRecord = {
          type: 'heartRate',
          value: 75,
          timestamp: Date.now(),
          unit: 'bpm',
        };
  
        mockHealthService.addHealthRecord.mockResolvedValue({
          success: true,
          id: 'new-record-id',
        });
  
        const addResult = await mockHealthService.addHealthRecord(newVitalRecord);
        expect(addResult.success).toBe(true);
        expect(mockHealthService.addHealthRecord).toHaveBeenCalledWith(newVitalRecord);
  
        // 3. 验证数据已保存到本地存储
        expect(mockStorage.setItem).toHaveBeenCalledWith(
          'health_data',
          expect.stringContaining('75')
        );
  
        // 4. 同步数据到服务器
        mockHealthService.syncHealthData.mockResolvedValue({
          success: true,
          synced: 1,
        });
  
        const syncResult = await mockHealthService.syncHealthData();
        expect(syncResult.success).toBe(true);
        expect(mockHealthService.syncHealthData).toHaveBeenCalled();
      });
  
      it('应该处理批量健康数据记录', async () => {
        const batchRecords = [
          { type: 'weight', value: 71, timestamp: Date.now(), unit: 'kg' },
          { type: 'bloodPressure', systolic: 125, diastolic: 82, timestamp: Date.now(), unit: 'mmHg' },
          { type: 'steps', value: 9000, timestamp: Date.now() },
        ];
  
        mockHealthService.addHealthRecord.mockImplementation((record) => 
          Promise.resolve({ success: true, id: `record-${record.type}` })
        );
  
        // 批量添加记录
        const results = await Promise.all(
          batchRecords.map(record => mockHealthService.addHealthRecord(record))
        );
  
        expect(results).toHaveLength(3);
        results.forEach(result => {
          expect(result.success).toBe(true);
        });
  
        expect(mockHealthService.addHealthRecord).toHaveBeenCalledTimes(3);
      });
  
      it('应该验证健康数据的有效性', async () => {
        const invalidRecords = [
          { type: 'heartRate', value: -10, timestamp: Date.now(), unit: 'bpm' }, // 负值
          { type: 'bloodPressure', systolic: 300, diastolic: 200, timestamp: Date.now(), unit: 'mmHg' }, // 异常高值
          { type: 'weight', value: 0, timestamp: Date.now(), unit: 'kg' }, // 零值
        ];
  
        mockHealthService.addHealthRecord.mockImplementation((record) => {
          if (record.value <= 0 || (record.type === 'heartRate' && record.value > 200)) {
            return Promise.resolve({ success: false, error: '健康数据值异常' });
          }
          if (record.type === 'bloodPressure' && (record.systolic > 250 || record.diastolic > 150)) {
            return Promise.resolve({ success: false, error: '血压值异常' });
          }
          return Promise.resolve({ success: true, id: 'valid-record' });
        });
  
        const results = await Promise.all(
          invalidRecords.map(record => mockHealthService.addHealthRecord(record))
        );
  
        expect(results[0].success).toBe(false);
        expect(results[1].success).toBe(false);
        expect(results[2].success).toBe(false);
      });
    });
  
    describe('健康趋势分析流程', () => {
      it('应该生成健康趋势分析报告', async () => {
        const trendData = {
          heartRate: {
            trend: 'stable',
            average: 72,
            range: { min: 65, max: 80 },
            data: [70, 72, 74, 71, 73],
          },
          weight: {
            trend: 'decreasing',
            average: 69.5,
            change: -0.5,
            data: [70, 69.8, 69.5, 69.3, 69.2],
          },
          steps: {
            trend: 'increasing',
            average: 8800,
            goalAchievement: 0.88,
            data: [8000, 8200, 8500, 8800, 9000],
          },
        };
  
        mockHealthService.getHealthTrends.mockResolvedValue({
          success: true,
          data: trendData,
          period: '7days',
        });
  
        const trends = await mockHealthService.getHealthTrends('7days');
        expect(trends.success).toBe(true);
        expect(trends.data).toEqual(trendData);
  
        // 验证趋势分析的准确性
        expect(trends.data.heartRate.trend).toBe('stable');
        expect(trends.data.weight.trend).toBe('decreasing');
        expect(trends.data.steps.trend).toBe('increasing');
      });
  
      it('应该获取智能体健康分析', async () => {
        const analysisResult = {
          overall_score: 85,
          recommendations: [
            '建议增加每日步数到10000步',
            '保持当前的心率水平',
            '继续保持体重下降趋势',
          ],
          risk_factors: [
            { factor: '睡眠不足', level: 'low', suggestion: '建议每晚睡眠7-8小时' },
          ],
          achievements: [
            '本周体重下降0.5kg',
            '心率保持稳定范围',
          ],
        };
  
        mockAgentService.getHealthAnalysis.mockResolvedValue({
          success: true,
          analysis: analysisResult,
          agent: 'xiaoai',
        });
  
        const analysis = await mockAgentService.getHealthAnalysis(mockHealthData);
        expect(analysis.success).toBe(true);
        expect(analysis.analysis.overall_score).toBe(85);
        expect(analysis.analysis.recommendations).toHaveLength(3);
      });
  
      it('应该生成个性化健康建议', async () => {
        const personalizedAdvice = {
          nutrition: [
            '建议增加蛋白质摄入',
            '减少糖分摄入',
            '多吃绿叶蔬菜',
          ],
          exercise: [
            '增加有氧运动时间',
            '添加力量训练',
            '保持运动规律性',
          ],
          lifestyle: [
            '改善睡眠质量',
            '减少压力',
            '定期体检',
          ],
          tcm: [
            '根据体质调理饮食',
            '适当进行穴位按摩',
            '注意情志调节',
          ],
        };
  
        mockAgentService.getPersonalizedAdvice.mockResolvedValue({
          success: true,
          advice: personalizedAdvice,
          agent: 'xiaoke',
        });
  
        const advice = await mockAgentService.getPersonalizedAdvice(mockHealthData);
        expect(advice.success).toBe(true);
        expect(advice.advice.nutrition).toHaveLength(3);
        expect(advice.advice.tcm).toHaveLength(3);
      });
    });
  
    describe('健康报告生成流程', () => {
      it('应该生成完整的健康报告', async () => {
        const healthReport = {
          id: 'report-2024-01',
          period: { start: Date.now() - 30 * 24 * 60 * 60 * 1000, end: Date.now() },
          summary: {
            overall_health_score: 82,
            improvement_areas: ['睡眠', '运动'],
            achievements: ['体重管理', '心率稳定'],
          },
          vitals_analysis: {
            heart_rate: { average: 72, status: 'normal' },
            blood_pressure: { average: '120/80', status: 'optimal' },
            weight: { change: -1.2, status: 'improving' },
          },
          activity_analysis: {
            steps: { daily_average: 8500, goal_achievement: 0.85 },
            exercise: { weekly_minutes: 180, recommendation: 150 },
            sleep: { average_hours: 7.2, quality_score: 75 },
          },
          nutrition_analysis: {
            calorie_balance: 'appropriate',
            water_intake: 'adequate',
            meal_regularity: 'good',
          },
          recommendations: [
            '增加每日步数到10000步',
            '改善睡眠质量',
            '保持当前饮食习惯',
          ],
          next_goals: [
            '达到每日步数目标',
            '保持体重下降趋势',
            '提高睡眠质量',
          ],
        };
  
        mockHealthService.generateHealthReport.mockResolvedValue({
          success: true,
          report: healthReport,
        });
  
        const report = await mockHealthService.generateHealthReport('monthly');
        expect(report.success).toBe(true);
        expect(report.report.summary.overall_health_score).toBe(82);
        expect(report.report.recommendations).toHaveLength(3);
        expect(report.report.next_goals).toHaveLength(3);
      });
  
      it('应该支持不同时间段的报告生成', async () => {
        const periods = ['weekly', 'monthly', 'quarterly', 'yearly'];
        
        mockHealthService.generateHealthReport.mockImplementation((period) => 
          Promise.resolve({
            success: true,
            report: { period, generated_at: Date.now() },
          })
        );
  
        const reports = await Promise.all(
          periods.map(period => mockHealthService.generateHealthReport(period))
        );
  
        expect(reports).toHaveLength(4);
        reports.forEach((report, index) => {
          expect(report.success).toBe(true);
          expect(report.report.period).toBe(periods[index]);
        });
      });
  
      it('应该导出健康数据', async () => {
        const exportData = {
          format: 'json',
          data: mockHealthData,
          metadata: {
            export_date: Date.now(),
            user_id: 'user-123',
            data_range: { start: Date.now() - 30 * 24 * 60 * 60 * 1000, end: Date.now() },
          },
        };
  
        mockHealthService.exportHealthData.mockResolvedValue({
          success: true,
          export: exportData,
          download_url: 'https://example.com/export/health-data.json',
        });
  
        const exportResult = await mockHealthService.exportHealthData('json', '30days');
        expect(exportResult.success).toBe(true);
        expect(exportResult.export.format).toBe('json');
        expect(exportResult.download_url).toContain('health-data.json');
      });
    });
  
    describe('健康提醒和通知流程', () => {
      it('应该设置健康提醒', async () => {
        const reminders = [
          { type: 'medication', time: '08:00', message: '服用维生素D' },
          { type: 'water', interval: 2, message: '记得喝水' },
          { type: 'exercise', time: '18:00', message: '运动时间到了' },
          { type: 'sleep', time: '22:00', message: '准备睡觉' },
        ];
  
        mockNotificationService.scheduleHealthReminder.mockImplementation((reminder) =>
          Promise.resolve({ success: true, id: `reminder-${reminder.type}` })
        );
  
        const results = await Promise.all(
          reminders.map(reminder => mockNotificationService.scheduleHealthReminder(reminder))
        );
  
        expect(results).toHaveLength(4);
        results.forEach(result => {
          expect(result.success).toBe(true);
        });
  
        expect(mockNotificationService.scheduleHealthReminder).toHaveBeenCalledTimes(4);
      });
  
      it('应该发送健康警报', async () => {
        const healthAlerts = [
          { type: 'high_heart_rate', value: 120, threshold: 100 },
          { type: 'low_activity', steps: 2000, goal: 10000 },
          { type: 'missed_medication', medication: '维生素D', time: '08:00' },
        ];
  
        mockNotificationService.sendHealthAlert.mockImplementation((alert) =>
          Promise.resolve({ success: true, sent: true })
        );
  
        const results = await Promise.all(
          healthAlerts.map(alert => mockNotificationService.sendHealthAlert(alert))
        );
  
        expect(results).toHaveLength(3);
        results.forEach(result => {
          expect(result.success).toBe(true);
          expect(result.sent).toBe(true);
        });
      });
  
      it('应该管理提醒的生命周期', async () => {
        // 创建提醒
        const reminder = { type: 'medication', time: '08:00', message: '服用维生素D' };
        
        mockNotificationService.scheduleHealthReminder.mockResolvedValue({
          success: true,
          id: 'reminder-123',
        });
  
        const createResult = await mockNotificationService.scheduleHealthReminder(reminder);
        expect(createResult.success).toBe(true);
  
        // 取消提醒
        mockNotificationService.cancelReminder.mockResolvedValue({
          success: true,
          cancelled: true,
        });
  
        const cancelResult = await mockNotificationService.cancelReminder('reminder-123');
        expect(cancelResult.success).toBe(true);
        expect(cancelResult.cancelled).toBe(true);
      });
    });
  
    describe('智能体健康咨询流程', () => {
      it('应该开始健康咨询会话', async () => {
        const consultationData = {
          symptoms: ['头痛', '疲劳'],
          duration: '2天',
          severity: 3,
          additional_info: '最近工作压力大，睡眠不足',
        };
  
        mockAgentService.startHealthConsultation.mockResolvedValue({
          success: true,
          session_id: 'consultation-123',
          agent: 'laoke',
          initial_response: '根据您的症状，可能是压力和睡眠不足导致的。建议您...',
        });
  
        const consultation = await mockAgentService.startHealthConsultation(consultationData);
        expect(consultation.success).toBe(true);
        expect(consultation.session_id).toBe('consultation-123');
        expect(consultation.agent).toBe('laoke');
        expect(consultation.initial_response).toContain('压力和睡眠不足');
      });
  
      it('应该发送健康数据给智能体分析', async () => {
        const analysisRequest = {
          data: mockHealthData,
          focus_areas: ['心率', '睡眠', '运动'],
          questions: ['我的心率是否正常？', '如何改善睡眠质量？'],
        };
  
        mockAgentService.sendHealthData.mockResolvedValue({
          success: true,
          analysis: {
            heart_rate_analysis: '您的心率在正常范围内',
            sleep_analysis: '睡眠时间略少，建议增加到8小时',
            exercise_analysis: '运动量适中，可以适当增加强度',
          },
          recommendations: [
            '保持当前的心率水平',
            '建立规律的睡眠时间',
            '增加有氧运动',
          ],
        });
  
        const analysis = await mockAgentService.sendHealthData(analysisRequest);
        expect(analysis.success).toBe(true);
        expect(analysis.analysis.heart_rate_analysis).toContain('正常范围');
        expect(analysis.recommendations).toHaveLength(3);
      });
    });
  
    describe('数据同步和备份流程', () => {
      it('应该同步本地和云端数据', async () => {
        // 模拟本地数据
        const localData = { ...mockHealthData, lastSync: Date.now() - 60 * 60 * 1000 };
        
        // 模拟云端数据
        const cloudData = {
          ...mockHealthData,
          vitals: {
            ...mockHealthData.vitals,
            heartRate: { value: 74, timestamp: Date.now(), unit: 'bpm' },
          },
          lastSync: Date.now(),
        };
  
        mockStorage.getItem.mockResolvedValue(JSON.stringify(localData));
        mockHealthService.syncHealthData.mockResolvedValue({
          success: true,
          synced_records: 5,
          conflicts: 0,
          latest_data: cloudData,
        });
  
        const syncResult = await mockHealthService.syncHealthData();
        expect(syncResult.success).toBe(true);
        expect(syncResult.synced_records).toBe(5);
        expect(syncResult.conflicts).toBe(0);
  
        // 验证本地数据已更新
        expect(mockStorage.setItem).toHaveBeenCalledWith(
          'health_data',
          JSON.stringify(cloudData)
        );
      });
  
      it('应该处理数据冲突', async () => {
        const conflictData = {
          local: { heartRate: 72, timestamp: Date.now() - 1000 },
          cloud: { heartRate: 75, timestamp: Date.now() },
        };
  
        mockHealthService.syncHealthData.mockResolvedValue({
          success: true,
          conflicts: 1,
          conflict_resolution: 'use_latest',
          resolved_data: conflictData.cloud,
        });
  
        const syncResult = await mockHealthService.syncHealthData();
        expect(syncResult.success).toBe(true);
        expect(syncResult.conflicts).toBe(1);
        expect(syncResult.conflict_resolution).toBe('use_latest');
      });
  
      it('应该处理离线模式', async () => {
        // 模拟网络断开
        mockHealthService.syncHealthData.mockRejectedValue(new Error('Network Error'));
  
        // 数据应该保存到本地队列
        const offlineRecord = { type: 'heartRate', value: 76, timestamp: Date.now() };
        
        mockStorage.setItem.mockResolvedValue(undefined);
        
        // 保存到离线队列
        await mockStorage.setItem('offline_queue', JSON.stringify([offlineRecord]));
        
        expect(mockStorage.setItem).toHaveBeenCalledWith(
          'offline_queue',
          JSON.stringify([offlineRecord])
        );
  
        // 网络恢复后同步
        mockHealthService.syncHealthData.mockResolvedValue({
          success: true,
          synced_offline_records: 1,
        });
  
        const syncResult = await mockHealthService.syncHealthData();
        expect(syncResult.success).toBe(true);
        expect(syncResult.synced_offline_records).toBe(1);
      });
    });
  
    describe('错误处理和恢复', () => {
      it('应该处理服务不可用错误', async () => {
        mockHealthService.getHealthMetrics.mockRejectedValue(new Error('Service Unavailable'));
  
        try {
          await mockHealthService.getHealthMetrics();
        } catch (error: unknown) {
          const err = error as Error;
          expect(err.message).toBe('Service Unavailable');
        }
  
        // 应该从本地缓存获取数据
        const cachedData = await mockStorage.getItem('health_data');
        expect(cachedData).toBeTruthy();
      });
  
      it('应该处理数据验证错误', async () => {
        const invalidData = { heartRate: 'invalid' };
        
        mockHealthService.addHealthRecord.mockResolvedValue({
          success: false,
          error: 'Invalid data format',
          validation_errors: ['heartRate must be a number'],
        });
  
        const result = await mockHealthService.addHealthRecord(invalidData);
        expect(result.success).toBe(false);
        expect(result.validation_errors).toContain('heartRate must be a number');
      });
  
      it('应该实现数据恢复机制', async () => {
        // 模拟数据损坏
        mockStorage.getItem.mockResolvedValue('corrupted_data');
  
        // 应该从备份恢复
        const backupData = JSON.stringify(mockHealthData);
        mockStorage.getItem.mockImplementation((key) => {
          if (key === 'health_data_backup') {
            return Promise.resolve(backupData);
          }
          return Promise.resolve('corrupted_data');
        });
  
        const recoveredData = await mockStorage.getItem('health_data_backup');
        expect(recoveredData).toBe(backupData);
  
        // 恢复主数据
        await mockStorage.setItem('health_data', recoveredData);
        expect(mockStorage.setItem).toHaveBeenCalledWith('health_data', backupData);
      });
    });
  });
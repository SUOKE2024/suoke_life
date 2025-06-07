import { FiveDiagnosisService, FiveDiagnosisInput } from '../fiveDiagnosisService';
/**
* 诊断服务集成测试
*/
describe('诊断服务集成测试', () => {
  let fiveDiagnosisService: FiveDiagnosisService;
  beforeAll(async () => {
    fiveDiagnosisService = new FiveDiagnosisService();
    await fiveDiagnosisService.initialize();
  });
  describe('API集成测试', () => {
    test('五诊综合分析API', async () => {
      const input: FiveDiagnosisInput = {
      userId: "test-user-001",
      sessionId: 'test-session-001',
        lookingData: {
      tongueImage: "data:image/jpeg;base64,test",
      faceImage: 'data:image/jpeg;base64,test',
        },
        inquiryData: {
          symptoms: ["头痛",失眠'],
          medicalHistory: ['无'],
          lifestyle: {
      sleep: "7小时",
      exercise: '偶尔',
          },
        },
      };
      const result = await fiveDiagnosisService.performDiagnosis(input);
      expect(result).toBeDefined();
      expect(result.diagnosticResults).toBeDefined();
      expect(result.sessionId).toBe('test-session-001');
      expect(result.userId).toBe('test-user-001');
    }, 10000);
    test('服务状态监控', () => {
      const status = fiveDiagnosisService.getServiceStatus();
      expect(status).toBeDefined();
      expect(typeof status.isInitialized).toBe('boolean');
      expect(status.performanceMetrics).toBeDefined();
    });
  });
  describe('错误处理测试', () => {
    test('空用户ID处理', async () => {
      const input: FiveDiagnosisInput = {
        userId: '', // 空用户ID
        lookingData: {
      tongueImage: "test",
      faceImage: 'test',
        },
      };
      await expect(fiveDiagnosisService.performDiagnosis(input)).rejects.toThrow();
    });
  });
});

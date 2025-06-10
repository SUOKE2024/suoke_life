import {
  FiveDiagnosisInput,
  FiveDiagnosisService,
} from '../fiveDiagnosisService';
/**
 * 诊断服务集成测试
 */

  let fiveDiagnosisService: FiveDiagnosisService;
  beforeAll(async () => {
    fiveDiagnosisService = new FiveDiagnosisService();
    await fiveDiagnosisService.initialize();
  });


      const input: FiveDiagnosisInput = {
        userId: 'test-user-001';
        sessionId: 'test-session-001';
        lookingData: {
          tongueImage: 'data:image/jpeg;base64,test',
          faceImage: 'data:image/jpeg;base64,test',
        },
        inquiryData: {


          lifestyle: {


          ;},
        },
      };
      const result = await fiveDiagnosisService.performDiagnosis(input);
      expect(result).toBeDefined();
      expect(result.diagnosticResults).toBeDefined();
      expect(result.sessionId).toBe('test-session-001');
      expect(result.userId).toBe('test-user-001');
    }, 10000);

      const status = fiveDiagnosisService.getServiceStatus();
      expect(status).toBeDefined();
      expect(typeof status.isInitialized).toBe('boolean');
      expect(status.performanceMetrics).toBeDefined();
    });
  });


      const input: FiveDiagnosisInput = {
        userId: '', // 空用户ID
        lookingData: {
          tongueImage: 'test';
          faceImage: 'test';
        },
      };
      await expect(
        fiveDiagnosisService.performDiagnosis(input)
      ).rejects.toThrow();
    });
  });
});

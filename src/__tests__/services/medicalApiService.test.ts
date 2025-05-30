import { medicalApiService } from "../../services/medicalApiService";
import type {
  /**
   * 医疗API服务测试
   * 索克生活APP - 第三方医疗API集成测试
   */

  MedicalApiProvider,
  PatientInfo,
  MedicalRecord,
  MedicalAppointment,
  Prescription,
  LabResult,
} from "../../services/medicalApiService";

// Mock apiClient
jest.mock("../../services/apiClient", () => ({
  apiClient: {
    post: jest.fn(),
    get: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
  },
}));

// Mock fetch
global.fetch = jest.fn();

describe("MedicalApiService", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockClear();
  });

  describe("基础功能测试", () => {
    test("应该正确初始化服务", () => {
      expect(medicalApiService).toBeDefined();
      expect(typeof medicalApiService.getPatientInfo).toBe("function");
      expect(typeof medicalApiService.getMedicalRecords).toBe("function");
      expect(typeof medicalApiService.getAppointments).toBe("function");
    });

    test("应该支持所有医疗API提供商", () => {
      const providers: MedicalApiProvider[] = [
        "fhir",
        "epic",
        "cerner",
        "allscripts",
        "athenahealth",
        "veracross",
        "meditech",
        "nextgen",
        "eclinicalworks",
        "practice_fusion",
      ];

      providers.forEach((provider) => {
        expect(typeof provider).toBe("string");
      });
    });
  });

  describe("患者信息获取", () => {
    test("应该成功获取患者信息", async () => {
      const mockPatientData = {
        id: "patient123",
        name: [{ text: "张三" }],
        birthDate: "1990-01-01",
        gender: "male",
        telecom: [
          { system: "phone", value: "13800138000" },
          { system: "email", value: "zhangsan@example.com" },
        ],
        address: [{ text: "北京市朝阳区" }],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockPatientData),
      });

      const result = await medicalApiService.getPatientInfo(
        "fhir",
        "patient123"
      );

      expect(result).toEqual({
        id: "patient123",
        name: "张三",
        dateOfBirth: "1990-01-01",
        gender: "male",
        contactInfo: {
          phone: "13800138000",
          email: "zhangsan@example.com",
          address: "北京市朝阳区",
        },
      });
    });

    test("应该处理API请求失败", async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: "Not Found",
      });

      await expect(
        medicalApiService.getPatientInfo("fhir", "nonexistent")
      ).rejects.toThrow("API request failed: 404 Not Found");
    });

    test("应该处理网络错误", async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(
        new Error("Network error")
      );

      await expect(
        medicalApiService.getPatientInfo("fhir", "patient123")
      ).rejects.toThrow("Network error");
    });
  });

  describe("医疗记录获取", () => {
    test("应该成功获取所有医疗记录", async () => {
      const mockRecordsData = {
        entry: [
          {
            resource: {
              id: "condition123",
              resourceType: "Condition",
              subject: { reference: "Patient/patient123" },
              recordedDate: "2024-01-01T10:00:00Z",
              code: { text: "高血压" },
            },
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockRecordsData),
      });

      const result = await medicalApiService.getMedicalRecords(
        "fhir",
        "patient123"
      );

      expect(result).toHaveLength(1);
      expect(result[0]).toMatchObject({
        id: "condition123",
        patientId: "patient123",
        recordType: "diagnosis",
        source: "fhir",
        verified: true,
      });
    });

    test("应该支持按记录类型过滤", async () => {
      const mockRecordsData = {
        entry: [
          {
            resource: {
              id: "med123",
              resourceType: "MedicationRequest",
              subject: { reference: "Patient/patient123" },
              authoredOn: "2024-01-01T10:00:00Z",
            },
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockRecordsData),
      });

      const result = await medicalApiService.getMedicalRecords(
        "fhir",
        "patient123",
        "prescription"
      );

      expect(result).toHaveLength(1);
      expect(result[0].recordType).toBe("prescription");
    });

    test("应该支持日期范围过滤", async () => {
      const mockRecordsData = { entry: [] };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockRecordsData),
      });

      await medicalApiService.getMedicalRecords(
        "fhir",
        "patient123",
        undefined,
        { start: "2024-01-01", end: "2024-01-31" }
      );

      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining("date=ge2024-01-01&date=le2024-01-31"),
        expect.any(Object)
      );
    });
  });

  describe("预约管理", () => {
    test("应该成功获取预约信息", async () => {
      const mockAppointmentsData = {
        entry: [
          {
            resource: {
              id: "appointment123",
              status: "scheduled",
              serviceType: [{ text: "consultation" }],
              start: "2024-02-01T14:00:00Z",
              minutesDuration: 30,
              participant: [
                { actor: { reference: "Patient/patient123" } },
                { actor: { reference: "Practitioner/doctor123" } },
              ],
            },
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockAppointmentsData),
      });

      const result = await medicalApiService.getAppointments(
        "fhir",
        "patient123"
      );

      expect(result).toHaveLength(1);
      expect(result[0]).toMatchObject({
        id: "appointment123",
        patientId: "patient123",
        clinicianId: "doctor123",
        appointmentType: "consultation",
        status: "scheduled",
        duration: 30,
      });
    });

    test("应该成功创建预约", async () => {
      const mockCreatedAppointment = {
        id: "new_appointment123",
        status: "scheduled",
        start: "2024-02-01T14:00:00Z",
        minutesDuration: 30,
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockCreatedAppointment),
      });

      const appointmentData = {
        patientId: "patient123",
        providerId: "fhir",
        clinicianId: "doctor123",
        appointmentType: "consultation" as const,
        scheduledTime: "2024-02-01T14:00:00Z",
        duration: 30,
        status: "scheduled" as const,
        location: {
          facility: "北京医院",
          address: "北京市朝阳区",
        },
      };

      const result = await medicalApiService.createAppointment(
        "fhir",
        appointmentData
      );

      expect(result).toMatchObject({
        id: "new_appointment123",
        status: "scheduled",
        duration: 30,
      });
    });
  });

  describe("处方管理", () => {
    test("应该成功获取处方信息", async () => {
      const mockPrescriptionsData = {
        entry: [
          {
            resource: {
              id: "prescription123",
              subject: { reference: "Patient/patient123" },
              requester: { reference: "Practitioner/doctor123" },
              medicationCodeableConcept: { text: "阿司匹林" },
              status: "active",
              authoredOn: "2024-01-01T10:00:00Z",
              dosageInstruction: [
                {
                  text: "每日一次，每次100mg",
                  patientInstruction: "饭后服用",
                },
              ],
              dispenseRequest: { numberOfRepeatsAllowed: 2 },
            },
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockPrescriptionsData),
      });

      const result = await medicalApiService.getPrescriptions(
        "fhir",
        "patient123"
      );

      expect(result).toHaveLength(1);
      expect(result[0]).toMatchObject({
        id: "prescription123",
        patientId: "patient123",
        clinicianId: "doctor123",
        medication: {
          name: "阿司匹林",
          dosage: "每日一次，每次100mg",
          instructions: "饭后服用",
        },
        status: "active",
        refillsRemaining: 2,
      });
    });
  });

  describe("实验室结果", () => {
    test("应该成功获取实验室结果", async () => {
      const mockLabResultsData = {
        entry: [
          {
            resource: {
              id: "lab123",
              subject: { reference: "Patient/patient123" },
              code: {
                text: "血糖",
                coding: [{ code: "glucose" }],
              },
              valueQuantity: {
                value: 5.5,
                unit: "mmol/L",
              },
              interpretation: [{ coding: [{ code: "N" }] }],
              effectiveDateTime: "2024-01-01T10:00:00Z",
              issued: "2024-01-01T09:00:00Z",
              performer: [
                {
                  reference: "Practitioner/lab_tech123",
                  display: "检验科",
                },
              ],
            },
          },
        ],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(mockLabResultsData),
      });

      const result = await medicalApiService.getLabResults(
        "fhir",
        "patient123"
      );

      expect(result).toHaveLength(1);
      expect(result[0]).toMatchObject({
        id: "lab123",
        patientId: "patient123",
        testName: "血糖",
        testCode: "glucose",
        result: {
          value: 5.5,
          unit: "mmol/L",
          status: "normal",
        },
        clinicianId: "lab_tech123",
        labFacility: "检验科",
      });
    });
  });

  describe("多提供商同步", () => {
    test("应该成功同步多个提供商的数据", async () => {
      // Mock successful responses for multiple providers
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ entry: [] }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ entry: [] }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ entry: [] }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ entry: [] }),
        });

      const result = await medicalApiService.syncMultipleProviders(
        ["fhir", "epic"],
        "patient123"
      );

      expect(result.success).toContain("fhir");
      expect(result.success).toContain("epic");
      expect(result.failed).toHaveLength(0);
      expect(result.data).toHaveProperty("records");
      expect(result.data).toHaveProperty("appointments");
      expect(result.data).toHaveProperty("prescriptions");
      expect(result.data).toHaveProperty("labResults");
    });

    test("应该处理部分提供商失败的情况", async () => {
      // Mock one successful and one failed response
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ entry: [] }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ entry: [] }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ entry: [] }),
        })
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve({ entry: [] }),
        })
        .mockRejectedValueOnce(new Error("Epic API error"));

      const result = await medicalApiService.syncMultipleProviders(
        ["fhir", "epic"],
        "patient123"
      );

      expect(result.success).toContain("fhir");
      expect(result.failed).toHaveLength(1);
      expect(result.failed[0]).toMatchObject({
        provider: "epic",
        error: "Epic API error",
      });
    });
  });

  describe("错误处理", () => {
    test("应该处理速率限制", async () => {
      // 模拟超过速率限制的情况
      const promises = [];
      for (let i = 0; i < 150; i++) {
        promises.push(medicalApiService.getPatientInfo("fhir", `patient${i}`));
      }

      // 应该有一些请求因为速率限制而失败
      const results = await Promise.allSettled(promises);
      const rejectedResults = results.filter(
        (result) => result.status === "rejected"
      );

      expect(rejectedResults.length).toBeGreaterThan(0);
      expect(rejectedResults[0].status).toBe("rejected");
    });

    test("应该处理无效的提供商", async () => {
      await expect(
        medicalApiService.getPatientInfo(
          "invalid_provider" as any,
          "patient123"
        )
      ).rejects.toThrow(
        "Configuration not found for provider: invalid_provider"
      );
    });

    test("应该处理空响应数据", async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({}),
      });

      const result = await medicalApiService.getMedicalRecords(
        "fhir",
        "patient123"
      );
      expect(result).toEqual([]);
    });
  });

  describe("性能测试", () => {
    test("应该在合理时间内完成API调用", async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () =>
          Promise.resolve({
            id: "patient123",
            name: [{ text: "张三" }],
            birthDate: "1990-01-01",
            gender: "male",
          }),
      });

      const startTime = Date.now();
      await medicalApiService.getPatientInfo("fhir", "patient123");
      const endTime = Date.now();

      expect(endTime - startTime).toBeLessThan(5000); // 5秒内完成
    });

    test("应该支持并发请求", async () => {
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () =>
          Promise.resolve({
            id: "patient123",
            name: [{ text: "张三" }],
            birthDate: "1990-01-01",
            gender: "male",
          }),
      });

      const promises = Array.from({ length: 10 }, (_, i) =>
        medicalApiService.getPatientInfo("fhir", `patient${i}`)
      );

      const startTime = Date.now();
      const results = await Promise.all(promises);
      const endTime = Date.now();

      expect(results).toHaveLength(10);
      expect(endTime - startTime).toBeLessThan(10000); // 10秒内完成所有请求
    });
  });

  describe("数据转换测试", () => {
    test("应该正确转换FHIR患者数据", async () => {
      const fhirPatientData = {
        id: "patient123",
        name: [
          {
            given: ["张", "三"],
            family: "先生",
          },
        ],
        birthDate: "1990-01-01",
        gender: "male",
        telecom: [
          { system: "phone", value: "+86-13800138000" },
          { system: "email", value: "zhangsan@example.com" },
        ],
        address: [{ text: "北京市朝阳区建国路1号" }],
      };

      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve(fhirPatientData),
      });

      const result = await medicalApiService.getPatientInfo(
        "fhir",
        "patient123"
      );

      expect(result.name).toBe("张 三 先生");
      expect(result.contactInfo.phone).toBe("+86-13800138000");
      expect(result.contactInfo.email).toBe("zhangsan@example.com");
      expect(result.contactInfo.address).toBe("北京市朝阳区建国路1号");
    });

    test("应该正确映射资源类型到记录类型", async () => {
      const testCases = [
        { resourceType: "Condition", expectedType: "diagnosis" },
        { resourceType: "MedicationRequest", expectedType: "prescription" },
        { resourceType: "Observation", expectedType: "lab_result" },
        { resourceType: "AllergyIntolerance", expectedType: "allergy" },
        { resourceType: "Immunization", expectedType: "immunization" },
      ];

      for (const testCase of testCases) {
        const mockData = {
          entry: [
            {
              resource: {
                id: "test123",
                resourceType: testCase.resourceType,
                subject: { reference: "Patient/patient123" },
                recordedDate: "2024-01-01T10:00:00Z",
              },
            },
          ],
        };

        (global.fetch as jest.Mock).mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve(mockData),
        });

        const result = await medicalApiService.getMedicalRecords(
          "fhir",
          "patient123"
        );
        expect(result[0].recordType).toBe(testCase.expectedType);
      }
    });
  });
});

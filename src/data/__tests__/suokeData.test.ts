import { SERVICE_CATEGORIES, DIAGNOSIS_SERVICES, ECO_SERVICES, OTHER_SERVICES, ALL_SERVICES, RECOMMENDED_SERVICES, POPULAR_SERVICES } from "../suokeData";

describe("suokeData", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("SERVICE_CATEGORIES", () => {
    it("should be defined", () => {
      expect(SERVICE_CATEGORIES).toBeDefined();
    });

    it("should be an array", () => {
      expect(Array.isArray(SERVICE_CATEGORIES)).toBe(true);
    });
  });

  describe("DIAGNOSIS_SERVICES", () => {
    it("should be defined", () => {
      expect(DIAGNOSIS_SERVICES).toBeDefined();
    });

    it("should be an array", () => {
      expect(Array.isArray(DIAGNOSIS_SERVICES)).toBe(true);
    });
  });

  describe("ECO_SERVICES", () => {
    it("should be defined", () => {
      expect(ECO_SERVICES).toBeDefined();
    });

    it("should be an array", () => {
      expect(Array.isArray(ECO_SERVICES)).toBe(true);
    });
  });

  describe("OTHER_SERVICES", () => {
    it("should be defined", () => {
      expect(OTHER_SERVICES).toBeDefined();
    });

    it("should be an array", () => {
      expect(Array.isArray(OTHER_SERVICES)).toBe(true);
    });
  });

  describe("ALL_SERVICES", () => {
    it("should be defined", () => {
      expect(ALL_SERVICES).toBeDefined();
    });

    it("should be an array", () => {
      expect(Array.isArray(ALL_SERVICES)).toBe(true);
    });
  });

  describe("RECOMMENDED_SERVICES", () => {
    it("should be defined", () => {
      expect(RECOMMENDED_SERVICES).toBeDefined();
    });

    it("should be an array", () => {
      expect(Array.isArray(RECOMMENDED_SERVICES)).toBe(true);
    });
  });

  describe("POPULAR_SERVICES", () => {
    it("should be defined", () => {
      expect(POPULAR_SERVICES).toBeDefined();
    });

    it("should be an array", () => {
      expect(Array.isArray(POPULAR_SERVICES)).toBe(true);
    });
  });
});
import { SOER_SUGGESTIONS, HEALTH_METRICS, LIFE_PLANS, LIFE_HABITS, LIFE_GOALS, LIFE_STATS } from "../lifeData";

describe("lifeData", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe("SOER_SUGGESTIONS", () => {
    it("should be defined", () => {
      expect(SOER_SUGGESTIONS).toBeDefined();
    });

    it("should be an array", () => {
      expect(Array.isArray(SOER_SUGGESTIONS)).toBe(true);
    });
  });

  describe("HEALTH_METRICS", () => {
    it("should be defined", () => {
      expect(HEALTH_METRICS).toBeDefined();
    });

    it("should be an array", () => {
      expect(Array.isArray(HEALTH_METRICS)).toBe(true);
    });
  });

  describe("LIFE_PLANS", () => {
    it("should be defined", () => {
      expect(LIFE_PLANS).toBeDefined();
    });
  });

  describe("LIFE_HABITS", () => {
    it("should be defined", () => {
      expect(LIFE_HABITS).toBeDefined();
    });
  });

  describe("LIFE_GOALS", () => {
    it("should be defined", () => {
      expect(LIFE_GOALS).toBeDefined();
    });
  });

  describe("LIFE_STATS", () => {
    it("should be defined", () => {
      expect(LIFE_STATS).toBeDefined();
    });
  });
});
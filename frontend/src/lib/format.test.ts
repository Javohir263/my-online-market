import { describe, expect, it } from "vitest";
import { formatPrice, formatDate } from "./format";

describe("formatPrice", () => {
  it("formats with grouped thousands + currency", () => {
    const out = formatPrice(1500000);
    expect(out).toContain("UZS");
    // Grouping char varies by environment; digits must be present
    expect(out.replace(/\D/g, "")).toBe("1500000");
  });

  it("accepts string input", () => {
    expect(formatPrice("99000").replace(/\D/g, "")).toBe("99000");
  });

  it("drops fraction digits", () => {
    expect(formatPrice(1000.99).replace(/\D/g, "")).toBe("1001");
  });

  it("respects custom currency", () => {
    expect(formatPrice(100, "USD")).toContain("USD");
  });
});

describe("formatDate", () => {
  it("renders a non-empty localized date", () => {
    const out = formatDate("2026-05-30T10:00:00Z");
    expect(out.length).toBeGreaterThan(0);
    expect(out).toMatch(/2026/);
  });
});

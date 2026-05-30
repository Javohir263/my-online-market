import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { Price } from "./price";

describe("Price", () => {
  it("renders the current price", () => {
    render(<Price current={150000} />);
    expect(screen.getByText(/150[\s ]?000/)).toBeInTheDocument();
  });

  it("shows struck-through base price when discounted", () => {
    const { container } = render(
      <Price current={70000} base={100000} hasDiscount />,
    );
    const struck = container.querySelector(".line-through");
    expect(struck).not.toBeNull();
    expect(struck?.textContent?.replace(/\D/g, "")).toBe("100000");
  });

  it("hides base price when no discount", () => {
    const { container } = render(<Price current={100000} base={100000} />);
    expect(container.querySelector(".line-through")).toBeNull();
  });
});

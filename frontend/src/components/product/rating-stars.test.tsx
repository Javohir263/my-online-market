import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import { RatingStars } from "./rating-stars";

describe("RatingStars", () => {
  it("renders 5 star icons", () => {
    const { container } = render(<RatingStars value={4} count={10} />);
    // lucide Star renders an <svg>
    expect(container.querySelectorAll("svg")).toHaveLength(5);
  });

  it("shows the review count", () => {
    render(<RatingStars value={4.5} count={42} />);
    expect(screen.getByText("(42)")).toBeInTheDocument();
  });

  it("hides count when showCount is false", () => {
    render(<RatingStars value={3} count={5} showCount={false} />);
    expect(screen.queryByText("(5)")).toBeNull();
  });

  it("accepts string rating value", () => {
    const { container } = render(<RatingStars value="4.00" count={1} />);
    expect(container.querySelectorAll("svg")).toHaveLength(5);
  });
});

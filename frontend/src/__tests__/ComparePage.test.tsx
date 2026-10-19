import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ComparePage } from "../components/ComparePage";

const prediction = {
  prediction: "BBB+",
  probability_bbb_plus: 0.79,
  canonical_smiles: "Cn1c(=O)c2c(ncn2C)n(C)c1=O",
  descriptors: { "Molecular Weight": 194.19, LogP: -1.03, TPSA: 61.82 },
  applicability_domain: { max_similarity: 0.86 },
  uncertainty: { tree_probability_std: 0.08 },
};

describe("Candidate comparison", () => {
  afterEach(() => vi.restoreAllMocks());

  it("scores each filled candidate through the production prediction endpoint", async () => {
    const fetchMock = vi.fn(() => Promise.resolve({ ok: true, json: async () => prediction }));
    vi.stubGlobal("fetch", fetchMock);
    render(<ComparePage />);

    fireEvent.change(screen.getByLabelText("Candidate 1 SMILES"), { target: { value: "CCO" } });
    fireEvent.change(screen.getByLabelText("Candidate 2 SMILES"), { target: { value: "CCN" } });
    fireEvent.click(screen.getByRole("button", { name: "Compare 2 candidates" }));

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2));
    expect(fetchMock).toHaveBeenCalledWith(expect.stringContaining("/api/predict"), expect.objectContaining({
      method: "POST",
      body: JSON.stringify({ smiles: "CCO" }),
    }));
    expect(screen.getByText("Model comparison")).toBeInTheDocument();
    expect(screen.getAllByText("BBB+")).toHaveLength(2);
    expect(screen.getAllByText("0.86")).toHaveLength(2);
  });
});

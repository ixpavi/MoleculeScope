import { render, screen, fireEvent, waitFor, within } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import App from "../App";

const MOCK_CAFFEINE_RESPONSE = {
  prediction: "BBB+",
  probability_bbb_plus: 0.7898609017435456,
  probability_bbb_minus: 0.2101390982564544,
  canonical_smiles: "Cn1c(=O)c2c(ncn2C)n(C)c1=O",
  molecular_formula: "C8H10N4O2",
  inchikey: "RYYVLZVUVIJVGH-UHFFFAOYSA-N",
  svg: '<svg id="caffeine-svg"><rect width="300" height="300" fill="transparent"/></svg>',
  descriptors: {
    "Molecular Weight": 194.194,
    "LogP": -1.0293,
    "TPSA": 61.82,
    "H-Bond Donors": 0,
    "H-Bond Acceptors": 3,
    "Rotatable Bonds": 0,
    "Ring Count": 2,
    "Aromatic Ring Count": 2,
    "Heavy Atom Count": 14,
    "Fraction CSP3": 0.375,
    "Formal Charge": 0
  },
  descriptor_percentiles: {
    "Molecular Weight": { percentile: 7.4, position: 0.1 },
    "LogP": { percentile: 8.0, position: 0.17 },
    "TPSA": { percentile: 42.2, position: 0.29 },
    "H-Bond Donors": { percentile: 12.0, position: 0.06 },
    "H-Bond Acceptors": { percentile: 62.0, position: 0.48 },
    "Rotatable Bonds": { percentile: 5.0, position: 0.04 },
    "Ring Count": { percentile: 48.0, position: 0.4 },
    "Aromatic Ring Count": { percentile: 48.0, position: 0.4 },
    "Heavy Atom Count": { percentile: 19.0, position: 0.15 },
    "Fraction CSP3": { percentile: 51.0, position: 0.38 },
    "Formal Charge": { percentile: 40.0, position: 0.5 },
  },
  applicability_domain: {
    max_similarity: 1.0,
    nearest_neighbors: [
      { name: "58-08-2", smiles: "Cn1c(=O)c2c(ncn2C)n(C)c1=O", bbb_label: "BBB+", similarity: 1.0 },
      { name: "dimethazan", smiles: "CN1C(=O)N(C)c2nc(N(C)C)n(C)c2C1=O", bbb_label: "BBB+", similarity: 0.568 },
    ],
  },
  uncertainty: {
    tree_probability_std: 0.0863,
    tree_probability_iqr_low: 0.85,
    tree_probability_iqr_high: 1.0,
    tree_count: 250,
    trees_voting_bbb_plus: 227,
    vote_histogram: Array.from({ length: 20 }, (_, i) => ({
      bin_start: i * 0.05,
      bin_end: (i + 1) * 0.05,
      count: i === 18 ? 120 : i < 4 ? 2 : 5,
      height_pct: i === 18 ? 100 : i < 4 ? 1.7 : 4.2,
    })),
  },
};

const MOCK_EXPLANATION_RESPONSE = {
  canonical_smiles: "Cn1c(=O)c2c(ncn2C)n(C)c1=O",
  prediction: "BBB+",
  probability_bbb_plus: 0.7898609017435456,
  base_value: 0.5,
  contributions: [
    { descriptor: "TPSA", descriptor_value: 61.82, shap_value: 0.15 },
    { descriptor: "LogP", descriptor_value: -1.0293, shap_value: -0.08 },
  ],
};

const fetchRouter = (overrides: Record<string, any> = {}) =>
  vi.fn((url: string) => {
    for (const key of Object.keys(overrides)) {
      if (url.includes(key)) {
        return Promise.resolve({ ok: true, json: async () => overrides[key] });
      }
    }
    if (url.includes("/api/predict")) {
      return Promise.resolve({ ok: true, json: async () => MOCK_CAFFEINE_RESPONSE });
    }
    if (url.includes("/api/explain")) {
      return Promise.resolve({ ok: true, json: async () => MOCK_EXPLANATION_RESPONSE });
    }
    return Promise.resolve({ ok: true, json: async () => ({}) });
  });

const setSmilesAndRun = (value: string) => {
  const textarea = document.getElementById("smiles-input") as HTMLTextAreaElement;
  fireEvent.change(textarea, { target: { value } });
  fireEvent.click(screen.getByRole("button", { name: /Run prediction/i }));
};

describe("MoleculeScope Frontend Unit Tests", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", fetchRouter());
  });

  afterEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
  });

  it("1. Predictor page renders correctly", () => {
    render(<App />);
    expect(screen.getByText("SCREENING / PREDICTOR")).toBeInTheDocument();
    expect(document.querySelector(".topbar .title")?.textContent).toBe("MoleculeScope");
    expect(document.getElementById("smiles-input")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Run prediction/i })).toBeInTheDocument();
  });

  it("2. SMILES input accepts text typed by user", () => {
    render(<App />);
    const textarea = document.getElementById("smiles-input") as HTMLTextAreaElement;
    fireEvent.change(textarea, { target: { value: "CCO" } });
    expect(textarea.value).toBe("CCO");
  });

  it("3. No prediction layout is shown before running inference", () => {
    render(<App />);
    expect(screen.getByText("Screen a molecule")).toBeInTheDocument();
    expect(screen.queryByText("BBB+")).not.toBeInTheDocument();
  });

  it("4. Run prediction calls fetch API with the correct payload", async () => {
    const fetchMock = fetchRouter();
    vi.stubGlobal("fetch", fetchMock);

    render(<App />);
    setSmilesAndRun("CCO");

    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledWith(
        expect.stringContaining("/api/predict"),
        expect.objectContaining({
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ smiles: "CCO" }),
        })
      );
    });
  });

  it("5. Loading state appears during active fetch requests", async () => {
    let resolveFetch: any;
    const fetchPromise = new Promise((resolve) => { resolveFetch = resolve; });
    vi.stubGlobal("fetch", () => fetchPromise);

    render(<App />);
    const textarea = document.getElementById("smiles-input") as HTMLTextAreaElement;
    fireEvent.change(textarea, { target: { value: "CCO" } });
    const runBtn = screen.getByRole("button", { name: /Run prediction/i });
    fireEvent.click(runBtn);

    expect(screen.getByText("Running...")).toBeInTheDocument();
    expect(runBtn).toBeDisabled();

    resolveFetch({ ok: true, json: async () => MOCK_CAFFEINE_RESPONSE });
  });

  it("6. Successful prediction renders the BBB+ verdict", async () => {
    render(<App />);
    setSmilesAndRun("CN1C(=O)N(C)c2ncn(C)c2C1=O");

    await waitFor(() => {
      expect(screen.getAllByText("BBB+").length).toBeGreaterThan(0);
    });
  });

  it("7. Probability and consensus label display correctly", async () => {
    render(<App />);
    setSmilesAndRun("CN1C(=O)N(C)c2ncn(C)c2C1=O");

    await waitFor(() => {
      expect(screen.getByText(/p 0\.790/)).toBeInTheDocument();
      expect(screen.getByText(/high consensus/)).toBeInTheDocument();
    });
  });

  it("8. RDKit generated SVG renders safely in the structure card", async () => {
    render(<App />);
    setSmilesAndRun("CN1C(=O)N(C)c2ncn(C)c2C1=O");

    await waitFor(() => {
      const container = document.querySelector(".mol-box");
      expect(container).toBeInTheDocument();
      expect(container?.querySelector("svg")).toBeInTheDocument();
    });
  });

  it("8b. Applicability domain / neighbours card renders real nearest neighbors", async () => {
    render(<App />);
    setSmilesAndRun("CN1C(=O)N(C)c2ncn(C)c2C1=O");

    await waitFor(() => {
      expect(screen.getByText("Applicability domain")).toBeInTheDocument();
      expect(screen.getByText("dimethazan")).toBeInTheDocument();
      expect(screen.getByText(/max T 1\.00/)).toBeInTheDocument();
    });
  });

  it("8c. Vote histogram renders real tree-vote data in the Prediction card", async () => {
    render(<App />);
    setSmilesAndRun("CN1C(=O)N(C)c2ncn(C)c2C1=O");

    await waitFor(() => {
      expect(screen.getByText(/227 of 250 trees vote BBB\+/)).toBeInTheDocument();
      expect(document.querySelectorAll(".hist i").length).toBe(20);
    });
  });

  it("9. All 11 descriptors render with real training-distribution percentiles", async () => {
    render(<App />);
    setSmilesAndRun("CN1C(=O)N(C)c2ncn(C)c2C1=O");

    await waitFor(() => {
      expect(screen.getByText("MolWt")).toBeInTheDocument();
      expect(screen.getByText("194.19")).toBeInTheDocument();
      expect(screen.getByText("TPSA")).toBeInTheDocument();
      expect(screen.getByText("NumHDonors")).toBeInTheDocument();
      expect(screen.getByText("NumHAcceptors")).toBeInTheDocument();
      expect(screen.getByText("NumRotatableBonds")).toBeInTheDocument();
      expect(screen.getByText("FractionCSP3")).toBeInTheDocument();
      expect(screen.getByText("FormalCharge")).toBeInTheDocument();
      expect(screen.getByText("7th")).toBeInTheDocument();
    });
  });

  it("10. HTTP 400 error returns and displays a friendly warning message", async () => {
    vi.stubGlobal("fetch", fetchRouter({
      "/api/predict": undefined,
    }));
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: false,
      status: 400,
      json: async () => ({ detail: "Invalid or malformed SMILES string: 'NOT_A_SMILES'." }),
    }));

    render(<App />);
    setSmilesAndRun("NOT_A_SMILES");

    await waitFor(() => {
      expect(screen.getByText("Invalid or malformed SMILES string: 'NOT_A_SMILES'.")).toBeInTheDocument();
    });
  });

  it("11. Network connectivity / server down error displays a friendly message", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("Connection refused")));

    render(<App />);
    setSmilesAndRun("CN1C(=O)N(C)c2ncn(C)c2C1=O");

    await waitFor(() => {
      expect(screen.getByText(/Unable to connect to the MoleculeScope backend/i)).toBeInTheDocument();
    });
  });

  it("11b. Evaluation figures render with alt text and fall back gracefully on load error", () => {
    render(<App />);
    fireEvent.click(screen.getAllByRole("button", { name: /Performance/i })[0]);

    expect(screen.getByText("Evaluation Figures")).toBeInTheDocument();
    const img = screen.getByAltText("ROC Curves (Scaffold Split)") as HTMLImageElement;
    expect(img).toBeInTheDocument();

    fireEvent.error(img);
    expect(screen.queryByAltText("ROC Curves (Scaffold Split)")).not.toBeInTheDocument();
    expect(screen.getByText("Figure unavailable")).toBeInTheDocument();
  });

  it("12. Performance tab renders the verified Phase 5 evaluation metrics", () => {
    render(<App />);
    fireEvent.click(screen.getAllByRole("button", { name: /Performance/i })[0]);

    expect(screen.getByText(/Scientific Evaluation Disclaimer/i)).toBeInTheDocument();
    expect(screen.getAllByText("74.47%")[0]).toBeInTheDocument();
    expect(screen.getAllByText("0.7212")[0]).toBeInTheDocument();
    expect(screen.getAllByText("0.8017")[0]).toBeInTheDocument();
    expect(screen.getAllByText("0.8504")[0]).toBeInTheDocument();
    expect(screen.getByText("Random Forest + Descriptors")).toBeInTheDocument();
    expect(screen.getByText(/The model maps structure to permeability using passive molecular descriptors/i)).toBeInTheDocument();
  });

  it("14. SHAP attribution card renders real per-descriptor contributions", async () => {
    render(<App />);
    setSmilesAndRun("CN1C(=O)N(C)c2ncn(C)c2C1=O");

    await waitFor(() => {
      expect(screen.getByText("SHAP attribution")).toBeInTheDocument();
      expect(screen.getByText("+0.150")).toBeInTheDocument();
      expect(screen.getByText("-0.080")).toBeInTheDocument();
    });
  });

  it("15. Global feature importance chart renders on the Performance tab", async () => {
    vi.stubGlobal("fetch", fetchRouter({
      "/api/explain/global": { feature_importances: [{ descriptor: "TPSA", importance: 0.35 }, { descriptor: "LogP", importance: 0.2 }] },
    }));

    render(<App />);
    fireEvent.click(screen.getAllByRole("button", { name: /Performance/i })[0]);

    await waitFor(() => {
      expect(screen.getByText("Global Feature Importance")).toBeInTheDocument();
      expect(screen.getByText("35.0%")).toBeInTheDocument();
    });
  });

  it("16. Compound name search populates SMILES and the compound-name field on selection", async () => {
    vi.stubGlobal("fetch", fetchRouter({
      "/api/molecules/search": {
        results: [
          { name: "ibuprofen", smiles: "CC(C)Cc1ccc(C(C)C(=O)O)cc1", verified: false },
          { name: "(r)-(-)-ibuprofen", smiles: "CC(C)Cc1ccc([C@@H](C)C(=O)O)cc1", verified: false },
        ],
      },
    }));

    render(<App />);
    const searchInput = screen.getByPlaceholderText("e.g. ibuprofen, caffeine, morphine...");
    fireEvent.change(searchInput, { target: { value: "ibuprofen" } });

    await waitFor(() => {
      expect(screen.getByText("ibuprofen")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText("ibuprofen"));

    const textarea = document.getElementById("smiles-input") as HTMLTextAreaElement;
    expect(textarea.value).toBe("CC(C)Cc1ccc(C(C)C(=O)O)cc1");
    expect(screen.getByText("matched · ibuprofen")).toBeInTheDocument();
  });

  it("16b. Compound name search supports keyboard navigation (ArrowDown + Enter)", async () => {
    vi.stubGlobal("fetch", fetchRouter({
      "/api/molecules/search": {
        results: [
          { name: "ibuprofen", smiles: "CC(C)Cc1ccc(C(C)C(=O)O)cc1", verified: false },
          { name: "(r)-(-)-ibuprofen", smiles: "CC(C)Cc1ccc([C@@H](C)C(=O)O)cc1", verified: false },
        ],
      },
    }));

    render(<App />);
    const searchInput = screen.getByPlaceholderText("e.g. ibuprofen, caffeine, morphine...");
    fireEvent.change(searchInput, { target: { value: "ibuprofen" } });

    await waitFor(() => {
      expect(screen.getByText("(r)-(-)-ibuprofen")).toBeInTheDocument();
    });

    fireEvent.keyDown(searchInput, { key: "ArrowDown" });
    fireEvent.keyDown(searchInput, { key: "ArrowDown" });
    fireEvent.keyDown(searchInput, { key: "Enter" });

    const textarea = document.getElementById("smiles-input") as HTMLTextAreaElement;
    expect(textarea.value).toBe("CC(C)Cc1ccc([C@@H](C)C(=O)O)cc1");
  });

  it("16c. Compound name search shows a Verified badge for hand-verified aliases", async () => {
    vi.stubGlobal("fetch", fetchRouter({
      "/api/molecules/search": { results: [{ name: "Aspirin", smiles: "CC(=O)Oc1ccccc1C(=O)O", verified: true }] },
    }));

    render(<App />);
    const searchInput = screen.getByPlaceholderText("e.g. ibuprofen, caffeine, morphine...");
    fireEvent.change(searchInput, { target: { value: "aspirin" } });

    await waitFor(() => {
      const listbox = screen.getByRole("listbox");
      expect(within(listbox).getByText("Aspirin")).toBeInTheDocument();
      expect(within(listbox).getByText("Verified")).toBeInTheDocument();
    });
  });

  it("16d. Compound name search shows a 'Differs from others' badge for structurally inconsistent duplicate names", async () => {
    vi.stubGlobal("fetch", fetchRouter({
      "/api/molecules/search": {
        results: [
          { name: "morphine", smiles: "CN1CC[C@]23c4c5ccc(O)c4O[C@H]2[C@@H](O)C=C[C@H]3[C@H]1C5", verified: false, group_consistent: true },
          { name: "morphine", smiles: "Cc1ccccc1-n1c(C)nc2ccccc2c1=O", verified: false, group_consistent: false },
        ],
      },
    }));

    render(<App />);
    const searchInput = screen.getByPlaceholderText("e.g. ibuprofen, caffeine, morphine...");
    fireEvent.change(searchInput, { target: { value: "morphine" } });

    await waitFor(() => {
      const listbox = screen.getByRole("listbox");
      expect(within(listbox).getAllByText("morphine")).toHaveLength(2);
      expect(within(listbox).queryAllByText("Differs from others")).toHaveLength(1);
    });
  });

  it("17. Compound name search shows a no-match message for an unmatched query", async () => {
    vi.stubGlobal("fetch", fetchRouter({ "/api/molecules/search": { results: [] } }));

    render(<App />);
    const searchInput = screen.getByPlaceholderText("e.g. ibuprofen, caffeine, morphine...");
    fireEvent.change(searchInput, { target: { value: "notarealdrugname" } });

    await waitFor(() => {
      expect(screen.getByText(/No matches in the B3DB dataset/i)).toBeInTheDocument();
    });
  });

  it("18. A successful prediction with a matched compound name is remembered in 'recent'", async () => {
    vi.stubGlobal("fetch", fetchRouter({
      "/api/molecules/search": { results: [{ name: "caffeine", smiles: "CN1C(=O)N(C)c2ncn(C)c2C1=O", verified: true }] },
    }));

    render(<App />);
    const searchInput = screen.getByPlaceholderText("e.g. ibuprofen, caffeine, morphine...");
    fireEvent.change(searchInput, { target: { value: "caffeine" } });
    await waitFor(() => expect(screen.getByText("caffeine")).toBeInTheDocument());
    fireEvent.click(screen.getByText("caffeine"));

    fireEvent.click(screen.getByRole("button", { name: /Run prediction/i }));

    await waitFor(() => {
      expect(screen.getAllByText("BBB+").length).toBeGreaterThan(0);
    });

    expect(screen.getByText("recent")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "caffeine" })).toBeInTheDocument();
  });

  it("19. Export button is disabled until a prediction exists", async () => {
    render(<App />);
    const exportBtn = screen.getByRole("button", { name: /Export/i });
    expect(exportBtn).toBeDisabled();

    setSmilesAndRun("CN1C(=O)N(C)c2ncn(C)c2C1=O");

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Export/i })).not.toBeDisabled();
    });
  });
});

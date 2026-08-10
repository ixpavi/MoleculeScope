import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { BatchScreenerPage } from "../components/BatchScreenerPage";

// Mock response payload
const MOCK_BATCH_RESPONSE = {
  summary: {
    filename: "library.csv",
    total_rows: 6,
    processed_rows: 4,
    failed_rows: 2,
    bbb_plus_count: 3,
    bbb_minus_count: 1
  },
  results: [
    {
      row_index: 1,
      input_smiles: "CN1C(=O)N(C)c2ncn(C)c2C1=O",
      status: "success",
      error: null,
      prediction: "BBB+",
      probability_bbb_plus: 0.7898609017,
      probability_bbb_minus: 0.2101390983,
      canonical_smiles: "CN1C(=O)N(C)c2ncn(C)c2C1=O",
      molecular_formula: "C8H10N4O2",
      descriptors: {
        "Molecular Weight": 194.194,
        "LogP": -1.0293,
        "TPSA": 61.82,
        "H-Bond Donors": 0.0,
        "H-Bond Acceptors": 3.0,
        "Rotatable Bonds": 0.0,
        "Ring Count": 2.0,
        "Aromatic Ring Count": 2.0,
        "Heavy Atom Count": 14.0,
        "Fraction CSP3": 0.375,
        "Formal Charge": 0.0
      },
      extra_columns: { "Compound_ID": "CMP001" }
    },
    {
      row_index: 2,
      input_smiles: "CC(=O)Oc1ccccc1C(=O)O",
      status: "success",
      error: null,
      prediction: "BBB+",
      probability_bbb_plus: 0.6855578530,
      probability_bbb_minus: 0.3144421470,
      canonical_smiles: "CC(=O)Oc1ccccc1C(=O)O",
      molecular_formula: "C9H8O4",
      descriptors: {
        "Molecular Weight": 180.159,
        "LogP": 1.3101,
        "TPSA": 63.60,
        "H-Bond Donors": 1.0,
        "H-Bond Acceptors": 3.0,
        "Rotatable Bonds": 2.0,
        "Ring Count": 1.0,
        "Aromatic Ring Count": 1.0,
        "Heavy Atom Count": 13.0,
        "Fraction CSP3": 0.111,
        "Formal Charge": 0.0
      },
      extra_columns: { "Compound_ID": "CMP002" }
    },
    {
      row_index: 3,
      input_smiles: "NOT_A_SMILES",
      status: "error",
      error: "Invalid or malformed SMILES string: 'NOT_A_SMILES'.",
      prediction: null,
      probability_bbb_plus: null,
      probability_bbb_minus: null,
      canonical_smiles: null,
      molecular_formula: null,
      descriptors: null,
      extra_columns: { "Compound_ID": "CMP003" }
    },
    {
      row_index: 4,
      input_smiles: "CCO.O",
      status: "error",
      error: "Multi-component structures (mixtures/complexes containing '.') are excluded from prediction.",
      prediction: null,
      probability_bbb_plus: null,
      probability_bbb_minus: null,
      canonical_smiles: null,
      molecular_formula: null,
      descriptors: null,
      extra_columns: { "Compound_ID": "CMP004" }
    },
    {
      row_index: 5,
      input_smiles: "CC(C)Cc1ccc(cc1)C(C)C(=O)O",
      status: "success",
      error: null,
      prediction: "BBB+",
      probability_bbb_plus: 0.7920485218,
      probability_bbb_minus: 0.2079514782,
      canonical_smiles: "CC(C)Cc1ccc(cc1)C(C)C(=O)O",
      molecular_formula: "C13H18O2",
      descriptors: {
        "Molecular Weight": 206.285,
        "LogP": 3.0674,
        "TPSA": 37.30,
        "H-Bond Donors": 1.0,
        "H-Bond Acceptors": 1.0,
        "Rotatable Bonds": 4.0,
        "Ring Count": 1.0,
        "Aromatic Ring Count": 1.0,
        "Heavy Atom Count": 15.0,
        "Fraction CSP3": 0.385,
        "Formal Charge": 0.0
      },
      extra_columns: { "Compound_ID": "CMP005" }
    },
    {
      row_index: 6,
      input_smiles: "CC(=O)Nc1ccc(O)cc1",
      status: "success",
      error: null,
      prediction: "BBB-",
      probability_bbb_plus: 0.450123456,
      probability_bbb_minus: 0.549876544,
      canonical_smiles: "CC(=O)Nc1ccc(O)cc1",
      molecular_formula: "C8H9NO2",
      descriptors: {
        "Molecular Weight": 151.165,
        "LogP": 1.3501,
        "TPSA": 49.33,
        "H-Bond Donors": 2.0,
        "H-Bond Acceptors": 2.0,
        "Rotatable Bonds": 1.0,
        "Ring Count": 1.0,
        "Aromatic Ring Count": 1.0,
        "Heavy Atom Count": 11.0,
        "Fraction CSP3": 0.125,
        "Formal Charge": 0.0
      },
      extra_columns: { "Compound_ID": "CMP006" }
    }
  ]
};

describe("MoleculeScope Batch Screener Page Unit Tests", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("1. Batch Screener renders title and description successfully", () => {
    render(<BatchScreenerPage />);
    expect(screen.getByText("Batch Screening & Screenings Export")).toBeInTheDocument();
    expect(screen.getByText(/Upload a CSV molecular library/i)).toBeInTheDocument();
    expect(screen.getByText(/Drag & drop CSV file or click to browse/i)).toBeInTheDocument();
  });

  it("2. File selection accepts CSV files", () => {
    render(<BatchScreenerPage />);
    const file = new File(["smiles\nCCO"], "valid.csv", { type: "text/csv" });
    const input = document.querySelector("input[type='file']") as HTMLInputElement;
    
    fireEvent.change(input, { target: { files: [file] } });
    expect(screen.getByText("valid.csv")).toBeInTheDocument();
  });

  it("3. File selection rejects non-CSV files and displays error", () => {
    render(<BatchScreenerPage />);
    const file = new File(["smiles\nCCO"], "invalid.txt", { type: "text/plain" });
    const input = document.querySelector("input[type='file']") as HTMLInputElement;
    
    fireEvent.change(input, { target: { files: [file] } });
    expect(screen.getByText(/Invalid file type/i)).toBeInTheDocument();
    expect(screen.queryByText("invalid.txt")).not.toBeInTheDocument();
  });

  it("4. Loading state appears during file upload/analysis requests", async () => {
    let resolveFetch: any;
    const fetchPromise = new Promise((resolve) => {
      resolveFetch = resolve;
    });
    vi.stubGlobal("fetch", () => fetchPromise);

    render(<BatchScreenerPage />);
    const file = new File(["smiles\nCCO"], "valid.csv", { type: "text/csv" });
    const input = document.querySelector("input[type='file']") as HTMLInputElement;
    fireEvent.change(input, { target: { files: [file] } });

    const runBtn = screen.getByRole("button", { name: /Analyze Batch Library/i });
    fireEvent.click(runBtn);

    expect(screen.getByText("Analyzing descriptors and scoring batch model...")).toBeInTheDocument();

    // Clean up promise resolution
    resolveFetch({
      ok: true,
      json: async () => MOCK_BATCH_RESPONSE,
    });
  });

  it("5. Successful results render summary statistics card values", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      json: async () => MOCK_BATCH_RESPONSE,
    }));

    render(<BatchScreenerPage />);
    const file = new File(["smiles\nCCO"], "valid.csv", { type: "text/csv" });
    const input = document.querySelector("input[type='file']") as HTMLInputElement;
    fireEvent.change(input, { target: { files: [file] } });
    fireEvent.click(screen.getByRole("button", { name: /Analyze Batch Library/i }));

    await waitFor(() => {
      expect(screen.getByText("Total Rows")).toBeInTheDocument();
    });

    const metricValues = Array.from(document.querySelectorAll(".metric-num")).map(
      (el) => el.textContent
    );
    expect(metricValues).toEqual(["6", "4", "2", "3", "1"]);
  });

  it("6. Row level predictions and error details are rendered in results list", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      json: async () => MOCK_BATCH_RESPONSE,
    }));

    render(<BatchScreenerPage />);
    const file = new File(["smiles\nCCO"], "valid.csv", { type: "text/csv" });
    const input = document.querySelector("input[type='file']") as HTMLInputElement;
    fireEvent.change(input, { target: { files: [file] } });
    fireEvent.click(screen.getByRole("button", { name: /Analyze Batch Library/i }));

    await waitFor(() => {
      // Table SMILES rendering
      expect(screen.getByText("CN1C(=O)N(C)c2ncn(C)c2C1=O")).toBeInTheDocument();
      expect(screen.getByText("NOT_A_SMILES")).toBeInTheDocument();
      
      // Badges
      expect(screen.getAllByText("BBB+").length).toBeGreaterThan(0);
      expect(screen.getAllByText("Error").length).toBeGreaterThan(0);
    });

    // Expand details check for invalid row
    const toggleBtns = screen.getAllByRole("button", { name: "Toggle details" });
    fireEvent.click(toggleBtns[2]); // NOT_A_SMILES row details (row 3, index 2)

    await waitFor(() => {
      expect(screen.getByText("Invalid or malformed SMILES string: 'NOT_A_SMILES'.")).toBeInTheDocument();
    });
  });

  it("7. Filters separate row results without changing baseline summary counts", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      json: async () => MOCK_BATCH_RESPONSE,
    }));

    render(<BatchScreenerPage />);
    const file = new File(["smiles\nCCO"], "valid.csv", { type: "text/csv" });
    const input = document.querySelector("input[type='file']") as HTMLInputElement;
    fireEvent.change(input, { target: { files: [file] } });
    fireEvent.click(screen.getByRole("button", { name: /Analyze Batch Library/i }));

    await waitFor(() => {
      expect(screen.getByText("CN1C(=O)N(C)c2ncn(C)c2C1=O")).toBeInTheDocument();
      expect(screen.getByText("CC(=O)Nc1ccc(O)cc1")).toBeInTheDocument();
    });

    // Filter to errors only
    const errorsBtn = screen.getByRole("button", { name: "errors" });
    fireEvent.click(errorsBtn);

    // Caffeine and Paracetamol should be hidden
    expect(screen.queryByText("CN1C(=O)N(C)c2ncn(C)c2C1=O")).not.toBeInTheDocument();
    expect(screen.queryByText("CC(=O)Nc1ccc(O)cc1")).not.toBeInTheDocument();
    // Errors should still show
    expect(screen.getByText("NOT_A_SMILES")).toBeInTheDocument();
    expect(screen.getByText("CCO.O")).toBeInTheDocument();

    // Summary counts remain completely static!
    expect(screen.getByText("Total Rows")).toBeInTheDocument();
    expect(screen.getAllByText("6")[0]).toBeInTheDocument(); // still 6!
    expect(screen.getByText("Valid Predictions")).toBeInTheDocument();
    expect(screen.getAllByText("4")[0]).toBeInTheDocument(); // still 4!
  });

  it("7b. Clicking the probability column header sorts rows by BBB+ probability, errors last", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: true,
      json: async () => MOCK_BATCH_RESPONSE,
    }));

    render(<BatchScreenerPage />);
    const file = new File(["smiles\nCCO"], "valid.csv", { type: "text/csv" });
    const input = document.querySelector("input[type='file']") as HTMLInputElement;
    fireEvent.change(input, { target: { files: [file] } });
    fireEvent.click(screen.getByRole("button", { name: /Analyze Batch Library/i }));

    await waitFor(() => {
      expect(screen.getByText("CN1C(=O)N(C)c2ncn(C)c2C1=O")).toBeInTheDocument();
    });

    // First click sorts descending by BBB+ probability (highest first)
    fireEvent.click(screen.getByText("BBB+ Probability"));

    const bodyRows = document.querySelectorAll("tbody > tr:not([style*='display: none'])");
    const smilesInOrder = Array.from(bodyRows)
      .map((r) => r.querySelector("td:nth-child(2)")?.textContent)
      .filter(Boolean);

    // Ibuprofen (0.7920) > Caffeine (0.7899) > Aspirin (0.6856) > Paracetamol (0.4501) > errors
    expect(smilesInOrder).toEqual([
      "CC(C)Cc1ccc(cc1)C(C)C(=O)O",
      "CN1C(=O)N(C)c2ncn(C)c2C1=O",
      "CC(=O)Oc1ccccc1C(=O)O",
      "CC(=O)Nc1ccc(O)cc1",
      "NOT_A_SMILES",
      "CCO.O",
    ]);
  });

  it("8. API error handling displays backend error detail correctly", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: false,
      status: 400,
      json: async () => ({ detail: "File size exceeds the 5 MB limit." }),
    }));

    render(<BatchScreenerPage />);
    const file = new File(["smiles\nCCO"], "valid.csv", { type: "text/csv" });
    const input = document.querySelector("input[type='file']") as HTMLInputElement;
    fireEvent.change(input, { target: { files: [file] } });
    fireEvent.click(screen.getByRole("button", { name: /Analyze Batch Library/i }));

    await waitFor(() => {
      expect(screen.getByText("File size exceeds the 5 MB limit.")).toBeInTheDocument();
    });
  });
});

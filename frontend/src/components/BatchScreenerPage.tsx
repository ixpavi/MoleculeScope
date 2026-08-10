import React, { useState, useRef } from "react";
import { Upload, Download, Search, AlertCircle, RefreshCw, ChevronDown, ChevronUp, ArrowUpDown, ArrowUp, ArrowDown } from "lucide-react";

interface DescriptorSchema {
  "Molecular Weight": number;
  "LogP": number;
  "TPSA": number;
  "H-Bond Donors": number;
  "H-Bond Acceptors": number;
  "Rotatable Bonds": number;
  "Ring Count": number;
  "Aromatic Ring Count": number;
  "Heavy Atom Count": number;
  "Fraction CSP3": number;
  "Formal Charge": number;
}

interface BatchRow {
  row_index: number;
  input_smiles: string;
  status: "success" | "error";
  error: string | null;
  prediction: "BBB+" | "BBB-" | null;
  probability_bbb_plus: number | null;
  probability_bbb_minus: number | null;
  canonical_smiles: string | null;
  molecular_formula: string | null;
  descriptors: DescriptorSchema | null;
  extra_columns: Record<string, string>;
}

interface BatchSummary {
  filename: string;
  total_rows: number;
  processed_rows: number;
  failed_rows: number;
  bbb_plus_count: number;
  bbb_minus_count: number;
}

interface BatchResponse {
  summary: BatchSummary;
  results: BatchRow[];
}

export const BatchScreenerPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<BatchResponse | null>(null);

  // Table filters & pagination state
  const [search, setSearch] = useState("");
  const [filterType, setFilterType] = useState<"all" | "bbb_plus" | "bbb_minus" | "errors">("all");
  const [currentPage, setCurrentPage] = useState(1);
  const [expandedRows, setExpandedRows] = useState<Record<number, boolean>>({});

  type SortColumn = "row_index" | "probability_bbb_plus" | "molecular_weight" | "logp";
  const [sortColumn, setSortColumn] = useState<SortColumn>("row_index");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc");

  const handleSort = (column: SortColumn) => {
    if (sortColumn === column) {
      setSortDirection((d) => (d === "asc" ? "desc" : "asc"));
    } else {
      setSortColumn(column);
      setSortDirection(column === "row_index" ? "asc" : "desc");
    }
    setCurrentPage(1);
  };

  const getSortIcon = (column: SortColumn) => {
    if (sortColumn !== column) return <ArrowUpDown size={12} style={{ opacity: 0.4 }} />;
    return sortDirection === "asc" ? <ArrowUp size={12} /> : <ArrowDown size={12} />;
  };

  const fileInputRef = useRef<HTMLInputElement>(null);
  const pageSize = 10;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setError(null);
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (selectedFile.name.substring(selectedFile.name.lastIndexOf(".")) !== ".csv") {
        setError("Invalid file type. Please select a valid CSV file (.csv).");
        setFile(null);
        return;
      }
      if (selectedFile.size > 5 * 1024 * 1024) {
        setError("File size exceeds the 5 MB limit. Please select a smaller CSV file.");
        setFile(null);
        return;
      }
      setFile(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError(null);
    setData(null);
    setCurrentPage(1);
    setExpandedRows({});

    const formData = new FormData();
    formData.append("file", file);

    const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "";
    const endpoint = `${apiBaseUrl}/api/predict/batch`;

    try {
      const response = await fetch(endpoint, {
        method: "POST",
        body: formData,
      });

      const json = await response.json();

      if (!response.ok) {
        setError(json.detail || "Failed to process the batch file.");
      } else {
        setData(json);
      }
    } catch (err) {
      setError("Unable to connect to the MoleculeScope backend. Please ensure the FastAPI server is running.");
    } finally {
      setLoading(false);
    }
  };

  const downloadTemplate = () => {
    const csvContent =
      "SMILES,Compound_ID\n" +
      "CN1C(=O)N(C)c2ncn(C)c2C1=O,Caffeine\n" +
      "CC(=O)Oc1ccccc1C(=O)O,Aspirin\n" +
      "CC(C)Cc1ccc(cc1)C(C)C(=O)O,Ibuprofen\n" +
      "CC(=O)Nc1ccc(O)cc1,Paracetamol\n" +
      "NOT_A_SMILES,InvalidMolecule\n" +
      "CCO.O,MixtureStructure\n";

    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "moleculescope_template.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const handleExport = () => {
    if (!data || !data.results.length) return;

    // Collect all unique extra column headers
    const extraHeaders = new Set<string>();
    data.results.forEach((row) => {
      Object.keys(row.extra_columns).forEach((k) => extraHeaders.add(k));
    });
    const extraHeadersArr = Array.from(extraHeaders);

    const descriptorNames = [
      "Molecular Weight",
      "LogP",
      "TPSA",
      "H-Bond Donors",
      "H-Bond Acceptors",
      "Rotatable Bonds",
      "Ring Count",
      "Aromatic Ring Count",
      "Heavy Atom Count",
      "Fraction CSP3",
      "Formal Charge",
    ];

    // CSV header row
    const headers = [
      "row_index",
      "input_smiles",
      "canonical_smiles",
      "status",
      "error_message",
      "prediction",
      "probability_bbb_plus",
      "probability_bbb_minus",
      "molecular_formula",
      ...descriptorNames,
      ...extraHeadersArr,
    ];

    const csvRows = [headers.join(",")];

    data.results.forEach((row) => {
      const escape = (val: any) => {
        if (val === null || val === undefined) return "";
        let str = String(val);
        // Neutralize CSV formula injection: a cell starting with =, +, -, @, or a tab/CR
        // can be interpreted as a formula by Excel/Sheets when the exported file is
        // reopened. Prefixing a single quote forces those apps to treat it as plain text.
        // Values here originate from user-uploaded CSVs (input_smiles, extra_columns), so
        // this must be neutralized even though this app itself never executes them.
        if (/^[=+\-@\t\r]/.test(str)) {
          str = `'${str}`;
        }
        if (str.includes(",") || str.includes('"') || str.includes("\n")) {
          return `"${str.replace(/"/g, '""')}"`;
        }
        return str;
      };

      const rowData = [
        row.row_index,
        escape(row.input_smiles),
        escape(row.canonical_smiles),
        row.status,
        escape(row.error),
        escape(row.prediction),
        row.probability_bbb_plus !== null ? row.probability_bbb_plus.toFixed(6) : "",
        row.probability_bbb_minus !== null ? row.probability_bbb_minus.toFixed(6) : "",
        escape(row.molecular_formula),
      ];

      // Add descriptors
      descriptorNames.forEach((dName) => {
        if (row.descriptors) {
          const val = row.descriptors[dName as keyof DescriptorSchema];
          rowData.push(val !== undefined && val !== null ? String(val) : "");
        } else {
          rowData.push("");
        }
      });

      // Add extra columns
      extraHeadersArr.forEach((h) => {
        rowData.push(escape(row.extra_columns[h]));
      });

      csvRows.push(rowData.join(","));
    });

    const blob = new Blob([csvRows.join("\n")], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", "moleculescope_batch_results.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const toggleRow = (index: number) => {
    setExpandedRows((prev) => ({ ...prev, [index]: !prev[index] }));
  };

  // Get matching filtered data
  const getFilteredResults = (): BatchRow[] => {
    if (!data) return [];
    return data.results.filter((row) => {
      // 1. Filter type
      if (filterType === "bbb_plus" && row.prediction !== "BBB+") return false;
      if (filterType === "bbb_minus" && row.prediction !== "BBB-") return false;
      if (filterType === "errors" && row.status !== "error") return false;

      // 2. Search query
      if (search) {
        const query = search.toLowerCase();
        const matchesSmiles = row.input_smiles.toLowerCase().includes(query);
        const matchesExtra = Object.values(row.extra_columns).some((val) =>
          val.toLowerCase().includes(query)
        );
        return matchesSmiles || matchesExtra;
      }

      return true;
    });
  };

  const getSortValue = (row: BatchRow, column: SortColumn): number | null => {
    switch (column) {
      case "row_index":
        return row.row_index;
      case "probability_bbb_plus":
        return row.probability_bbb_plus;
      case "molecular_weight":
        return row.descriptors ? row.descriptors["Molecular Weight"] : null;
      case "logp":
        return row.descriptors ? row.descriptors["LogP"] : null;
    }
  };

  const sortRows = (rows: BatchRow[]): BatchRow[] => {
    const sorted = [...rows].sort((a, b) => {
      const va = getSortValue(a, sortColumn);
      const vb = getSortValue(b, sortColumn);
      // Rows with no value (errors) always sort to the end, regardless of direction.
      if (va === null && vb === null) return 0;
      if (va === null) return 1;
      if (vb === null) return -1;
      return sortDirection === "asc" ? va - vb : vb - va;
    });
    return sorted;
  };

  const filtered = getFilteredResults();
  const sorted = sortRows(filtered);
  const totalPages = Math.ceil(sorted.length / pageSize);
  const paginated = sorted.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  return (
    <div className="page-shell" style={{ display: "flex", flexDirection: "column", gap: "1.5rem" }}>
      <div>
        <h1 className="page-title">Batch Screening & Screenings Export</h1>
        <p className="page-description">
          Upload a CSV molecular library to perform high-throughput blood-brain barrier permeability predictions.
        </p>
      </div>

      {error && (
        <div className="alert alert-error" role="alert">
          <AlertCircle className="alert-icon" size={20} style={{ flexShrink: 0 }} />
          <div>{error}</div>
        </div>
      )}

      {/* Upload card container */}
      {!data && !loading && (
        <div className="card">
          <h2 className="card-title">Upload Chemical Library</h2>
          <div
            className="smiles-textarea"
            style={{
              border: "2px dashed var(--border-color)",
              borderRadius: "18px",
              padding: "3rem 1.5rem",
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              gap: "1rem",
              cursor: "pointer",
              textAlign: "center",
              backgroundColor: "var(--bg-inset)",
            }}
            onClick={() => fileInputRef.current?.click()}
          >
            <Upload size={40} style={{ color: "var(--color-primary)" }} />
            <div>
              <p style={{ fontWeight: 600, fontSize: "1rem" }}>
                {file ? file.name : "Drag & drop CSV file or click to browse"}
              </p>
              <p style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginTop: "0.25rem" }}>
                Limit: 5 MB file size, 5,000 data rows. Must contain a case-insensitive 'smiles' column.
              </p>
            </div>
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileChange}
              accept=".csv"
              style={{ display: "none" }}
            />
          </div>

          <div style={{ display: "flex", justifyContent: "space-between", gap: "1rem", marginTop: "1.5rem", flexWrap: "wrap" }}>
            <button type="button" className="example-btn" onClick={downloadTemplate}>
              <Download size={14} style={{ marginRight: "0.25rem" }} />
              Download Sample CSV Template
            </button>
            <button
              type="button"
              className="predict-btn"
              disabled={!file}
              onClick={handleUpload}
              style={{ margin: 0 }}
            >
              Analyze Batch Library
            </button>
          </div>
        </div>
      )}

      {/* Loading active progress spinner */}
      {loading && (
        <div className="card loading-container" style={{ display: "flex", flexDirection: "column", gap: "1rem", padding: "3rem" }}>
          <RefreshCw className="spinner" size={32} style={{ color: "var(--color-primary)" }} />
          <span style={{ fontSize: "1.1rem", fontWeight: 600 }}>Analyzing descriptors and scoring batch model...</span>
        </div>
      )}

      {/* Summary statistics & paginated table */}
      {data && !loading && (
        <>
          {/* Summary statistic cards (represent entire upload batch, untouched by filters) */}
          <div className="metrics-summary-grid" style={{ gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))" }}>
            <div className="metric-stat-card">
              <div className="metric-label">Total Rows</div>
              <div className="metric-num" style={{ color: "var(--text-main)" }}>{data.summary.total_rows}</div>
            </div>
            <div className="metric-stat-card">
              <div className="metric-label">Valid Predictions</div>
              <div className="metric-num" style={{ color: "var(--color-success)" }}>{data.summary.processed_rows}</div>
            </div>
            <div className="metric-stat-card">
              <div className="metric-label">Row Errors</div>
              <div className="metric-num" style={{ color: "var(--color-bbb-minus)" }}>{data.summary.failed_rows}</div>
            </div>
            <div className="metric-stat-card">
              <div className="metric-label">BBB+ Permeable</div>
              <div className="metric-num" style={{ color: "var(--color-bbb-plus)" }}>{data.summary.bbb_plus_count}</div>
            </div>
            <div className="metric-stat-card">
              <div className="metric-label">BBB- Impermeable</div>
              <div className="metric-num" style={{ color: "var(--color-bbb-minus)" }}>{data.summary.bbb_minus_count}</div>
            </div>
          </div>

          {/* Filtering and Actions toolbar */}
          <div className="card" style={{ padding: "1.25rem" }}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: "1.25rem", flexWrap: "wrap" }}>
              {/* Filter Buttons */}
              <div style={{ display: "flex", gap: "0.5rem" }}>
                {(["all", "bbb_plus", "bbb_minus", "errors"] as const).map((t) => (
                  <button
                    key={t}
                    onClick={() => {
                      setFilterType(t);
                      setCurrentPage(1);
                    }}
                    className={`example-btn ${filterType === t ? "active" : ""}`}
                    style={{
                      padding: "0.4rem 0.75rem",
                      fontSize: "0.8rem",
                      textTransform: "capitalize",
                    }}
                  >
                    {t === "bbb_plus" ? "BBB+" : t === "bbb_minus" ? "BBB-" : t}
                  </button>
                ))}
              </div>

              {/* Search and export actions */}
              <div style={{ display: "flex", gap: "0.75rem", flexGrow: 1, justifyContent: "flex-end", flexWrap: "wrap" }}>
                <div style={{ position: "relative", maxWidth: "250px", width: "100%" }}>
                  <Search
                    size={14}
                    style={{
                      position: "absolute",
                      left: "0.75rem",
                      top: "50%",
                      transform: "translateY(-50%)",
                      color: "var(--text-muted)",
                    }}
                  />
                  <input
                    type="text"
                    placeholder="Search SMILES or ID..."
                    value={search}
                    onChange={(e) => {
                      setSearch(e.target.value);
                      setCurrentPage(1);
                    }}
                    style={{
                      width: "100%",
                      padding: "0.4rem 0.75rem 0.4rem 2rem",
                      fontSize: "0.8rem",
                      backgroundColor: "var(--bg-inset)",
                      border: "1px solid var(--border-color)",
                      borderRadius: "12px",
                      outline: "none",
                    }}
                  />
                </div>

                <button
                  type="button"
                  className="predict-btn"
                  onClick={handleExport}
                  style={{ margin: 0, padding: "0.4rem 0.75rem", fontSize: "0.8rem", height: "fit-content" }}
                >
                  <Download size={14} style={{ marginRight: "0.25rem" }} />
                  Export Results CSV
                </button>

                <button
                  type="button"
                  className="example-btn"
                  onClick={() => {
                    setData(null);
                    setFile(null);
                  }}
                  style={{ padding: "0.4rem 0.75rem", fontSize: "0.8rem" }}
                >
                  Clear Screener
                </button>
              </div>
            </div>

            {/* Results counts */}
            <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginTop: "1rem" }}>
              Showing {filtered.length} of {data.results.length} total rows
            </div>

            {/* Paginated results table layout */}
            <div className="table-container" style={{ marginTop: "1rem" }}>
              {paginated.length > 0 ? (
                <table className="scientific-table">
                  <thead>
                    <tr>
                      <th
                        style={{ width: "60px", cursor: "pointer", userSelect: "none" }}
                        onClick={() => handleSort("row_index")}
                      >
                        <span style={{ display: "inline-flex", alignItems: "center", gap: "0.25rem" }}>
                          Row {getSortIcon("row_index")}
                        </span>
                      </th>
                      <th>Input SMILES</th>
                      <th style={{ width: "120px" }}>Prediction</th>
                      <th
                        style={{ width: "140px", cursor: "pointer", userSelect: "none" }}
                        onClick={() => handleSort("probability_bbb_plus")}
                      >
                        <span style={{ display: "inline-flex", alignItems: "center", gap: "0.25rem" }}>
                          BBB+ Probability {getSortIcon("probability_bbb_plus")}
                        </span>
                      </th>
                      <th
                        style={{ width: "100px", cursor: "pointer", userSelect: "none" }}
                        onClick={() => handleSort("molecular_weight")}
                      >
                        <span style={{ display: "inline-flex", alignItems: "center", gap: "0.25rem" }}>
                          MW {getSortIcon("molecular_weight")}
                        </span>
                      </th>
                      <th
                        style={{ width: "80px", cursor: "pointer", userSelect: "none" }}
                        onClick={() => handleSort("logp")}
                      >
                        <span style={{ display: "inline-flex", alignItems: "center", gap: "0.25rem" }}>
                          LogP {getSortIcon("logp")}
                        </span>
                      </th>
                      <th style={{ width: "60px" }}>Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    {paginated.map((row) => {
                      const isExpanded = !!expandedRows[row.row_index];
                      const hasError = row.status === "error";

                      return (
                        <React.Fragment key={row.row_index}>
                          <tr>
                            <td>{row.row_index}</td>
                            <td
                              style={{
                                maxWidth: "250px",
                                textOverflow: "ellipsis",
                                overflow: "hidden",
                                whiteSpace: "nowrap",
                              }}
                              title={row.input_smiles}
                            >
                              {row.input_smiles}
                            </td>
                            <td>
                              {hasError ? (
                                <span className="badge-bbb bbb-minus" style={{ padding: "0.2rem 0.4rem", fontSize: "0.7rem" }}>
                                  Error
                                </span>
                              ) : (
                                <span
                                  className={`badge-bbb ${row.prediction === "BBB+" ? "bbb-plus" : "bbb-minus"}`}
                                  style={{ padding: "0.2rem 0.4rem", fontSize: "0.7rem" }}
                                >
                                  {row.prediction}
                                </span>
                              )}
                            </td>
                            <td>
                              {hasError || row.probability_bbb_plus === null
                                ? "-"
                                : `${(row.probability_bbb_plus * 100).toFixed(2)}%`}
                            </td>
                            <td>{row.descriptors ? row.descriptors["Molecular Weight"].toFixed(2) : "-"}</td>
                            <td>{row.descriptors ? row.descriptors["LogP"].toFixed(2) : "-"}</td>
                            <td>
                              <button
                                type="button"
                                className="copy-btn"
                                onClick={() => toggleRow(row.row_index)}
                                style={{ padding: "0.25rem", borderRadius: "8px" }}
                                title="Toggle details"
                              >
                                {isExpanded ? <ChevronUp size={16} /> : <ChevronDown size={16} />}
                              </button>
                            </td>
                          </tr>

                          {/* Expanded detail section */}
                          {isExpanded && (
                            <tr>
                              <td colSpan={7} style={{ backgroundColor: "var(--bg-inset)", padding: "1.25rem" }}>
                                {hasError ? (
                                  <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", color: "var(--color-bbb-minus)" }}>
                                    <AlertCircle size={16} />
                                    <span>{row.error}</span>
                                  </div>
                                ) : (
                                  <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                                    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
                                      <div>
                                        <strong style={{ display: "block", fontSize: "0.8rem", color: "var(--text-muted)" }}>
                                          Canonical SMILES
                                        </strong>
                                        <span style={{ fontSize: "0.85rem", wordBreak: "break-all" }}>{row.canonical_smiles}</span>
                                      </div>
                                      <div>
                                        <strong style={{ display: "block", fontSize: "0.8rem", color: "var(--text-muted)" }}>
                                          Molecular Formula
                                        </strong>
                                        <span style={{ fontSize: "0.85rem" }}>{row.molecular_formula}</span>
                                      </div>
                                    </div>

                                    {/* Descriptors Detail grid */}
                                    <div>
                                      <strong style={{ display: "block", fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "0.4rem" }}>
                                        Full Computed Physicochemical Descriptors
                                      </strong>
                                      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: "0.5rem" }}>
                                        {row.descriptors &&
                                          Object.entries(row.descriptors).map(([dName, dVal]) => (
                                            <div
                                              key={dName}
                                              style={{
                                                padding: "0.4rem",
                                                border: "1px solid var(--border-color)",
                                                borderRadius: "10px",
                                                backgroundColor: "var(--bg-inset)",
                                                display: "flex",
                                                justifyContent: "space-between",
                                                fontSize: "0.75rem",
                                              }}
                                            >
                                              <span style={{ color: "var(--text-muted)" }}>{dName}</span>
                                              <span style={{ fontWeight: 600 }}>{dVal.toFixed(dName.includes("Weight") || dName.includes("CSP3") ? 3 : 2)}</span>
                                            </div>
                                          ))}
                                      </div>
                                    </div>

                                    {/* Extra columns preservation details */}
                                    {Object.keys(row.extra_columns).length > 0 && (
                                      <div>
                                        <strong style={{ display: "block", fontSize: "0.8rem", color: "var(--text-muted)", marginBottom: "0.4rem" }}>
                                          Preserved Metadata Columns
                                        </strong>
                                        <div style={{ display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                                          {Object.entries(row.extra_columns).map(([colName, colVal]) => (
                                            <div
                                              key={colName}
                                              style={{
                                                padding: "0.4rem 0.6rem",
                                                backgroundColor: "var(--color-primary-soft)",
                                                border: "1px solid var(--border-color)",
                                                borderRadius: "10px",
                                                fontSize: "0.75rem",
                                              }}
                                            >
                                              <strong style={{ color: "var(--color-primary)" }}>{colName}:</strong>{" "}
                                              <span>{colVal}</span>
                                            </div>
                                          ))}
                                        </div>
                                      </div>
                                    )}
                                  </div>
                                )}
                              </td>
                            </tr>
                          )}
                        </React.Fragment>
                      );
                    })}
                  </tbody>
                </table>
              ) : (
                <div style={{ textAlign: "center", padding: "2rem", color: "var(--text-muted)" }}>
                  No matching row results found in this screen list.
                </div>
              )}
            </div>

            {/* Pagination Controls */}
            {totalPages > 1 && (
              <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: "1rem", marginTop: "1.25rem" }}>
                <button
                  type="button"
                  className="example-btn"
                  disabled={currentPage === 1}
                  onClick={() => setCurrentPage((c) => Math.max(c - 1, 1))}
                  style={{ padding: "0.3rem 0.6rem", fontSize: "0.8rem" }}
                >
                  Previous
                </button>
                <span style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>
                  Page {currentPage} of {totalPages}
                </span>
                <button
                  type="button"
                  className="example-btn"
                  disabled={currentPage === totalPages}
                  onClick={() => setCurrentPage((c) => Math.min(c + 1, totalPages))}
                  style={{ padding: "0.3rem 0.6rem", fontSize: "0.8rem" }}
                >
                  Next
                </button>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
};

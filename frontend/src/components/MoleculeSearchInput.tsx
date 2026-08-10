import React, { useEffect, useRef, useState } from "react";
import { Search, AlertTriangle, BadgeCheck, ShieldAlert } from "lucide-react";

interface MoleculeSearchResult {
  name: string;
  smiles: string;
  verified: boolean;
  group_consistent: boolean | null;
}

interface MoleculeSearchInputProps {
  onSelect: (smiles: string, name: string) => void;
  disabled: boolean;
  compact?: boolean;
  /** Minimal chrome: no label, no footer warning, no border — for embedding inside an existing bordered field. */
  bare?: boolean;
  placeholder?: string;
}

export const MoleculeSearchInput: React.FC<MoleculeSearchInputProps> = ({ onSelect, disabled, compact = false, bare = false, placeholder }) => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<MoleculeSearchResult[]>([]);
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const requestSeqRef = useRef(0);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (abortRef.current) abortRef.current.abort();

    const trimmed = query.trim();
    setActiveIndex(-1);
    if (trimmed.length < 2) {
      setResults([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    const thisRequestId = ++requestSeqRef.current;

    debounceRef.current = setTimeout(() => {
      const controller = new AbortController();
      abortRef.current = controller;

      const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
      fetch(`${apiBaseUrl}/api/molecules/search?q=${encodeURIComponent(trimmed)}&limit=15`, {
        signal: controller.signal,
      })
        .then((res) => (res.ok ? res.json() : { results: [] }))
        .then((data) => {
          // Ignore responses from requests that have since been superseded by newer input.
          if (thisRequestId !== requestSeqRef.current) return;
          setResults(Array.isArray(data?.results) ? data.results : []);
          setOpen(true);
        })
        .catch((err) => {
          if (err?.name === "AbortError") return;
          if (thisRequestId !== requestSeqRef.current) return;
          setResults([]);
        })
        .finally(() => {
          if (thisRequestId === requestSeqRef.current) setLoading(false);
        });
    }, 300);

    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [query]);

  const handleSelect = (result: MoleculeSearchResult) => {
    onSelect(result.smiles, result.name);
    setQuery(result.name);
    setOpen(false);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!open || results.length === 0) return;

    if (e.key === "ArrowDown") {
      e.preventDefault();
      setActiveIndex((prev) => (prev + 1) % results.length);
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActiveIndex((prev) => (prev <= 0 ? results.length - 1 : prev - 1));
    } else if (e.key === "Enter") {
      if (activeIndex >= 0 && activeIndex < results.length) {
        e.preventDefault();
        handleSelect(results[activeIndex]);
      }
    } else if (e.key === "Escape") {
      setOpen(false);
    }
  };

  const listboxId = "molecule-search-listbox";

  return (
    <div style={{ position: "relative" }}>
      {!compact && !bare && (
        <label htmlFor="molecule-search" style={{ fontSize: "0.85rem", color: "var(--text-muted)", fontWeight: 500 }}>
          Or search by compound name
        </label>
      )}
      <div
        className={compact ? "search" : undefined}
        style={
          compact
            ? { width: "100%" }
            : bare
              ? { display: "flex", alignItems: "center", gap: "8px" }
              : { position: "relative", marginTop: "0.4rem" }
        }
      >
        <Search
          size={compact ? 14 : 15}
          style={
            compact || bare
              ? { flexShrink: 0, color: bare ? "var(--dim2)" : undefined }
              : { position: "absolute", left: "0.75rem", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }
          }
        />
        <input
          id="molecule-search"
          type="text"
          role="combobox"
          aria-expanded={open}
          aria-controls={listboxId}
          aria-autocomplete="list"
          aria-activedescendant={activeIndex >= 0 ? `${listboxId}-option-${activeIndex}` : undefined}
          value={query}
          disabled={disabled}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => results.length > 0 && setOpen(true)}
          onBlur={() => setTimeout(() => setOpen(false), 150)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder || "e.g. ibuprofen, morphine, nitrofurantoin..."}
          style={
            compact
              ? undefined
              : bare
                ? {
                    width: "100%",
                    background: "transparent",
                    border: 0,
                    outline: 0,
                    color: "var(--text)",
                    fontFamily: "var(--f-mono)",
                    fontSize: "14.5px",
                    padding: "6px 0 0",
                  }
                : {
                    width: "100%",
                    padding: "0.6rem 0.75rem 0.6rem 2.25rem",
                    fontSize: "0.9rem",
                    backgroundColor: "var(--bg-inset)",
                    border: "1px solid var(--border-color)",
                    borderRadius: "12px",
                    outline: "none",
                    color: "inherit",
                  }
          }
        />
      </div>

      {open && query.trim().length >= 2 && (
        <div
          id={listboxId}
          role="listbox"
          style={{
            position: "absolute",
            zIndex: 10,
            top: "100%",
            left: 0,
            right: 0,
            marginTop: "0.5rem",
            backgroundColor: "var(--bg-card)",
            border: "1px solid var(--border-color)",
            borderRadius: "16px",
            maxHeight: "280px",
            overflowY: "auto",
            boxShadow: "0 14px 32px rgba(0, 0, 0, .35)",
            padding: "6px",
          }}
        >
          {loading && (
            <div style={{ padding: "0.6rem 0.75rem", fontSize: "0.8rem", color: "var(--text-muted)" }}>Searching...</div>
          )}

          {!loading && results.length === 0 && (
            <div style={{ padding: "0.6rem 0.75rem", fontSize: "0.8rem", color: "var(--text-muted)" }}>
              No matches in the B3DB dataset for "{query.trim()}". Not every common drug name is present — try a SMILES string instead.
            </div>
          )}

          {!loading &&
            results.map((r, idx) => (
              <button
                key={`${r.name}-${r.smiles}-${idx}`}
                id={`${listboxId}-option-${idx}`}
                role="option"
                aria-selected={idx === activeIndex}
                type="button"
                onMouseDown={(e) => e.preventDefault()}
                onMouseEnter={() => setActiveIndex(idx)}
                onClick={() => handleSelect(r)}
                style={{
                  display: "block",
                  width: "100%",
                  textAlign: "left",
                  padding: "0.5rem 0.75rem",
                  background: idx === activeIndex ? "var(--color-primary-soft)" : "none",
                  border: "none",
                  borderRadius: "10px",
                  cursor: "pointer",
                  color: "inherit",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: "0.35rem" }}>
                  <span style={{ fontSize: "0.85rem", fontWeight: 600, textTransform: "capitalize" }}>{r.name}</span>
                  {r.verified && (
                    <span
                      title="Hand-verified against a known reference structure"
                      style={{ display: "inline-flex", alignItems: "center", gap: "0.2rem", fontSize: "0.65rem", fontWeight: 700, color: "var(--color-bbb-plus)", textTransform: "uppercase" }}
                    >
                      <BadgeCheck size={12} /> Verified
                    </span>
                  )}
                  {r.group_consistent === false && (
                    <span
                      title="Other entries share this exact name but have a very different structure — this one may be a data error in the source dataset. Check the rendered structure carefully."
                      style={{ display: "inline-flex", alignItems: "center", gap: "0.2rem", fontSize: "0.65rem", fontWeight: 700, color: "var(--color-bbb-minus)", textTransform: "uppercase" }}
                    >
                      <ShieldAlert size={12} /> Differs from others
                    </span>
                  )}
                </div>
                <div style={{ fontSize: "0.7rem", color: "var(--text-muted)", fontFamily: "monospace", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {r.smiles}
                </div>
              </button>
            ))}
        </div>
      )}

      {!compact && !bare && (
        <div style={{ display: "flex", gap: "0.4rem", alignItems: "flex-start", marginTop: "0.5rem", fontSize: "0.72rem", color: "var(--text-muted)" }}>
          <AlertTriangle size={13} style={{ flexShrink: 0, marginTop: "0.1rem" }} />
          <span>
            Names come directly from the B3DB source dataset and aren't independently verified — always check the
            rendered structure after selecting before trusting it.
          </span>
        </div>
      )}
    </div>
  );
};

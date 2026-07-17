import {React, useEffect, useState, useRef} from "react";
import apiBook from "../apiBook";

function SearchablePaginatedDropdown({
  inputRef,
  apiUrl,
  value,
  onChange,
  pageSize = 2,
  resetTrigger,
  defaultSearchText,
  
}) {
  const [search, setSearch] = useState(defaultSearchText || "");
  const [inputValue, setInputValue] = useState(defaultSearchText || "");
  const [selectedText, setSelectedText] = useState(defaultSearchText || "");
  const [options, setOptions] = useState([]);
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [showOptions, setShowOptions] = useState(false);
  const wrapperRef = useRef(null);

  const fetchOptions = async (searchTerm, pageNumber) => {
    setLoading(true);
    try {
      const response = await apiBook.get(apiUrl, {
        params: {
          search: searchTerm || "",   // allow empty search
          page: pageNumber,
          page_size: pageSize,
        },
      });
      setOptions(response.data.results || []);
      setTotalCount(response.data.count || 0);
    } catch (error) {
      console.error("Failed to fetch options", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setSearch("");
    setInputValue("");
  }, [resetTrigger]);

  useEffect(() => {
    setInputValue(defaultSearchText || "");
    setSearch(defaultSearchText || "");
    setSelectedText(defaultSearchText || "");
  }, [defaultSearchText]);

  useEffect(() => {
    if (showOptions) {
      fetchOptions(search, page);
    }
  }, [search, page, showOptions]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setShowOptions(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const totalPages = Math.ceil(totalCount / pageSize);

  const handleOptionClick = (option) => {
    onChange(option);
    const label = value === "staff" ? option.display_name : option.company_name;
    setInputValue(label);
    setSelectedText(label);
    setShowOptions(false);
  };

  const handleSearchClick = () => {
    setSearch(inputValue);
    setPage(1);
    setShowOptions(true);
  };

  const handleFocus = () => {
    // Clear box and load full staff list
    setInputValue("");
    setSearch(""); // triggers empty search
    setPage(1);
    setShowOptions(true);
  };

  const handleBlur = (event) => {
    const relatedTarget =
      event.relatedTarget || event.nativeEvent.relatedTarget;
    if (
      wrapperRef.current &&
      relatedTarget &&
      wrapperRef.current.contains(relatedTarget)
    ) {
      return;
    }
    setShowOptions(false);
    if (!search || search.trim() === "" || search !== selectedText) {
      setInputValue(selectedText);
    }
  };

  return (
    <div ref={wrapperRef} style={{ position: "relative", width: 300 }}>
      <div style={{ display: "flex", gap: 4 }}>
        <input
          ref={inputRef}
          type="text"
          placeholder="Search..."
          value={inputValue || ""}
          onChange={(e) => setInputValue(e.target.value)}
          onFocus={handleFocus}
          onBlur={handleBlur}
          style={{ flex: 1, boxSizing: "border-box", padding: 8 }}
        />
        <button type="button" onClick={handleSearchClick}>Search</button>
      </div>

      {showOptions && (
        <div
          style={{
            position: "absolute",
            background: "white",
            border: "1px solid #ccc",
            width: "100%",
            maxHeight: 200,
            overflowY: "auto",
            zIndex: 1000,
          }}
        >
          {loading && <div style={{ padding: 8 }}>Loading...</div>}
          {!loading && options.length === 0 && (
            <div style={{ padding: 8 }}>No results found</div>
          )}
          {!loading &&
            options.map((opt) =>
              value === "staff" ? (
                <div
                  key={opt.staff_id}
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => handleOptionClick(opt)}
                  style={{ padding: 8, cursor: "pointer" }}
                >
                  {opt.display_name}
                </div>
              ) : (
                <div
                  key={opt.id}
                  onMouseDown={(e) => e.preventDefault()}
                  onClick={() => handleOptionClick(opt)}
                  style={{ padding: 8, cursor: "pointer" }}
                >
                  {opt.company_name}
                </div>
              )
            )}
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              padding: 8,
              borderTop: "1px solid #ccc",
            }}
          >
            <button
              onClick={() => setPage(Math.max(page - 1, 1))}
              disabled={page === 1 || loading}
            >
              Previous
            </button>
            <span>
              Page {page} / {totalPages || 1}
            </span>
            <button
              onClick={() => setPage(Math.min(page + 1, totalPages))}
              disabled={page === totalPages || loading}
            >
              Next
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default SearchablePaginatedDropdown;

import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiRequest } from '../../api/client';
import ProductCard from '../../components/ProductCard/ProductCard';
import '../../styles/Search.css';

const CATEGORIES = [
  { label: 'All', value: '' },
  { label: 'Tops', value: 'top' },
  { label: 'Bottoms', value: 'bottom' },
  { label: 'Dresses', value: 'dress' },
  { label: 'Footwear', value: 'footwear' },
  { label: 'Accessories', value: 'accessory' },
];

const SORT_OPTIONS = [
  { label: 'Relevance', value: 'relevance' },
  { label: 'Price: Low', value: 'price_asc' },
  { label: 'Price: High', value: 'price_desc' },
  { label: 'DNA Match', value: 'dna' },
];

export default function Search() {
  const navigate = useNavigate();
  const [query, setQuery] = useState('');
  const [category, setCategory] = useState('');
  const [sortBy, setSortBy] = useState('relevance');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [searched, setSearched] = useState(false);

  const doSearch = useCallback(async (q, cat) => {
    setLoading(true);
    setSearched(true);
    try {
      const params = new URLSearchParams({ limit: '50' });
      if (q.trim()) params.set('q', q.trim());
      if (cat) params.set('category', cat);

      const data = await apiRequest(`/api/products?${params.toString()}`);
      setResults(data);
    } catch {
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, []);

  // Debounced search on query change
  useEffect(() => {
    if (!query.trim() && !category) return;
    const timer = setTimeout(() => doSearch(query, category), 400);
    return () => clearTimeout(timer);
  }, [query, category, doSearch]);

  // Sort results
  const sortedResults = [...results].sort((a, b) => {
    if (sortBy === 'price_asc') return a.price - b.price;
    if (sortBy === 'price_desc') return b.price - a.price;
    if (sortBy === 'dna') {
      return (b.confidence?.overall || 70) - (a.confidence?.overall || 70);
    }
    return 0;
  });

  return (
    <div className="screen search-screen">
      {/* Header */}
      <div className="srch-hdr">
        <div className="srch-back-row">
          <div className="back-btn" onClick={() => navigate(-1)}>←</div>
          <div className="srch-input-wrap">
            <span className="srch-icon">🔍</span>
            <input
              className="srch-input"
              type="text"
              autoFocus
              placeholder="Search brands, occasions, styles…"
              value={query}
              onChange={e => setQuery(e.target.value)}
            />
            {query && (
              <button className="srch-clear" onClick={() => { setQuery(''); setResults([]); setSearched(false); }}>
                ×
              </button>
            )}
          </div>
        </div>

        {/* Category chips */}
        <div className="srch-cats">
          {CATEGORIES.map(c => (
            <button
              key={c.value}
              className={`srch-cat-chip ${category === c.value ? 'active' : ''}`}
              onClick={() => setCategory(c.value)}
            >
              {c.label}
            </button>
          ))}
        </div>
      </div>

      <div className="srch-body">
        {!searched && !loading && (
          <div className="srch-hint">
            <div className="srch-hint-icon">🔍</div>
            <div className="srch-hint-title">Search anything</div>
            <div className="srch-hint-sub">Try "minimalist tee", "night out", or a brand name</div>

            {/* Quick suggestions */}
            <div className="srch-suggestions">
              {['Oversized', 'Cargo pants', 'Blazer', 'Night out', 'Campus'].map(s => (
                <button
                  key={s}
                  className="srch-suggestion"
                  onClick={() => setQuery(s)}
                >
                  🔥 {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {loading && (
          <div className="srch-loading">
            <div className="srch-spinner">🔍</div>
            <div>Searching {query}…</div>
          </div>
        )}

        {searched && !loading && (
          <>
            <div className="srch-results-hdr">
              <div className="srch-count">
                {sortedResults.length === 0
                  ? 'No results found'
                  : `${sortedResults.length} results${query ? ` for "${query}"` : ''}`}
              </div>
              <select
                className="srch-sort"
                value={sortBy}
                onChange={e => setSortBy(e.target.value)}
              >
                {SORT_OPTIONS.map(o => (
                  <option key={o.value} value={o.value}>{o.label}</option>
                ))}
              </select>
            </div>

            {sortedResults.length === 0 ? (
              <div className="srch-empty">
                <div style={{ fontSize: 40 }}>😶</div>
                <div style={{ fontWeight: 700, marginBottom: 6 }}>No matches found</div>
                <div style={{ fontSize: 12, color: 'var(--text-2)' }}>Try a different keyword or category</div>
                <button className="wl-browse-btn" style={{ marginTop: 16 }} onClick={() => { setQuery(''); setCategory(''); setSearched(false); }}>
                  Clear Search
                </button>
              </div>
            ) : (
              <div className="prod-grid">
                {sortedResults.map(p => (
                  <ProductCard key={p.id} product={p} />
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

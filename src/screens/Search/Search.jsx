import {
  useCallback,
  useEffect,
  useState,
} from 'react';
import {
  ArrowLeft,
  Flame,
  Search as SearchIcon,
  X,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

import { apiRequest } from '../../api/client';
import ProductCard from '../../components/ProductCard/ProductCard';
import CartIconButton from '../../components/CartIconButton/CartIconButton';
import '../../styles/Search.css';


const CATEGORIES = [
  {
    label: 'All',
    value: '',
  },
  {
    label: 'Tops',
    value: 'top',
  },
  {
    label: 'Bottoms',
    value: 'bottom',
  },
  {
    label: 'Dresses',
    value: 'dress',
  },
  {
    label: 'Footwear',
    value: 'footwear',
  },
  {
    label: 'Accessories',
    value: 'accessory',
  },
];


const SORT_OPTIONS = [
  {
    label: 'Relevance',
    value: 'relevance',
  },
  {
    label: 'Price: Low',
    value: 'price_asc',
  },
  {
    label: 'Price: High',
    value: 'price_desc',
  },
  {
    label: 'DNA Match',
    value: 'dna',
  },
];


const QUICK_SUGGESTIONS = [
  'Oversized',
  'Cargo pants',
  'Blazer',
  'Night out',
  'Campus',
];


export default function Search() {
  const navigate = useNavigate();

  const [query, setQuery] =
    useState('');

  const [category, setCategory] =
    useState('');

  const [sortBy, setSortBy] =
    useState('relevance');

  const [results, setResults] =
    useState([]);

  const [loading, setLoading] =
    useState(false);

  const [searched, setSearched] =
    useState(false);


  const doSearch = useCallback(
    async (searchQuery, selectedCategory) => {
      setLoading(true);
      setSearched(true);

      try {
        const params = new URLSearchParams({
          limit: '50',
        });

        if (searchQuery.trim()) {
          params.set(
            'q',
            searchQuery.trim(),
          );
        }

        if (selectedCategory) {
          params.set(
            'category',
            selectedCategory,
          );
        }

        const data = await apiRequest(
          `/api/products?${params.toString()}`,
        );

        setResults(
          Array.isArray(data)
            ? data
            : [],
        );
      } catch (error) {
        console.error(
          'Product search failed:',
          error,
        );

        setResults([]);
      } finally {
        setLoading(false);
      }
    },
    [],
  );


  useEffect(() => {
    if (
      !query.trim()
      && !category
    ) {
      return undefined;
    }

    const timer = window.setTimeout(
      () => {
        void doSearch(
          query,
          category,
        );
      },
      400,
    );

    return () => {
      window.clearTimeout(timer);
    };
  }, [
    query,
    category,
    doSearch,
  ]);


  const sortedResults = [
    ...results,
  ].sort((first, second) => {
    if (sortBy === 'price_asc') {
      return (
        Number(first.price)
        - Number(second.price)
      );
    }

    if (sortBy === 'price_desc') {
      return (
        Number(second.price)
        - Number(first.price)
      );
    }

    if (sortBy === 'dna') {
      return (
        Number(
          second.confidence?.overall
          ?? 70,
        )
        - Number(
          first.confidence?.overall
          ?? 70,
        )
      );
    }

    return 0;
  });


  function clearSearch() {
    setQuery('');
    setCategory('');
    setResults([]);
    setSearched(false);
  }


  return (
    <div className="screen search-screen">
      <header className="srch-hdr">
        <div className="srch-back-row">
          <button
            type="button"
            className="back-btn"
            aria-label="Go back"
            onClick={() => {
              navigate(-1);
            }}
          >
            <ArrowLeft
              aria-hidden="true"
              size={21}
            />
          </button>

          <div className="srch-input-wrap">
            <SearchIcon
              className="srch-icon"
              aria-hidden="true"
              size={18}
            />

            <input
              className="srch-input"
              type="search"
              autoFocus
              aria-label="Search products"
              placeholder={
                'Search brands, occasions, '
                + 'styles…'
              }
              value={query}
              onChange={(event) => {
                setQuery(
                  event.target.value,
                );
              }}
            />

            {query && (
              <button
                type="button"
                className="srch-clear"
                aria-label="Clear search text"
                onClick={() => {
                  setQuery('');
                  setResults([]);
                  setSearched(false);
                }}
              >
                <X
                  aria-hidden="true"
                  size={18}
                />
              </button>
            )}
          </div>
          <CartIconButton className="back-btn" style={{ background: 'transparent', marginLeft: '8px' }} />
        </div>

        <div
          className="srch-cats"
          aria-label="Product categories"
        >
          {CATEGORIES.map(
            (categoryOption) => {
              const isSelected =
                category
                === categoryOption.value;

              return (
                <button
                  type="button"
                  key={categoryOption.value}
                  className={`srch-cat-chip ${
                    isSelected
                      ? 'active'
                      : ''
                  }`}
                  aria-pressed={isSelected}
                  onClick={() => {
                    setCategory(
                      categoryOption.value,
                    );
                  }}
                >
                  {categoryOption.label}
                </button>
              );
            },
          )}
        </div>
      </header>

      <div className="srch-body">
        {!searched && !loading && (
          <section className="srch-hint">
            <div
              className="srch-hint-icon"
              aria-hidden="true"
            >
              <SearchIcon size={40} />
            </div>

            <h1 className="srch-hint-title">
              Search anything
            </h1>

            <p className="srch-hint-sub">
              Try &quot;minimalist tee&quot;,
              &quot;night out&quot;, or a brand
              name.
            </p>

            <div className="srch-suggestions">
              {QUICK_SUGGESTIONS.map(
                (suggestion) => (
                  <button
                    type="button"
                    key={suggestion}
                    className="srch-suggestion"
                    onClick={() => {
                      setQuery(suggestion);
                    }}
                  >
                    <Flame
                      aria-hidden="true"
                      size={16}
                    />

                    <span>
                      {suggestion}
                    </span>
                  </button>
                ),
              )}
            </div>
          </section>
        )}

        {loading && (
          <div
            className="srch-loading"
            role="status"
            aria-live="polite"
          >
            <div
              className="srch-spinner"
              aria-hidden="true"
            >
              <SearchIcon size={25} />
            </div>

            <div>
              Searching {query}…
            </div>
          </div>
        )}

        {searched && !loading && (
          <>
            <div className="srch-results-hdr">
              <div
                className="srch-count"
                aria-live="polite"
              >
                {sortedResults.length === 0
                  ? 'No results found'
                  : (
                    `${sortedResults.length} `
                    + 'results'
                    + (
                      query
                        ? ` for "${query}"`
                        : ''
                    )
                  )}
              </div>

              <select
                className="srch-sort"
                aria-label="Sort search results"
                value={sortBy}
                onChange={(event) => {
                  setSortBy(
                    event.target.value,
                  );
                }}
              >
                {SORT_OPTIONS.map(
                  (option) => (
                    <option
                      key={option.value}
                      value={option.value}
                    >
                      {option.label}
                    </option>
                  ),
                )}
              </select>
            </div>

            {sortedResults.length === 0 ? (
              <section className="srch-empty">
                <div
                  className="srch-empty-icon"
                  aria-hidden="true"
                >
                  <SearchIcon size={40} />
                </div>

                <h2 className="srch-empty-title">
                  No matches found
                </h2>

                <p className="srch-empty-message">
                  Try a different keyword or
                  category.
                </p>

                <button
                  type="button"
                  className="wl-browse-btn"
                  onClick={clearSearch}
                >
                  Clear Search
                </button>
              </section>
            ) : (
              <div className="prod-grid">
                {sortedResults.map(
                  (product) => (
                    <ProductCard
                      key={product.id}
                      product={product}
                    />
                  ),
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}

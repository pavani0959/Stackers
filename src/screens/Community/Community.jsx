import {
  useEffect,
  useMemo,
  useState,
} from 'react';

import { apiRequest } from '../../api/client';
import BottomNav from '../../components/BottomNav/BottomNav';
import { useUser } from '../../context/useUser';
import '../../styles/Community.css';
import {
  Sparkles,
  Users,
  Dna,
  X,
} from 'lucide-react';


function percentage(value) {
  const parsed = Number(value);

  if (!Number.isFinite(parsed)) {
    return '0';
  }

  return Number.isInteger(parsed)
    ? String(parsed)
    : parsed.toFixed(2);
}


export default function Community() {
  const {
    user,
    updateUser,
  } = useUser();

  const [twinResponse, setTwinResponse] =
    useState({
      dataset: null,
      threshold: 70,
      twins: [],
    });

  const [profiles, setProfiles] =
    useState([]);

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState(null);

  const [selectedCreator, setSelectedCreator] =
    useState(null);

  const [blendValue, setBlendValue] =
    useState(25);

  const [blending, setBlending] =
    useState(false);

  const [toast, setToast] =
    useState('');


  useEffect(() => {
    let cancelled = false;

    async function loadCommunity() {
      setLoading(true);
      setError(null);

      try {
        /*
         * The Style Twin request is a server-owned
         * GET. The frontend submits no Fashion DNA
         * or user_profile.
         */
        const [
          twinsData,
          profileData,
        ] = await Promise.all([
          apiRequest('/api/community/twins'),
          apiRequest(
            '/api/community/profiles',
          ),
        ]);

        if (cancelled) {
          return;
        }

        setTwinResponse({
          dataset:
            twinsData.dataset ?? null,

          threshold:
            twinsData.threshold ?? 70,

          twins:
            Array.isArray(
              twinsData.twins,
            )
              ? twinsData.twins
              : [],
        });

        setProfiles(
          Array.isArray(profileData)
            ? profileData
            : [],
        );
      } catch (requestError) {
        if (!cancelled) {
          setError(
            requestError,
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    void loadCommunity();

    return () => {
      cancelled = true;
    };
  }, []);


  const creators = useMemo(
    () => (
      profiles.filter((profile) => {
        const normalizedRole =
          String(profile.role ?? '')
            .trim()
            .toLowerCase();

        return (
          normalizedRole === 'creator'
        );
      })
    ),
    [profiles],
  );


  const communityMembers = useMemo(
    () => (
      profiles.filter((profile) => {
        const normalizedRole =
          String(profile.role ?? '')
            .trim()
            .toLowerCase();

        return (
          normalizedRole === 'community'
        );
      })
    ),
    [profiles],
  );


  function showToast(message) {
    setToast(message);

    window.setTimeout(
      () => setToast(''),
      2500,
    );
  }


  async function handleBlend() {
    if (!selectedCreator) {
      return;
    }

    setBlending(true);

    try {
      const data = await apiRequest(
        '/api/dna/blend',
        {
          method: 'POST',
          body: JSON.stringify({
            user_profile: user,
            creator_dna:
              selectedCreator.dna,
            blend_percentage:
              blendValue,
          }),
        },
      );

      updateUser({
        dna: data.merged_dna,
      });

      showToast(
        `Blended ${blendValue}% of `
        + `${selectedCreator.name}'s style.`,
      );

      setSelectedCreator(null);
    } catch (blendError) {
      console.error(
        'Creator blend failed:',
        blendError,
      );

      showToast(
        'Creator blend could not be completed.',
      );
    } finally {
      setBlending(false);
    }
  }


  if (loading) {
    return (
      <main className="community-screen">
        <div className="community-state">
          Loading Style Twins…
        </div>
      </main>
    );
  }


  if (error) {
    return (
      <main className="community-screen">
        <div className="community-state error">
          <h1>
            Community could not be loaded
          </h1>

          <p>
            {error.message}
          </p>
        </div>

        <BottomNav />
      </main>
    );
  }


  return (
    <main className="community-screen">
      <header className="community-header">
        <div className="community-eyebrow">
          STYLE COMMUNITY ✦
          <span className="community-sparkles-dec">
            ✨
          </span>
        </div>

        <h1>Style Twins</h1>

        <p>
          Seeded demo users with at least a {percentage(twinResponse.threshold)}% weighted style match.
        </p>
      </header>

      <section className="dataset-notice">
        <div className="dataset-notice-left">
          <div className="dataset-icon">
            <Sparkles size={16} fill="currentColor" />
          </div>
          <strong>
            {twinResponse.dataset?.label ?? 'Insights use a seeded demo cohort'}
          </strong>
        </div>

        <span>
          Dataset: {twinResponse.dataset?.type ?? 'seeded_demo'}
        </span>
      </section>

      <section className="community-section">
        <div className="community-section-heading">
          <div>
            <p className="community-section-kicker">EVIDENCE-BACKED MATCHES ✦</p>
            <h2>Your Style Twins</h2>
          </div>
          <span className="community-count">{twinResponse.twins.length}</span>
        </div>

        {twinResponse.twins.length === 0 ? (
          <div className="community-empty">
            <div className="community-empty-icon"><Users size={20} /></div>
            <span>No seeded demo users currently meet the {percentage(twinResponse.threshold)}% threshold.</span>
          </div>
        ) : (
          <div className="profile-grid">
            {twinResponse.twins.map((twin) => (
              <article className="profile-card compact" key={twin.user_id}>
                <img
                  src={twin.avatar || '/catalog/fallback-product.webp'}
                  alt={twin.name}
                  onError={(event) => {
                    event.currentTarget.onerror = null;
                    event.currentTarget.src = '/catalog/fallback-product.webp';
                  }}
                />

                <div className="profile-info">
                  <h3>{twin.name}</h3>
                  <p>@{twin.name?.toLowerCase().replace(/\s+/g, '.') || `user${twin.user_id}`}</p>
                  <strong>{twin.shared_traits?.[0] || 'Similar Style'}</strong>
                </div>

                <div className="profile-badge">
                  <Users size={18} />
                </div>
              </article>
            ))}
          </div>
        )}
      </section>

      <section className="community-section">
        <div className="community-section-heading">
          <div>
            <p className="community-section-kicker">CREATOR DNA ✦</p>
            <h2>Creator Blends</h2>
          </div>
        </div>

        <div className="profile-grid">
          {creators.map((creator) => (
            <article className="profile-card" key={creator.id}>
              <div className="profile-card-top">
                <img
                  src={creator.avatar || '/catalog/fallback-product.webp'}
                  alt={creator.name}
                  onError={(event) => {
                    event.currentTarget.onerror = null;
                    event.currentTarget.src = '/catalog/fallback-product.webp';
                  }}
                />

                <div className="profile-info">
                  <h3>{creator.name}</h3>
                  <p>{creator.handle || `@${creator.name.toLowerCase().replace(/\s+/g, '.')}`}</p>
                  <strong>{creator.dna_label}</strong>
                </div>

                <div className="profile-badge-dna">
                  <Dna size={18} />
                </div>
              </div>

              <button
                type="button"
                className="community-primary-button"
                onClick={() => setSelectedCreator(creator)}
                style={{
                  background: creator.name.includes('Maya') 
                    ? 'linear-gradient(90deg, #ff416c 0%, #ff4b2b 100%)' 
                    : 'linear-gradient(90deg, #b06ab3 0%, #4568dc 100%)'
                }}
              >
                <Dna size={16} /> Blend DNA
              </button>
            </article>
          ))}
        </div>
      </section>

      {communityMembers.length > 0 && (
        <section className="community-section">
          <div className="community-section-heading">
            <div>
              <p className="community-section-kicker">COMMUNITY DISCOVERY ✦</p>
              <h2>Community Profiles</h2>
            </div>
          </div>

          <div className="profile-grid">
            {communityMembers.map((profile) => (
              <article className="profile-card compact" key={profile.id}>
                <img
                  src={profile.avatar || '/catalog/fallback-product.webp'}
                  alt={profile.name}
                  onError={(event) => {
                    event.currentTarget.onerror = null;
                    event.currentTarget.src = '/catalog/fallback-product.webp';
                  }}
                />

                <div className="profile-info">
                  <h3>{profile.name}</h3>
                  <p>{profile.handle || `@${profile.name.toLowerCase().replace(/\s+/g, '.')}`}</p>
                  <strong>{profile.dna_label}</strong>
                </div>

                <div className="profile-badge">
                  <Users size={18} />
                </div>
              </article>
            ))}
          </div>
        </section>
      )}

      {selectedCreator && (
        <div
          className="community-modal-overlay"
          role="presentation"
        >
          <section
            className="community-modal"
            role="dialog"
            aria-modal="true"
            aria-labelledby="blend-title"
          >
            <button
              type="button"
              className="community-modal-close"
              aria-label="Close creator blend"
              onClick={() => {
                setSelectedCreator(null);
              }}
            >
              <X
                aria-hidden="true"
                size={20}
              />
            </button>

            <p className="community-section-kicker">
              CREATOR DNA BLEND
            </p>

            <h2 id="blend-title">
              Blend with{' '}
              {selectedCreator.name}
            </h2>

            <label htmlFor="blend-percentage">
              Creator influence:{' '}
              <strong>
                {blendValue}%
              </strong>
            </label>

            <input
              id="blend-percentage"
              type="range"
              min="10"
              max="60"
              step="5"
              value={blendValue}
              onChange={(event) => {
                setBlendValue(
                  Number(
                    event.target.value,
                  ),
                );
              }}
            />

            <button
              type="button"
              className="community-primary-button"
              disabled={blending}
              onClick={handleBlend}
            >
              {blending
                ? 'Blending…'
                : 'Apply creator blend'}
            </button>
          </section>
        </div>
      )}

      {toast && (
        <div className="community-toast">
          {toast}
        </div>
      )}

      <BottomNav />
    </main>
  );
}

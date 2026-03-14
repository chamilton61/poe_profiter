import type { Profile } from '../types';
import { useProfileItems } from '../hooks/useProfileItems';
import Header from './Header';
import ItemRow from './ItemRow';
import './DetailsPage.css';

interface DetailsPageProps {
  profile: Profile;
  profiles: Profile[];
  league: string;
  poesessid: string | null;
  onNavigateOverview: () => void;
  onNavigateProfile: (profileId: string) => void;
  onSaveSessionId: (id: string) => void;
  onLeagueChange: (league: string) => void;
  onLogout: () => void;
}

export default function DetailsPage({
  profile,
  profiles,
  league,
  poesessid,
  onNavigateOverview,
  onNavigateProfile,
  onSaveSessionId,
  onLeagueChange,
  onLogout,
}: DetailsPageProps) {
  const { items, loading, error } = useProfileItems(profile, league, poesessid);

  return (
    <div className="details-page">
      <Header
        profiles={profiles}
        league={league}
        poesessid={poesessid}
        onNavigateOverview={onNavigateOverview}
        onNavigateProfile={onNavigateProfile}
        onSaveSessionId={onSaveSessionId}
        onLeagueChange={onLeagueChange}
        onLogout={onLogout}
      />
      <div className="main-content">
        <div className="details-back" onClick={onNavigateOverview}>
          ← Back to Overview
        </div>
        <div className="details-page-title">{profile.name}</div>
        <div className="details-layout">
          <div className="details-sidebar">
            <div className="info-card">
              <div className="info-card-title">Profile Description</div>
              <div className="description-text">{profile.description}</div>
            </div>
            <div className="info-card">
              <div className="info-card-title">Profit Thresholds</div>
              <div className="info-row">
                <span className="info-key">Max buy price</span>
                <span className="info-val green">{profile.maxProfitPrice}</span>
              </div>
              <div className="info-row">
                <span className="info-key">Method</span>
                <span className="info-val magic">{profile.gamblingMethod}</span>
              </div>
            </div>
            <div className="info-card">
              <div className="info-card-title">Related Materials</div>
              {profile.materials.map((m, i) => (
                <div key={i} className="material-row">
                  <span className="mat-name">{m.name}</span>
                  <span className="mat-price">{m.price}</span>
                </div>
              ))}
            </div>
            <div className="info-card">
              <div className="info-card-title">Notes</div>
              <div className="description-text notes-text">{profile.notes}</div>
            </div>
          </div>
          <div className="details-main">
            <div className="items-card">
              <div className="items-card-header profile-card-header">
                <div className="profile-name">Trade Hits</div>
                <div className="profile-badge">
                  <span className="live-dot" />
                  {loading ? 'loading…' : `${items.length} matching items`}
                </div>
              </div>
              <div className="profile-items">
                {loading && (
                  <div className="profile-status">Querying trade API…</div>
                )}
                {error && (
                  <div className="profile-status profile-error">{error}</div>
                )}
                {!loading &&
                  !error &&
                  items.map((item, i) => (
                    <ItemRow key={i} item={item} hasSession={!!poesessid} />
                  ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

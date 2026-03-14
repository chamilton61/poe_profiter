import type { Profile } from '../types';
import { useProfileItems } from '../hooks/useProfileItems';
import ItemRow from './ItemRow';
import './OverviewPage.css';

interface ProfileCardProps {
  profile: Profile;
  league: string;
  poesessid: string | null;
  onViewDetails: () => void;
}

export default function ProfileCard({
  profile,
  league,
  poesessid,
  onViewDetails,
}: ProfileCardProps) {
  const { items, loading, error } = useProfileItems(profile, league, poesessid);

  return (
    <div className="profile-card">
      <div className="profile-card-header">
        <div className="profile-name">{profile.name}</div>
        <div className="profile-badge">
          {loading ? 'loading…' : `${items.length} hits`}
        </div>
      </div>
      <div className="profile-items">
        {loading && <div className="profile-status">Querying trade API…</div>}
        {error && <div className="profile-status profile-error">{error}</div>}
        {!loading &&
          !error &&
          items
            .slice(0, 5)
            .map((item, i) => (
              <ItemRow key={i} item={item} hasSession={!!poesessid} />
            ))}
      </div>
      <div className="profile-footer">
        <button className="details-btn" onClick={onViewDetails}>
          View Details →
        </button>
      </div>
    </div>
  );
}

import type { Profile } from '../types';
import Header from './Header';
import ProfileCard from './ProfileCard';
import './OverviewPage.css';

interface OverviewPageProps {
  profiles: Profile[];
  league: string;
  poesessid: string | null;
  onNavigateProfile: (profileId: string) => void;
  onSaveSessionId: (id: string) => void;
  onLeagueChange: (league: string) => void;
  onLogout: () => void;
}

export default function OverviewPage({
  profiles,
  league,
  poesessid,
  onNavigateProfile,
  onSaveSessionId,
  onLeagueChange,
  onLogout,
}: OverviewPageProps) {
  return (
    <div className="overview-page">
      <Header
        profiles={profiles}
        league={league}
        poesessid={poesessid}
        onNavigateOverview={() => {}}
        onNavigateProfile={onNavigateProfile}
        onSaveSessionId={onSaveSessionId}
        onLeagueChange={onLeagueChange}
        onLogout={onLogout}
      />
      <div className="main-content">
        <div className="page-title">
          <span className="live-dot" />
          Search Profiles — Live
        </div>
        <div className="profiles-grid">
          {profiles.map((p) => (
            <ProfileCard
              key={p.id}
              profile={p}
              league={league}
              poesessid={poesessid}
              onViewDetails={() => onNavigateProfile(p.id)}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

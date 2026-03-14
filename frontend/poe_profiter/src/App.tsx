import { useState } from 'react';
import './App.css';
import { profiles } from './data/profiles';
import type { Page } from './types';
import LoginPage from './components/LoginPage';
import OverviewPage from './components/OverviewPage';
import DetailsPage from './components/DetailsPage';

export default function App() {
  const [page, setPage] = useState<Page>('login');
  const [poesessid, setPoesessid] = useState<string | null>(null);
  const [league, setLeague] = useState('Standard');
  const [currentProfileId, setCurrentProfileId] = useState<string | null>(null);

  function navigateOverview() {
    setPage('overview');
  }

  function navigateProfile(profileId: string) {
    setCurrentProfileId(profileId);
    setPage('details');
  }

  function handleLogin() {
    setPage('overview');
  }

  function handleLogout() {
    setPoesessid(null);
    setPage('login');
  }

  const currentProfile = profiles.find((p) => p.id === currentProfileId);

  if (page === 'login') {
    return <LoginPage onLogin={handleLogin} />;
  }

  if (page === 'details' && currentProfile) {
    return (
      <DetailsPage
        profile={currentProfile}
        profiles={profiles}
        league={league}
        poesessid={poesessid}
        onNavigateOverview={navigateOverview}
        onNavigateProfile={navigateProfile}
        onSaveSessionId={setPoesessid}
        onLeagueChange={setLeague}
        onLogout={handleLogout}
      />
    );
  }

  return (
    <OverviewPage
      profiles={profiles}
      league={league}
      poesessid={poesessid}
      onNavigateProfile={navigateProfile}
      onSaveSessionId={setPoesessid}
      onLeagueChange={setLeague}
      onLogout={handleLogout}
    />
  );
}

import { useEffect, useRef, useState } from 'react';
import type { Profile } from '../types';
import './Header.css';

interface HeaderProps {
  profiles: Profile[];
  league: string;
  poesessid: string | null;
  onNavigateOverview: () => void;
  onNavigateProfile: (profileId: string) => void;
  onSaveSessionId: (id: string) => void;
  onLeagueChange: (league: string) => void;
  onLogout: () => void;
}

export default function Header({
  profiles,
  league,
  poesessid,
  onNavigateOverview,
  onNavigateProfile,
  onSaveSessionId,
  onLeagueChange,
  onLogout,
}: HeaderProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const [sessionInput, setSessionInput] = useState(poesessid ?? '');
  const [leagueInput, setLeagueInput] = useState(league);
  const [saveConfirmed, setSaveConfirmed] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    setSessionInput(poesessid ?? '');
  }, [poesessid]);

  useEffect(() => {
    setLeagueInput(league);
  }, [league]);

  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setMenuOpen(false);
      }
    }
    document.addEventListener('click', handleClick);
    return () => document.removeEventListener('click', handleClick);
  }, []);

  function handleSave() {
    const sessid = sessionInput.trim();
    if (sessid) onSaveSessionId(sessid);
    const lg = leagueInput.trim();
    if (lg) onLeagueChange(lg);
    setSaveConfirmed(true);
    setTimeout(() => {
      setMenuOpen(false);
      setSaveConfirmed(false);
    }, 800);
  }

  function handleProfileNav(val: string) {
    if (val) onNavigateProfile(val);
  }

  return (
    <header className="site-header">
      <div className="site-title" onClick={onNavigateOverview}>
        PoE Profiter
      </div>
      <div className="header-right">
        <select
          className="nav-select"
          value=""
          onChange={(e) => handleProfileNav(e.target.value)}
        >
          <option value="">— Go to Profile —</option>
          {profiles.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
        <div className="settings-wrapper" ref={menuRef}>
          <button className="settings-btn" onClick={() => setMenuOpen((o) => !o)}>
            ⚙
          </button>
          <div className={`settings-menu ${menuOpen ? 'open' : ''}`}>
            <div className="settings-section">
              <div className="settings-label">League</div>
              <input
                className="settings-input"
                type="text"
                placeholder="e.g. Standard"
                value={leagueInput}
                onChange={(e) => setLeagueInput(e.target.value)}
              />
            </div>
            <div className="settings-section">
              <div className="settings-label">POESESSID</div>
              <input
                className="settings-input"
                type="text"
                placeholder="Paste session ID…"
                value={sessionInput}
                onChange={(e) => setSessionInput(e.target.value)}
              />
            </div>
            <div className="settings-section">
              <button className="settings-save-btn" onClick={handleSave}>
                Save Settings
              </button>
              {saveConfirmed && (
                <div className="session-status">✓ Settings saved</div>
              )}
            </div>
            <div className="settings-section">
              <button className="settings-logout-btn" onClick={onLogout}>
                Logout
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

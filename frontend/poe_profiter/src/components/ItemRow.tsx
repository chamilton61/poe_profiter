import { useState } from 'react';
import type { Item } from '../types';
import './ItemRow.css';

interface ItemRowProps {
  item: Item;
  hasSession: boolean;
}

function resolveIcon(icon: string): { isUrl: boolean; src: string } {
  if (icon.startsWith('http')) return { isUrl: true, src: icon };
  if (icon.startsWith('/')) {
    return { isUrl: true, src: `https://www.pathofexile.com${icon}` };
  }
  return { isUrl: false, src: icon };
}

export default function ItemRow({ item, hasSession }: ItemRowProps) {
  const [statsOpen, setStatsOpen] = useState(false);
  const [whisperCopied, setWhisperCopied] = useState(false);

  const rarityClass =
    item.rarity === 'unique' ? 'unique' : item.rarity === 'rare' ? 'rare' : '';
  const roiClass = item.roiSign > 0 ? 'positive' : 'negative';
  const { isUrl, src } = resolveIcon(item.icon);

  const canWhisper = !!item.whisper || hasSession;

  function handleWhisper(e: React.MouseEvent) {
    e.stopPropagation();
    if (item.whisper) {
      navigator.clipboard.writeText(item.whisper).catch(() => {});
      setWhisperCopied(true);
      setTimeout(() => setWhisperCopied(false), 1500);
    }
  }

  return (
    <div className="item-row" onClick={() => setStatsOpen((o) => !o)}>
      <div className="item-icon">
        {isUrl ? <img src={src} alt="" /> : src}
      </div>
      <div className="item-info">
        <div className={`item-name ${rarityClass}`}>{item.name}</div>
        <div className="item-stats-toggle">▸ stats</div>
        <div className={`item-stats ${statsOpen ? 'open' : ''}`}>
          <span>
            {item.stats.map((s, i) => (
              <div key={i}>• {s}</div>
            ))}
          </span>
        </div>
      </div>
      <div className="item-right">
        <div className="item-price">{item.cost}</div>
        <div className={`item-roi ${roiClass}`}>ROI {item.roi}</div>
        <button
          className={`whisper-btn ${canWhisper ? 'enabled' : 'disabled'}`}
          onClick={handleWhisper}
          disabled={!canWhisper}
        >
          {whisperCopied ? '✓ Copied' : '⚡ Whisper'}
        </button>
      </div>
    </div>
  );
}

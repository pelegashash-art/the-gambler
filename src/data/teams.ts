import type { Team } from '../lib/scoring'

// oddsProb: implied probability from typical 2026 WC winner odds (June 2025)
// historicalScore: avg round reached across WC 2010-2022 (1=winner, 2=finalist, 4=SF, 8=QF, 16=R16, 32=group)
export const TEAMS: Team[] = [
  { name: 'ברזיל', flag: '🇧🇷', fifaRank: 5, oddsProb: 0.16, historicalScore: 2.5, titles: 5 },
  { name: 'צרפת', flag: '🇫🇷', fifaRank: 2, oddsProb: 0.14, historicalScore: 3.0, titles: 2 },
  { name: 'אנגליה', flag: '🏴󠁧󠁢󠁥󠁮󠁧󠁿', fifaRank: 4, oddsProb: 0.11, historicalScore: 5.5, titles: 1 },
  { name: 'גרמניה', flag: '🇩🇪', fifaRank: 15, oddsProb: 0.10, historicalScore: 2.5, titles: 4 },
  { name: 'ספרד', flag: '🇪🇸', fifaRank: 3, oddsProb: 0.09, historicalScore: 3.5, titles: 1 },
  { name: 'ארגנטינה', flag: '🇦🇷', fifaRank: 1, oddsProb: 0.13, historicalScore: 2.0, titles: 3 },
  { name: 'פורטוגל', flag: '🇵🇹', fifaRank: 6, oddsProb: 0.06, historicalScore: 6.0, titles: 0 },
  { name: 'הולנד', flag: '🇳🇱', fifaRank: 7, oddsProb: 0.05, historicalScore: 4.0, titles: 0 },
  { name: 'בלגיה', flag: '🇧🇪', fifaRank: 9, oddsProb: 0.03, historicalScore: 5.0, titles: 0 },
  { name: 'אורוגוואי', flag: '🇺🇾', fifaRank: 16, oddsProb: 0.02, historicalScore: 5.5, titles: 2 },
  { name: 'קרואטיה', flag: '🇭🇷', fifaRank: 10, oddsProb: 0.02, historicalScore: 3.5, titles: 0 },
  { name: 'ארה"ב', flag: '🇺🇸', fifaRank: 16, oddsProb: 0.03, historicalScore: 8.0, titles: 0 },
  { name: 'מרוקו', flag: '🇲🇦', fifaRank: 14, oddsProb: 0.02, historicalScore: 7.0, titles: 0 },
  { name: 'יפן', flag: '🇯🇵', fifaRank: 18, oddsProb: 0.01, historicalScore: 8.5, titles: 0 },
  { name: 'מקסיקו', flag: '🇲🇽', fifaRank: 20, oddsProb: 0.01, historicalScore: 8.0, titles: 0 },
  { name: 'קולומביה', flag: '🇨🇴', fifaRank: 24, oddsProb: 0.01, historicalScore: 9.0, titles: 0 },
]

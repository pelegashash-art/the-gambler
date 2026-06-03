export interface Team {
  name: string
  flag: string
  fifaRank: number
  // Implied probability from betting odds (0-1)
  oddsProb: number
  // Average round reached in WC 2010-2022 (8=QF, 4=SF, 2=F, 1=W)
  historicalScore: number
  // titles won
  titles: number
}

/** Normalize FIFA rank: rank 1 → 100, rank 50 → ~50, rank 100+ → low */
function normalizeFifaRank(rank: number): number {
  return Math.max(0, 100 - (rank - 1) * 1.5)
}

/** Normalize historical WC performance to 0-100 */
function normalizeHistory(score: number): number {
  // score is avg round reached: 8=QF, 4=SF, 2=F, 1=W
  // Better = lower number. 1 = 100 pts, 8 = ~20 pts, 16+ = 0
  if (score >= 16) return 5
  return Math.round(100 - (score - 1) * (95 / 15))
}

export interface TeamScore {
  team: Team
  oddsScore: number
  fifaScore: number
  historyScore: number
  total: number
}

export function computeScores(teams: Team[]): TeamScore[] {
  return teams
    .map((team) => {
      const oddsScore = Math.round(team.oddsProb * 100)
      const fifaScore = Math.round(normalizeFifaRank(team.fifaRank))
      const historyScore = Math.round(normalizeHistory(team.historicalScore))
      const total = Math.round(oddsScore * 0.4 + fifaScore * 0.35 + historyScore * 0.25)
      return { team, oddsScore, fifaScore, historyScore, total }
    })
    .sort((a, b) => b.total - a.total)
}

/** Convert decimal odds to implied probability (0-1) */
export function decimalToProb(decimal: number): number {
  return 1 / decimal
}

/** Convert American odds to implied probability */
export function americanToProb(american: number): number {
  if (american > 0) return 100 / (american + 100)
  return Math.abs(american) / (Math.abs(american) + 100)
}

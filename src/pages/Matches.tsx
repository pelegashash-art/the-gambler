import { TEAMS } from '../data/teams'
import { computeScores } from '../lib/scoring'
import { useState } from 'react'

const scores = computeScores(TEAMS)
const teamMap = Object.fromEntries(scores.map((s) => [s.team.name, s]))

// Sample group stage fixtures — update as schedule is confirmed
const FIXTURES = [
  { home: 'ארגנטינה', away: 'מרוקו', group: 'A', homeOdds: 1.7, drawOdds: 3.8, awayOdds: 5.5 },
  { home: 'ברזיל', away: 'ארה"ב', group: 'B', homeOdds: 1.5, drawOdds: 4.2, awayOdds: 7.0 },
  { home: 'צרפת', away: 'יפן', group: 'C', homeOdds: 1.4, drawOdds: 4.5, awayOdds: 8.0 },
  { home: 'גרמניה', away: 'מקסיקו', group: 'D', homeOdds: 1.8, drawOdds: 3.6, awayOdds: 5.0 },
  { home: 'ספרד', away: 'קולומביה', group: 'E', homeOdds: 1.6, drawOdds: 3.9, awayOdds: 6.0 },
  { home: 'אנגליה', away: 'הולנד', group: 'F', homeOdds: 2.1, drawOdds: 3.3, awayOdds: 3.6 },
  { home: 'פורטוגל', away: 'בלגיה', group: 'G', homeOdds: 2.0, drawOdds: 3.4, awayOdds: 3.8 },
  { home: 'קרואטיה', away: 'אורוגוואי', group: 'H', homeOdds: 2.4, drawOdds: 3.2, awayOdds: 3.0 },
]

function Recommendation({
  homeOdds,
  drawOdds,
  awayOdds,
  homeName,
  awayName,
  homeFifaRank,
  awayFifaRank,
  homeTotal,
  awayTotal,
}: {
  homeOdds: number
  drawOdds: number
  awayOdds: number
  homeName: string
  awayName: string
  homeFifaRank: number
  awayFifaRank: number
  homeTotal: number
  awayTotal: number
}) {
  const homeProb = 1 / homeOdds
  const drawProb = 1 / drawOdds
  const awayProb = 1 / awayOdds

  const rankAdv = awayFifaRank - homeFifaRank // positive = home better ranked
  const scoreAdv = homeTotal - awayTotal

  let rec = '1'
  let confidence = 'בינונית'
  let color = 'text-blue-400'

  if (scoreAdv > 15 || (homeProb > 0.5 && rankAdv > 10)) {
    rec = '1'
    confidence = 'גבוהה'
    color = 'text-emerald-400'
  } else if (scoreAdv < -15 || (awayProb > 0.5 && rankAdv < -10)) {
    rec = '2'
    confidence = 'גבוהה'
    color = 'text-emerald-400'
  } else if (Math.abs(scoreAdv) < 8) {
    rec = 'X'
    confidence = 'נמוכה'
    color = 'text-yellow-400'
  } else if (scoreAdv > 0) {
    rec = '1'
    confidence = 'בינונית'
    color = 'text-blue-400'
  } else {
    rec = '2'
    confidence = 'בינונית'
    color = 'text-blue-400'
  }

  const recLabel = rec === '1' ? homeName : rec === '2' ? awayName : 'תיקו'

  return (
    <div className="mt-4 bg-slate-900/50 rounded-lg p-3 border border-slate-700">
      <div className="flex items-center justify-between">
        <div>
          <span className="text-slate-400 text-xs">המלצה: </span>
          <span className={`font-bold ${color}`}>{rec} — {recLabel}</span>
        </div>
        <div className="text-xs text-slate-400">
          ביטחון: <span className={color}>{confidence}</span>
        </div>
      </div>
      <div className="mt-2 flex gap-3 text-xs text-slate-400">
        <span>אודס: {homeProb.toFixed(0)}% / {(drawProb * 100).toFixed(0)}% / {(awayProb * 100).toFixed(0)}%</span>
        <span>הפרש FIFA: {Math.abs(rankAdv)} דרוגים</span>
      </div>
    </div>
  )
}

export default function Matches() {
  const [open, setOpen] = useState<number | null>(null)

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">⚽ ניתוח משחקים</h2>
        <p className="text-slate-400 mt-1">לחץ על משחק לניתוח מפורט</p>
      </div>

      <div className="space-y-3">
        {FIXTURES.map((f, i) => {
          const home = teamMap[f.home]
          const away = teamMap[f.away]
          const isOpen = open === i

          return (
            <div
              key={i}
              className="bg-slate-800 rounded-xl border border-slate-700 overflow-hidden"
            >
              <button
                className="w-full p-4 text-right hover:bg-slate-700/30 transition-colors"
                onClick={() => setOpen(isOpen ? null : i)}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3 text-lg font-medium">
                    <span>{home?.team.flag ?? '🏳️'}</span>
                    <span>{f.home}</span>
                    <span className="text-slate-500 text-sm">vs</span>
                    <span>{f.away}</span>
                    <span>{away?.team.flag ?? '🏳️'}</span>
                  </div>
                  <div className="flex items-center gap-4">
                    <span className="text-xs text-slate-500 bg-slate-700 px-2 py-1 rounded">
                      בית {f.group}
                    </span>
                    <span className="text-slate-400">{isOpen ? '▲' : '▼'}</span>
                  </div>
                </div>

                <div className="mt-2 flex gap-4 text-sm text-slate-400">
                  <span>1: <strong className="text-white">x{f.homeOdds}</strong></span>
                  <span>X: <strong className="text-white">x{f.drawOdds}</strong></span>
                  <span>2: <strong className="text-white">x{f.awayOdds}</strong></span>
                </div>
              </button>

              {isOpen && home && away && (
                <div className="border-t border-slate-700 p-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="space-y-2">
                      <h4 className="font-semibold text-slate-300">{f.home}</h4>
                      <div className="text-slate-400">דירוג FIFA: <span className="text-white">#{home.team.fifaRank}</span></div>
                      <div className="text-slate-400">ציון כולל: <span className="text-emerald-400 font-bold">{home.total}</span></div>
                      <div className="text-slate-400">אליפויות: <span className="text-yellow-400">{'🏆'.repeat(home.team.titles) || '—'}</span></div>
                    </div>
                    <div className="space-y-2 text-left">
                      <h4 className="font-semibold text-slate-300">{f.away}</h4>
                      <div className="text-slate-400">דירוג FIFA: <span className="text-white">#{away.team.fifaRank}</span></div>
                      <div className="text-slate-400">ציון כולל: <span className="text-emerald-400 font-bold">{away.total}</span></div>
                      <div className="text-slate-400">אליפויות: <span className="text-yellow-400">{'🏆'.repeat(away.team.titles) || '—'}</span></div>
                    </div>
                  </div>

                  <Recommendation
                    homeOdds={f.homeOdds}
                    drawOdds={f.drawOdds}
                    awayOdds={f.awayOdds}
                    homeName={f.home}
                    awayName={f.away}
                    homeFifaRank={home.team.fifaRank}
                    awayFifaRank={away.team.fifaRank}
                    homeTotal={home.total}
                    awayTotal={away.total}
                  />
                </div>
              )}
            </div>
          )
        })}
      </div>

      <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700 text-sm text-slate-400">
        <strong className="text-slate-200">✏️ לעדכון משחקים:</strong> ערוך את המערך{' '}
        <code className="bg-slate-700 px-1 rounded">FIXTURES</code> ב-{' '}
        <code className="bg-slate-700 px-1 rounded">src/pages/Matches.tsx</code> עם אודס עדכניים.
      </div>
    </div>
  )
}

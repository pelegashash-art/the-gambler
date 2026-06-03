import candidates from '../data/golden-boot-candidates.json'

interface Candidate {
  name: string
  country: string
  flag: string
  club: string
  age: number
  decimalOdds: number
  avgGoalsPerWC: number
  prevWCGoals: number[]
  note: string
}

function valueBetScore(c: Candidate): number {
  // Higher = better value: low odds (= high prob) + good historical output
  const impliedProb = 1 / c.decimalOdds
  const histFactor = Math.min(c.avgGoalsPerWC / 6, 1)
  return Math.round((impliedProb * 0.6 + histFactor * 0.4) * 100)
}

const sorted = [...(candidates as Candidate[])].sort(
  (a, b) => valueBetScore(b) - valueBetScore(a)
)

export default function GoldenBoot() {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-white">👟 גביע הזהב — מלך השערים</h2>
        <p className="text-slate-400 mt-1">מיון לפי "value bet": אודס נמוך + היסטוריה טובה</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {sorted.map((c, i) => {
          const prob = Math.round((1 / c.decimalOdds) * 100)
          const value = valueBetScore(c)
          return (
            <div
              key={c.name}
              className={`bg-slate-800 rounded-xl p-4 border transition-colors ${
                i === 0 ? 'border-emerald-500' : 'border-slate-700'
              }`}
            >
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{i === 0 ? '⭐' : c.flag}</span>
                  <div>
                    <h3 className="font-bold text-white">{c.name}</h3>
                    <p className="text-slate-400 text-xs">
                      {c.flag} {c.country} · {c.club} · גיל {c.age}
                    </p>
                  </div>
                </div>
                <div className="text-left">
                  <div className="text-emerald-400 font-bold text-lg">x{c.decimalOdds}</div>
                  <div className="text-slate-400 text-xs">{prob}% סיכוי</div>
                </div>
              </div>

              <div className="mt-3 flex items-center gap-4 text-sm">
                <div>
                  <span className="text-slate-400">גולים קודמים: </span>
                  <span className="text-white">
                    {c.prevWCGoals.length > 0 ? c.prevWCGoals.join(', ') : '—'}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400">ממוצע: </span>
                  <span className="text-white">{c.avgGoalsPerWC} ⚽</span>
                </div>
              </div>

              <p className="mt-2 text-xs text-slate-400 border-t border-slate-700 pt-2">{c.note}</p>

              <div className="mt-3 flex items-center gap-2">
                <span className="text-xs text-slate-500">Value score:</span>
                <div className="flex-1 bg-slate-700 rounded-full h-1.5">
                  <div
                    className="bg-emerald-500 h-1.5 rounded-full"
                    style={{ width: `${value}%` }}
                  />
                </div>
                <span className="text-xs font-bold text-emerald-400">{value}</span>
              </div>
            </div>
          )
        })}
      </div>

      <div className="bg-slate-800/50 rounded-xl p-4 border border-slate-700 text-sm text-slate-400">
        <strong className="text-slate-200">✏️ לעדכון:</strong> ערוך את{' '}
        <code className="bg-slate-700 px-1 rounded">src/data/golden-boot-candidates.json</code> להוספת
        שחקנים או עדכון אודס.
      </div>
    </div>
  )
}

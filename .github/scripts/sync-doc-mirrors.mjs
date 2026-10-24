#!/usr/bin/env node
// Rewrites the hand-maintained mirrors of catalog/packs.json: the "N skills"
// counts, the "all-N-skills-by-pack" anchor, the full-catalog table rows and
// the per-pack count column. Run by .github/workflows/register-skill.yml so a
// skill author never touches these by hand.
import { readFileSync, writeFileSync, existsSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '../..')
const packs = JSON.parse(readFileSync(resolve(ROOT, 'catalog/packs.json'), 'utf8'))
const total = packs.total_skills
const maxPack = Math.max(0, ...packs.packs.map((p) => p.skills.length))
const esc = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
// packs.json stores each skill as {slug,...}; tolerate a bare string too.
const slugOf = (s) => (typeof s === 'string' ? s : s?.slug)

const FILES = [
  '.github/README.md',
  'docs/skill-packs.md',
  'docs/aeon-setup.md',
  'docs/examples/README.md',
  'docs/assets/hero-animated.svg',
]

let changed = 0
for (const rel of FILES) {
  const p = resolve(ROOT, rel)
  if (!existsSync(p)) continue
  const before = readFileSync(p, 'utf8')
  let t = before
  // Only rewrite a count that can only be the whole-catalog total (> largest
  // pack), so per-pack prose like "the 12 Core skills" is left alone.
  t = t.replace(/\b(\d+)\+?\s+skills\b/g, (m, n) => (Number(n) > maxPack ? `${total} skills` : m))
  t = t.replace(/all-\d+-skills-by-pack/g, `all-${total}-skills-by-pack`)
  if (t !== before) { writeFileSync(p, t); changed++ }
}

// Full-catalog table + per-pack count column live in docs/skill-packs.md.
const sp = resolve(ROOT, 'docs/skill-packs.md')
if (existsSync(sp)) {
  const before = readFileSync(sp, 'utf8')
  let t = before
  for (const pack of packs.packs) {
    const name = esc(pack.name), key = esc(pack.key)
    const slugs = pack.skills.map(slugOf).filter(Boolean)
      .map((s) => existsSync(resolve(ROOT, 'docs/assets/skill-icons', `${s}.svg`))
        ? `<img src="assets/skill-icons/${s}.svg" width="14" height="14" align="top" alt=""> \`${s}\``
        : `\`${s}\``)
      .join(', ')
    t = t.replace(
      new RegExp(`^\\| \\*\\*${name}\\*\\* \\(\`${key}\`, \\d+\\) \\|.*$`, 'm'),
      `| **${pack.name}** (\`${pack.key}\`, ${pack.skills.length}) | ${slugs} |`)
    t = t.replace(
      new RegExp(`^(\\| \\*\\*${name}\\*\\* \\(\`${key}\`\\) \\| [^|]*\\| )\\d+( \\|)$`, 'm'),
      `$1${pack.skills.length}$2`)
  }
  if (t !== before) { writeFileSync(sp, t); changed++ }
}

console.log(changed ? `sync-doc-mirrors: rewrote ${changed} file(s)` : 'sync-doc-mirrors: already in sync')
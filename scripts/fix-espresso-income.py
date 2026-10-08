from pathlib import Path
p = Path("app/src/services/database.ts")
s = p.read_text()
old = "params.type === 'OUT' && currentItem.name.trim().toLowerCase() === 'espresso'"
new = "params.type === 'OUT' && (currentItem.category === 'Espresso Base' || currentItem.name.trim().toLowerCase().includes('espresso'))"
if old not in s:
    raise SystemExit("Expected Espresso income condition was not found")
p.write_text(s.replace(old, new))
print("ESPRESSO_INCOME_FIX_DONE")

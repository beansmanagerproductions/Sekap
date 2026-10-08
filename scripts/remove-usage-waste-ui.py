from pathlib import Path
import re

ROOT = Path("app")

def read(rel):
    return (ROOT / rel).read_text()

def write(rel, text):
    (ROOT / rel).write_text(text)

# Production: keep ONLY Beans -> Espresso production. Remove Pemakaian and Waste UI/forms.
p = read("src/components/production/ProductionView.tsx")

p = p.replace("InventoryItem, ProductionLog, EspressoUsageLog, WasteLog", "InventoryItem, ProductionLog")
p = re.sub(r"\n\s*const \[usageHistory.*?\n\s*const \[wasteHistory.*?;", "", p, flags=re.S)
p = re.sub(r"\n\s*// Sub-tab inside Production view\n\s*const \[activeSubTab.*?;", "\n  const activeSubTab = 'produce';", p, flags=re.S)
p = re.sub(r"\n\s*// FORM 2: PEMAKAIAN ESPRESSO.*?\n\s*// Current active conversion ratio", "\n\n  // Current active conversion ratio", p, flags=re.S)
p = re.sub(r"\n\s*const \[prodWasteLiter.*?;", "", p)
p = re.sub(r"\n\s*// FORM 3: WASTE / SUSUT TERPISAH.*?\n\s*// Current active conversion ratio", "\n\n  // Current active conversion ratio", p, flags=re.S)
p = re.sub(r",\s*usages,\s*wastes", "", p)
p = re.sub(r"\n\s*db\.getEspressoUsages\(currentShop\.id, 50\),\n\s*db\.getWasteLogs\(currentShop\.id, 50\)", "", p)
p = re.sub(r"\n\s*setUsageHistory\(usages\);\n\s*setWasteHistory\(wastes\);", "", p)
p = re.sub(r"\n\s*const wasteNum = parseFloat\(prodWasteLiter\) \|\| 0;\n", "\n", p)
p = re.sub(r"\n\s*waste_liter: wasteNum > 0 \? wasteNum : undefined,", "", p)
p = re.sub(r"\n\s*setProdWasteLiter\('0'\);", "", p)

# Remove handlers for usage and waste.
p = re.sub(r"\n\s*// Handle Submit Espresso Usage.*?\n\s*const formatRupiah", "\n\n  const formatRupiah", p, flags=re.S)

# Remove production waste input.
p = re.sub(r"\n\s*\{?/\* 4\. Susut / Waste Ekstraksi.*?\n\s*\}\n\n\s*\{?/\* 5\. Catatan Batch", "\n\n              {/* 4. Catatan Batch", p, flags=re.S)

# Remove the sub-navigation block.
p = re.sub(r"\n\s*\{?/\* Sub Navigation Segmented Tabs \*/\}.*?\n\s*</div>\n\s*</div>\n\n\s*\{?/\* =========================================================================\s*\n\s*SUB-TAB 1:", "\n      </div>\n\n      {/* =========================================================================\n          SUB-TAB 1:", p, flags=re.S)

# Header wording.
p = p.replace("Produksi & Pemakaian Espresso", "Produksi Espresso")
p = p.replace("Staff memasukkan hasil Espresso aktual, sistem menghitung Beans dan HPP otomatis.", "Staff memasukkan hasil Espresso aktual; sistem otomatis menghitung kebutuhan Beans dan HPP.")
p = p.replace("      <div className=\"space-y-6 pb-20\">", "    <div className=\"space-y-6 pb-20\">")

# Remove waste display from production history.
p = re.sub(r"\n\s*\{p\.waste_liter \? \(.*?\) : null\}", "", p, flags=re.S)

# Delete everything after the production tab; retain its closing div and component close.
marker = "      {/* =========================================================================\n          SUB-TAB 2: PEMAKAIAN ESPRESSO"
if marker in p:
    p = p.split(marker, 1)[0] + "    </div>\n  );\n};\n"

# Remove imports that belonged only to deleted tabs.
p = p.replace("  Clock,\n", "")
p = p.replace("  History,\n", "")
p = p.replace("  Trash2,\n", "")
p = p.replace("  TrendingDown,\n", "")
p = p.replace("  ArrowRight,\n", "")
p = p.replace("  Flame,\n", "")
p = p.replace("  MinusCircle\n", "")

write("src/components/production/ProductionView.tsx", p)

# Dashboard: remove Pemakaian and Waste metrics/data. Keep production, stock, income and expenses.
p = read("src/components/dashboard/DashboardView.tsx")
p = p.replace("  EspressoUsageLog,\n", "").replace("  WasteLog,\n", "")
p = re.sub(r"\n\s*const \[usages, setUsages\].*?;", "", p)
p = re.sub(r"\n\s*const \[wasteLogs, setWasteLogs\].*?;", "", p)
p = re.sub(r",\s*useList,\s*wasteList", "", p)
p = re.sub(r"\n\s*db\.getEspressoUsages\(currentShop\.id, 50\),\n\s*db\.getWasteLogs\(currentShop\.id, 50\)", "", p)
p = re.sub(r"\n\s*setUsages\(useList\);\n\s*setWasteLogs\(wasteList\);", "", p)
p = re.sub(r"\n\s*// 5\. Pemakaian Hari Ini.*?\n\s*// 7\. Pengeluaran Hari Ini", "\n\n  // 5. Pengeluaran Hari Ini", p, flags=re.S)
p = re.sub(r"\n\s*// 6\. Waste Hari Ini.*?\n\s*// 7\. Pengeluaran Hari Ini", "\n\n  // 5. Pengeluaran Hari Ini", p, flags=re.S)
p = p.replace("Produksi, Pemakaian, Waste, dan HPP", "Produksi dan HPP")
write("src/components/dashboard/DashboardView.tsx", p)

# Reports: remove Pemakaian/Waste metrics, data loading, and Waste detail tab.
p = read("src/components/reports/ReportsView.tsx")
p = p.replace("  EspressoUsageLog, \n", "").replace("  WasteLog, \n", "")
p = p.replace("type DetailTabType = 'transactions' | 'productions' | 'expenses' | 'waste';", "type DetailTabType = 'transactions' | 'productions' | 'expenses';")
p = re.sub(r"\n\s*const \[usages, setUsages\].*?;\n\s*const \[wasteLogs, setWasteLogs\].*?;", "", p)
p = re.sub(r",\s*useList,\s*wasteList", "", p)
p = re.sub(r"\n\s*db\.getEspressoUsages\(currentShop\.id, 300\),\n\s*db\.getWasteLogs\(currentShop\.id, 300\)", "", p)
p = re.sub(r"\n\s*setWasteLogs\(wasteList\);", "", p)
p = re.sub(r"\n\s*const filteredUsages = usages\.filter\(.*?\);\n\s*const filteredWasteLogs = wasteLogs\.filter\(.*?\);", "", p)
p = re.sub(r"\n\s*const totalEspressoUsedL = filteredUsages\.reduce\(.*?\);\n\s*const totalWasteProdL = .*?\n\s*const totalWasteLogL = .*?\n\s*const totalWasteBeansKg = .*?\n\s*const totalWasteLossRp = .*?;", "", p, flags=re.S)
p = p.replace("Rekap stok beans, produksi espresso, pemakaian, waste, HPP, dan pengeluaran per periode.", "Rekap stok beans, produksi espresso, HPP, dan pengeluaran per periode.")
p = re.sub(r"\n\s*\{?/\* 5\. Espresso Digunakan \*/\}.*?\n\s*\{?/\* 7\. Total Pengeluaran", "\n\n        {/* 5. Total Pengeluaran", p, flags=re.S)
p = re.sub(r"\n\s*\{?/\* 6\. Waste / Susut \*/\}.*?\n\s*\{?/\* 7\. Total Pengeluaran", "\n\n        {/* 5. Total Pengeluaran", p, flags=re.S)
p = re.sub(r"\n\s*\{?/\* 7\. Total Pengeluaran", "\n\n        {/* 5. Total Pengeluaran", p)
p = re.sub(r"\n\s*<button\s*\n\s*onClick=\{\(\) => setActiveDetailTab\('waste'\)\}.*?</button>", "", p, flags=re.S)
p = re.sub(r"\n\s*\{activeDetailTab === 'waste' && \(.*?\n\s*\)\}", "", p, flags=re.S)
write("src/components/reports/ReportsView.tsx", p)

print("REMOVED PEMAKAIAN AND WASTE UI")

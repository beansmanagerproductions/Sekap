from pathlib import Path
root=Path("app")

def edit(rel, f):
    p=root/rel; s=p.read_text(); n=f(s); p.write_text(n); print(rel, n!=s)

# Conversion standard: 1 kg beans = 2.5 L espresso
for rel in ["src/components/settings/SettingsView.tsx","src/components/dashboard/DashboardView.tsx","src/components/production/ProductionView.tsx","src/components/accounts/AccountManagementView.tsx","src/components/reports/ReportsView.tsx","src/services/database.ts"]:
    edit(rel, lambda s: s.replace("conversion_ratio: 3.0","conversion_ratio: 2.5")
        .replace("conversion_ratio || 3.0","conversion_ratio || 2.5")
        .replace("conversion_ratio ? currentShop.conversion_ratio.toString() : '3.0'","conversion_ratio ? currentShop.conversion_ratio.toString() : '2.5'")
        .replace("parseFloat(conversionRatioInput) || 3.0","parseFloat(conversionRatioInput) || 2.5")
        .replace("Default: 1 KG = 3.0 L.","Default: 1 KG = 2.5 L.")
        .replace("'3.0'","'2.5'"))

# Types
p=root/"src/types/index.ts"; s=p.read_text()
s=s.replace("conversion_ratio?: number; // Standard: 3 (1 kg beans = 3 L espresso)","conversion_ratio?: number; // Standard: 2.5 (1 kg beans = 2.5 L espresso)")
s=s.replace("conversion_ratio: number; // e.g. 3.0 (3 Liter / 1 Kg)","conversion_ratio: number; // e.g. 2.5 (2.5 Liter / 1 Kg)")
s=s.replace("  created_at: string;\n}\n\nexport interface ProductionLog","  created_at: string;\n  unit?: string;\n  price_per_qty?: number;\n  total_amount?: number;\n}\n\nexport interface IncomeEntry {\n  id: string; shop_id: string; item_id?: string; item_name: string;\n  quantity: number; unit: string; price_per_qty: number; total_amount: number;\n  source: string; reference_id?: string; recorded_by?: string; user_id?: string;\n  recorded_at: string; notes?: string;\n}\n\nexport interface ProductionLog")
p.write_text(s)

# Database: generic income generated from stock OUT
p=root/"src/services/database.ts"; s=p.read_text()
s=s.replace("  Expense,\n  TransactionType","  Expense,\n  IncomeEntry,\n  TransactionType")
s=s.replace("const STORAGE_EXPENSES = 'bem_local_expenses';","const STORAGE_EXPENSES = 'bem_local_expenses';\nconst STORAGE_INCOME = 'bem_local_income';")
s=s.replace("    user: { id: string; name: string };\n  }): Promise<{ item: InventoryItem; transaction: StockTransaction }>", "    user: { id: string; name: string };\n    price_per_qty?: number;\n    unit?: string;\n  }): Promise<{ item: InventoryItem; transaction: StockTransaction }>")
s=s.replace("    notifyAllListeners();\n    return { item: updatedItem, transaction: tx };","    if (params.type === 'OUT' && currentItem.name.trim().toLowerCase() === 'espresso') {\n      const fixedPricePerLiter = 150000;\n      await this.recordIncome({ shop_id: params.shop_id, item_id: currentItem.id, item_name: currentItem.name,\n        quantity: qty, unit: 'L', price_per_qty: fixedPricePerLiter,\n        total_amount: Math.round(qty * fixedPricePerLiter), source: 'STOCK_OUT', reference_id: tx.id,\n        recorded_by: params.user.name, user_id: params.user.id, recorded_at: new Date().toISOString(), notes: params.notes || '' });\n    }\n    notifyAllListeners();\n    return { item: updatedItem, transaction: tx };")
marker="  async getTransactions(shopId: string, itemId?: string, limit = 100): Promise<StockTransaction[]> {"
income="""  async recordIncome(entry: Omit<IncomeEntry, 'id'>): Promise<IncomeEntry> {
    const newEntry: IncomeEntry = { ...entry, id: generateId('income') };
    const supabase = getSupabaseClient();
    if (supabase) {
      const { error } = await supabase.from('income_entries').insert([newEntry]);
      if (error) throw error;
    }
    const rows = getLocal<IncomeEntry[]>(STORAGE_INCOME, []);
    rows.unshift(newEntry); setLocal(STORAGE_INCOME, rows);
    return newEntry;
  },

  async getIncome(shopId: string, limit = 200): Promise<IncomeEntry[]> {
    const supabase = getSupabaseClient();
    if (supabase) {
      const { data, error } = await supabase.from('income_entries').select('*').eq('shop_id', shopId)
        .order('recorded_at', { ascending: false }).limit(limit);
      if (!error && data) return data as IncomeEntry[];
    }
    return getLocal<IncomeEntry[]>(STORAGE_INCOME, []).filter(e => e.shop_id === shopId).slice(0, limit);
  },

"""
if marker in s: s=s.replace(marker,income+marker)
p.write_text(s)

# Inventory: fixed-price Espresso stock-out; no manual price field
p=root/"src/components/inventory/InventoryView.tsx"; s=p.read_text()
s=s.replace("  const [movementQty, setMovementQty] = useState('');","  const [movementQty, setMovementQty] = useState('');")
s=s.replace("    setMovementQty('');\n    setMovementNotes('');","    setMovementQty('');\n    setMovementNotes('');")
s=s.replace("    if (movementType === 'OUT' && qty > movementTargetItem.current_stock) {","    if (movementType === 'OUT' && qty > movementTargetItem.current_stock) {")
s=s.replace("        quantity: qty,\n        notes:", "        quantity: qty,\n        unit: movementTargetItem.unit,\n        notes:")
p.write_text(s)

# Dashboard: load income and show today/month income
p=root/"src/components/dashboard/DashboardView.tsx"; s=p.read_text()
s=s.replace("  WasteLog,\n  Expense \n", "  WasteLog,\n  Expense,\n  IncomeEntry\n")
s=s.replace("  const [expenses, setExpenses] = useState<Expense[]>([]);","  const [expenses, setExpenses] = useState<Expense[]>([]);\n  const [incomeEntries, setIncomeEntries] = useState<IncomeEntry[]>([]);")
s=s.replace("const [itemList, txList, prodList, useList, wasteList, expList] = await Promise.all([","const [itemList, txList, prodList, useList, wasteList, expList, incomeList] = await Promise.all([")
s=s.replace("        db.getExpenses(currentShop.id, 100),","        db.getExpenses(currentShop.id, 100),\n        db.getIncome(currentShop.id, 200),")
s=s.replace("      setExpenses(expList);","      setExpenses(expList);\n      setIncomeEntries(incomeList);")
s=s.replace("  // 8. Pengeluaran Bulan Berjalan","  const todayIncome = incomeEntries.filter(e => e.recorded_at.startsWith(todayStr)).reduce((sum,e) => sum + Number(e.total_amount), 0);\n  const currentMonthIncome = incomeEntries.filter(e => e.recorded_at.startsWith(currentMonthStr)).reduce((sum,e) => sum + Number(e.total_amount), 0);\n\n  // 8. Pengeluaran Bulan Berjalan")
s=s.replace("          {/* 7. Pengeluaran Hari Ini */}","          {/* 7. Pemasukan Hari Ini */}\n          <div className=\"bg-[#0F172A]/70 backdrop-blur-md border border-white/10 rounded-2xl p-4 flex flex-col justify-between shadow-lg\"><div className=\"flex items-center justify-between text-slate-400 mb-1.5\"><span className=\"text-xs font-semibold uppercase\">7. Pemasukan Hari Ini</span><Coins className=\"w-4 h-4 text-emerald-400\" /></div><div><div className=\"text-xl sm:text-2xl font-bold font-mono text-emerald-400 truncate\">{formatRupiah(todayIncome)}</div><div className=\"text-[11px] text-slate-400 mt-0.5\">Dari stok keluar / penjualan</div></div></div>\n\n          {/* 8. Pemasukan Bulan Ini */}\n          <div className=\"bg-[#0F172A]/70 backdrop-blur-md border border-white/10 rounded-2xl p-4 flex flex-col justify-between shadow-lg\"><div className=\"flex items-center justify-between text-slate-400 mb-1.5\"><span className=\"text-xs font-semibold uppercase\">8. Pemasukan Bulan Ini</span><CreditCard className=\"w-4 h-4 text-cyan-400\" /></div><div><div className=\"text-xl sm:text-2xl font-bold font-mono text-cyan-400 truncate\">{formatRupiah(currentMonthIncome)}</div><div className=\"text-[11px] text-slate-400 mt-0.5\">Akumulasi pemasukan</div></div></div>\n\n          {/* 9. Pengeluaran Hari Ini */}")
s=s.replace("          {/* 8. Pengeluaran Bulan Berjalan */}","          {/* 10. Pengeluaran Bulan Berjalan */}")
s=s.replace("          {/* 9. HPP Espresso */}","          {/* 11. HPP Espresso */}")
s=s.replace("<span>9 Ringkasan Metrik Bisnis & Finansial</span>","<span>11 Ringkasan Metrik Bisnis & Finansial</span>")
p.write_text(s)

print("BUSINESS_RULES_PATCH_DONE")

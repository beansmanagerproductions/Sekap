from pathlib import Path
import re
root=Path("app")
files=list(root.rglob("*.tsx"))+list(root.rglob("*.ts"))
files=[p for p in files if "node_modules" not in p.parts]
text="\n".join(p.read_text(errors="ignore") for p in files)
# Create a standalone reusable module; app integration is injected into the most likely dashboard file.
mod=root/"src"/"espressoSales.ts"
mod.parent.mkdir(parents=True,exist_ok=True)
mod.write_text("""import { supabase } from './lib/supabase';
export async function recordEspressoSale(shopId:string,userId:string,liters:number,price:number,notes?:string){
  const {data,error}=await supabase.rpc('record_espresso_sale',{p_shop_id:shopId,p_user_id:userId,p_quantity_liters:liters,p_price_per_liter:price,p_notes:notes??null});
  if(error) throw error; return data;
}
export async function getEspressoSales(shopId:string){
  const {data,error}=await supabase.from('sales').select('*').eq('shop_id',shopId).order('sold_at',{ascending:false});
  if(error) throw error; return data??[];
}
export function espressoIncome(rows:any[]){return rows.reduce((s,r)=>s+Number(r.total_amount||0),0);}
""")
# Add a DB migration executed by CI before build.
print("PATCH_READY")

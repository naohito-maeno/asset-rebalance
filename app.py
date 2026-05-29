import streamlit as st
import pandas as pd
import io

# -----------------------------------------------------------------------------
# 1. マスターデータ（統合・シンプル化）
# -----------------------------------------------------------------------------
MASTER_DATA = {
    "全世界株式": [
        "ｅＭＡＸＩＳ　Ｓｌｉｍ　全世界株式（オール・カントリー）",
        "ｅＭＡＸＩＳ　Ｓｌｉｍ　全世界株式（除く日本）",
        "楽天・オールカントリー株式インデックス・ファンド",
        "ＳＢＩ・Ｖ・全世界株式インデックス・ファンド"
    ],
    "先進国株式": [
        "ｅＭＡＸＩＳ　Ｓｌｉｍ　先進国株式インデックス",
        "楽天・先進国株式インデックス・ファンド"
    ],
    "米国株式": [
        "ｅＭＡＸＩＳ　Ｓｌｉｍ　米国株式（Ｓ＆Ｐ５００）",
        "楽天・Ｓ＆Ｐ５００インデックス・ファンド"
    ],
    "新興国株式": [
        "ｅＭＡＸＩＳ　Ｓｌｉｍ　新興国株式インデックス",
        "楽天・新興国株式インデックス・ファンド"
    ],
    "国内株式": [
        "ｅＭＡＸＩＳ　Ｓｌｉｍ　国内株式（ＴＯＰＩＸ）",
        "楽天・日経２２５インデックス・ファンド"
    ],
    "先進国債券": [
        "ｅＭＡＸＩＳ　Ｓｌｉｍ　先進国債券インデックス",
        "楽天・先進国債券インデックス・ファンド",
        "たわらノーロード　先進国債券＜為替ヘッジあり＞"
    ],
    "新興国債券": [
        "三菱ＵＦＪ　ｉ成信　新興国債券インデックス",
        "ｉfree　新興国債券インデックス"
    ],
    "国内債券": [
        "ｅＭＡＸＩＳ　Ｓｌｉｍ　国内債券インデックス",
        "日興　インデックスファンド日本債券"
    ],
    "先進国リート": [
        "ｅＭＡＸＩＳ　Ｓｌｉｍ　先進国リートインデックス",
        "ｉfree　外国リートインデックス"
    ],
    "国内リート": [
        "ｅＭＡＸＩＳ　Ｓｌｉｍ　国内リートインデックス",
        "Ｏｎｅ－ＤＩＡＭ　国内リートインデックスファンド"
    ],
    "ゴールド": [
        "三菱ＵＦＪ　純金ファンド",
        "ｉfree／新ゴールド・ファンド",
        "ＳＭＴ　ゴールドインデックス・オープン（為替ヘッジあり）",
        "楽天・プラス・ゴールドインデックス（為替ヘッジあり）"
    ]
}

ASSET_TYPES = list(MASTER_DATA.keys())
ACCOUNT_TYPES = ["NISAつみたて投資枠", "NISA成長投資枠", "特定口座", "その他課税口座"]

# -----------------------------------------------------------------------------
# 2. アプリの基本設定・タイトル
# -----------------------------------------------------------------------------
st.set_page_config(page_title="資産リバランスシミュレーター", layout="wide")
st.title("📊 資産リバランスシミュレーター")
st.write("総資産（リスク資産＋無リスク資産）を最適バランスに保つための、各資産の売買額を算出するツールです。")
st.caption("※バランスファンドを保有されている場合は、各大まかな資産タイプに分解して入力するか、本ツールを機に単一資産ファンドへの組み替えをご検討ください。")

st.markdown("---")

# -----------------------------------------------------------------------------
# 3. CSVファイルの読み込み（復元）機能
# -----------------------------------------------------------------------------
st.header("📂 設定の保存・読み込み")
uploaded_file = st.file_uploader("過去に保存したツール設定ファイル（.csv）があれば、ここにドラッグ＆ドロップしてください", type="csv")

# デフォルト設定値の準備
saved_rows = []
saved_targets = {atype: 0.0 for atype in ASSET_TYPES}
saved_targets["無リスク資産"] = 0.0

if uploaded_file is not None:
    try:
        df_load = pd.read_csv(uploaded_file)
        # データの分類
        df_risk = df_load[df_load['type'] == 'risk']
        df_target = df_load[df_load['type'] == 'target']
        
        for _, row in df_risk.iterrows():
            saved_rows.append({
                "asset_type": row["asset_type"],
                "brand": row["brand"],
                "account_type": row["account_type"]
            })
        for _, row in df_target.iterrows():
            saved_targets[row["asset_type"]] = float(row["target_ratio"])
        st.success("✅ 設定ファイルを読み込みました。下の入力欄に反映されています。評価額のみ最新の数字を入力してください。")
    except Exception as e:
        st.error("⚠️ ファイルの読み込みに失敗しました。正しい設定ファイルか確認してください。")

st.markdown("---")

# -----------------------------------------------------------------------------
# 4. 現在の資産入力（縦並びでゆったり配置）
# -----------------------------------------------------------------------------
st.header("1. 現在の資産入力")

# リスク資産の入力欄
st.subheader("🔹 リスク資産の入力")

# 読み込んだデータの件数を初期値にする（なければ5）
init_row_count = len(saved_rows) if len(saved_rows) > 0 else 5
row_count = st.number_input("入力行数（保有しているファンドの数）", min_value=1, max_value=20, value=int(init_row_count))

risk_data = []

for i in range(int(row_count)):
    st.markdown(f"##### 【{i+1}件目】")
    
    # 復元データの取得
    d_type = saved_rows[i]["asset_type"] if i < len(saved_rows) else ASSET_TYPES[0]
    d_brand = saved_rows[i]["brand"] if i < len(saved_rows) else None
    d_account = saved_rows[i]["account_type"] if i < len(saved_rows) else ACCOUNT_TYPES[0]
    
    # 横幅をPCでもしっかり確保する比率
    c_a, c_b, c_c, c_d = st.columns([1.2, 2.5, 1.3, 1.5])
    
    with c_a:
        idx_type = ASSET_TYPES.index(d_type) if d_type in ASSET_TYPES else 0
        asset_type = st.selectbox(f"資産タイプ", ASSET_TYPES, index=idx_type, key=f"type_{i}")
        
    with c_b:
        available_brands = MASTER_DATA[asset_type]
        idx_brand = available_brands.index(d_brand) if d_brand in available_brands else 0
        brand = st.selectbox(f"銘柄名（目安）", available_brands, index=idx_brand, key=f"brand_{i}")
        
    with c_c:
        idx_account = ACCOUNT_TYPES.index(d_account) if d_account in ACCOUNT_TYPES else 0
        account_type = st.selectbox(f"口座区分", ACCOUNT_TYPES, index=idx_account, key=f"account_{i}")
        
    with c_d:
        amount = st.number_input(f"評価額（円）", min_value=0, value=0, step=10000, key=f"amount_{i}")
        # コンマ付き金額プレビュー（入力欄のすぐ下に出力）
        st.markdown(f"👉 **{amount:,} 円**")
        
    risk_data.append({"asset_type": asset_type, "amount": amount, "brand": brand, "account_type": account_type})
    st.markdown(" ")

# 無リスク資産の入力欄
st.markdown("---")
st.subheader("🔹 無リスク資産の入力")
c_cash1, c_cash2 = st.columns(2)
with c_cash1:
    cash_bank = st.number_input("銀行預金・現金（円）", min_value=0, value=0, step=50000)
    st.markdown(f"👉 **{cash_bank:,} 円**")
with c_cash2:
    cash_bond = st.number_input("個人向け国債（円）", min_value=0, value=0, step=50000)
    st.markdown(f"👉 **{cash_bond:,} 円**")
    
cash_total = cash_bank + cash_bond

# データ集計（SUMIF関数相当）
current_summary = {atype: 0 for atype in ASSET_TYPES}
current_summary["無リスク資産"] = cash_total

for item in risk_data:
    current_summary[item["asset_type"]] += item["amount"]

total_assets = sum(current_summary.values())

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. 目標比率の設定（縦並びで入力しやすい形へ）
# -----------------------------------------------------------------------------
st.header("2. 目標比率の設定 (%)")
st.write("各資産の理想の配分比率を入力してください。合計が100%になるように調整します。")

target_ratios = {}
total_target_ratio = 0.0
all_categories = ASSET_TYPES + ["無リスク資産"]

# 横に並べて省スペース化しつつ入力しやすく配置
c_target = st.columns(3)
for idx, atype in enumerate(all_categories):
    with c_target[idx % 3]:
        d_target = saved_targets.get(atype, 0.0)
        t_ratio = st.number_input(f"{atype} (%)", min_value=0.0, max_value=100.0, value=d_target, step=5.0, key=f"target_{atype}")
        target_ratios[atype] = t_ratio
        total_target_ratio += t_ratio

st.markdown(f"### 📊 現在の目標比率の合計: **{total_target_ratio:.1f} %** / 100%")

st.markdown("---")

# -----------------------------------------------------------------------------
# 6. 分析結果とリバランス指示
# -----------------------------------------------------------------------------
st.header("3. 分析結果とリバランス指示")
st.write(f"### 💰 現在の総資産合計: **{total_assets:,} 円**")

# テーブル表示
st.markdown("| 資産タイプ | 目標比率 | 現在の合計額 | 現在の比率 | 必要売買額（＋購入 / －売却） |")
st.markdown("| :--- | :---: | :---: | :---: | :---: |")

for atype in all_categories:
    cur_amt = current_summary[atype]
    cur_ratio = (cur_amt / total_assets * 100) if total_assets > 0 else 0.0
    t_ratio = target_ratios[atype]
    
    target_amt = total_assets * (t_ratio / 100.0)
    required_trade = target_amt - cur_amt
    
    trade_str = f"+{required_trade:,.0f} 円" if required_trade > 0 else f"{required_trade:,.0f} 円"
    if required_trade == 0:
        trade_str = "0 円"
        
    st.markdown(f"| **{atype}** | {t_ratio:.1f} % | {cur_amt:,} 円 | {cur_ratio:.1f} % | **{trade_str}** |")
    
st.markdown("---")
st.markdown(f"| **合計** | **{total_target_ratio:.1f} %** | **{total_assets:,} 円** | **{100 if total_assets > 0 else 0} %** | - |")

# 目標比率の合計チェック判定
if total_target_ratio != 100.0:
    st.warning(f"⚠️ 目標比率の合計が **{total_target_ratio:.1f}%** になっています。100%になるように数値を調整してください。")
else:
    st.success("✅ 目標比率の合計が100%です。上記のリバランス指示（必要売買額）に従って資産を調整してください。")

st.markdown("---")

# -----------------------------------------------------------------------------
# 7. 今後のためのCSVダウンロード機能
# -----------------------------------------------------------------------------
st.header("💾 今回の設定データを保存する")
st.write("現在入力されている「資産タイプ」「銘柄名」「口座区分」「目標比率」のセットをパソコンにダウンロードしておけます。次回以降、一番上の欄に読み込ませることで入力を大幅に省略できます。")

# 保存用データフレームの構築
export_data = []
for item in risk_data:
    export_data.append({
        "type": "risk", "asset_type": item["asset_type"], "brand": item["brand"], 
        "account_type": item["account_type"], "target_ratio": 0.0
    })
for atype, ratio in target_ratios.items():
    export_data.append({
        "type": "target", "asset_type": atype, "brand": "", 
        "account_type": "", "target_ratio": ratio
    })

df_export = pd.DataFrame(export_data)

# メモリ上にCSVを出力してダウンロードボタンに渡す
csv_buffer = io.StringIO()
df_export.to_csv(csv_buffer, index=False)
csv_pasted = csv_buffer.getvalue()

st.download_button(
    label="現在の構成・目標比率をCSVとして保存する",
    data=csv_pasted,
    file_name="my_portfolio_settings.csv",
    mime="text/csv"
)
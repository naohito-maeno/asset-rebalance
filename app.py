import streamlit as st

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
# 2. アプリの基本設定・タイトル（文言のご指定通りに変更）
# -----------------------------------------------------------------------------
st.set_page_config(page_title="資産リバランスシミュレーター", layout="wide")
st.title("📊 資産リバランスシミュレーター")
st.write("総資産（リスク資産＋無リスク資産）を最適バランスに保つための、各資産の売買額を算出するツールです。")
st.caption("※バランスファンドを保有されている場合は、各大まかな資産タイプに分解して入力するか、本ツールを機に単一資産ファンドへの組み替えをご検討ください。")

# -----------------------------------------------------------------------------
# 3. 画面レイアウト（左側：入力、右側：分析・集計）
# -----------------------------------------------------------------------------
col1, col2 = st.columns([1.2, 1])

with col1:
    st.header("1. 現在の資産入力")
    
    # リスク資産の入力欄
    st.subheader("🔹 リスク資産の入力")
    risk_data = []
    
    row_count = st.number_input("入力行数（保有しているファンドの数）", min_value=1, max_value=20, value=5)
    
    for i in range(int(row_count)):
        st.markdown(f"**【{i+1}件目】**")
        c_a, c_b, c_c, c_d = st.columns([1, 1.5, 1, 1])
        
        with c_a:
            asset_type = st.selectbox(f"資産タイプ", ASSET_TYPES, key=f"type_{i}")
        with c_b:
            available_brands = MASTER_DATA[asset_type]
            brand = st.selectbox(f"銘柄名（目安）", available_brands, key=f"brand_{i}")
        with c_c:
            account_type = st.selectbox(f"口座区分", ACCOUNT_TYPES, key=f"account_{i}")
        with c_d:
            amount = st.number_input(f"評価額（円）", min_value=0, value=0, step=10000, key=f"amount_{i}")
            
        risk_data.append({"asset_type": asset_type, "amount": amount})
        
    # 無リスク資産の入力欄
    st.subheader("🔹 無リスク資産の入力")
    c_cash1, c_cash2 = st.columns(2)
    with c_cash1:
        cash_bank = st.number_input("銀行預金・現金（円）", min_value=0, value=0, step=50000)
    with c_cash2:
        cash_bond = st.number_input("個人向け国債（円）", min_value=0, value=0, step=50000)
        
    cash_total = cash_bank + cash_bond

# -----------------------------------------------------------------------------
# 4. データ集計と目標比率の設定（「分析」シート相当）
# -----------------------------------------------------------------------------
current_summary = {atype: 0 for atype in ASSET_TYPES}
current_summary["無リスク資産"] = cash_total

for item in risk_data:
    current_summary[item["asset_type"]] += item["amount"]

total_assets = sum(current_summary.values())

# サイドバー（左メニュー）での目標比率の入力と合計の自動計算
st.sidebar.header("🎯 目標比率の設定 (%)")
target_ratios = {}
total_target_ratio = 0.0

all_categories = ASSET_TYPES + ["無リスク資産"]

# 最初に入力欄をすべて生成し、合計を算出する
for atype in all_categories:
    t_ratio = st.sidebar.number_input(f"{atype} (%)", min_value=0.0, max_value=100.0, value=0.0, step=5.0, key=f"target_{atype}")
    target_ratios[atype] = t_ratio
    total_target_ratio += t_ratio

# リアルタイム合計の表示（サイドバー上部）
st.sidebar.markdown(f"### 📊 目標合計: **{total_target_ratio:.1f} %** / 100%")

with col2:
    st.header("2. 分析結果とリバランス指示")
    st.write(f"### 💰 現在の総資産: **{total_assets:,} 円**")
    
    st.markdown("---")
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
        st.warning(f"⚠️ 左メニューの目標比率の合計が **{total_target_ratio:.1f}%** になっています。100%になるように調整してください。")
    else:
        st.success("✅ 目標比率の合計が100%です。リバランス指示に従って資産を調整してください。")
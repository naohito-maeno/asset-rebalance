import streamlit as st

# -----------------------------------------------------------------------------
# 1. マスターデータ（「設定」シート相当のクレンジング済みデータ）
# -----------------------------------------------------------------------------
# Excelの仕様制限（カッコ問題）がないため、アプローチに合わせた綺麗な表記で一元管理します。
MASTER_DATA = {
    "全世界株式": {
        "SBI": [
            "ｅＭＡＸＩＳ　Ｓｌｉｍ　全世界株式（オール・カントリー）",
            "ＳＢＩ・Ｖ・全世界株式インデックス・ファンド",
            "みのりのみのり"
        ],
        "楽天": [
            "楽天・オールカントリー株式インデックス・ファンド",
            "三井住友ＤＳ－三井住友・ＤＣ外国株式インデックスファンド"
        ]
    },
    "全世界株式除く日本": {
        "SBI": ["ｅＭＡＸＩＳ　Ｓｌｉｍ　全世界株式（除く日本）"],
        "楽天": ["楽天・全世界株式（除く日本）インデックス・ファンド"]
    },
    "先進国株式": {
        "SBI": ["ｅＭＡＸＩＳ　Ｓｌｉｍ　先進国株式インデックス"],
        "楽天": ["楽天・先進国株式インデックス・ファンド"]
    },
    "米国株式": {
        "SBI": ["ｅＭＡＸＩＳ　Ｓｌｉｍ　米国株式（Ｓ＆Ｐ５００）"],
        "楽天": ["楽天・Ｓ＆Ｐ５００インデックス・ファンド"]
    },
    "新興国株式": {
        "SBI": ["ｅＭＡＸＩＳ　Ｓｌｉｍ　新興国株式インデックス"],
        "楽天": ["楽天・新興国株式インデックス・ファンド"]
    },
    "国内株式": {
        "SBI": ["ｅＭＡＸＩＳ　Ｓｌｉｍ　国内株式（ＴＯＰＩＸ）"],
        "楽天": ["楽天・日経２２５インデックス・ファンド"]
    },
    "先進国債券": {
        "SBI": ["ｅＭＡＸＩＳ　Ｓｌｉｍ　先進国債券インデックス"],
        "楽天": ["楽天・先進国債券インデックス・ファンド"]
    },
    "先進国債券H有": {
        "SBI": ["たわらノーロード　先進国債券＜為替ヘッジあり＞"],
        "楽天": ["フィデリティ・ＵＳハイ・イールド・ファンド（資産成長型）Ｄ"]
    },
    "新興国債券": {
        "SBI": ["三菱ＵＦＪ　ｉ成信　新興国債券インデックス"],
        "楽天": ["ｉfree　新興国債券インデックス"]
    },
    "国内債券": {
        "SBI": ["ｅＭＡＸＩＳ　Ｓｌｉｍ　国内債券インデックス"],
        "楽天": ["日興　インデックスファンド日本債券"]
    },
    "先進国リート": {
        "SBI": ["ｅＭＡＸＩＳ　Ｓｌｉｍ　先進国リートインデックス"],
        "楽天": ["ｉfree　外国リートインデックス"]
    },
    "国内リート": {
        "SBI": ["ｅＭＡＸＩＳ　Ｓｌｉｍ　国内リートインデックス"],
        "楽天": ["Ｏｎｅ－ＤＩＡＭ　国内リートインデックスファンド"]
    },
    "ゴールド": {
        "SBI": ["三菱ＵＦＪ　純金ファンド"],
        "楽天": ["ｉfree／新ゴールド・ファンド"]
    },
    "ゴールドH有": {
        "SBI": ["ＳＭＴ　ゴールドインデックス・オープン（為替ヘッジあり）"],
        "楽天": ["楽天・プラス・ゴールドインデックス（為替ヘッジあり）"]
    }
}

ASSET_TYPES = list(MASTER_DATA.keys())

# -----------------------------------------------------------------------------
# 2. アプリの基本設定・タイトル
# -----------------------------------------------------------------------------
st.set_page_config(page_title="資産リバランスシミュレーター", layout="wide")
st.title("📊 資産リバランスシミュレーター")
st.write("総資産（リスク資産＋無リスク資産）の最適バランスを算出するツールです。")

# -----------------------------------------------------------------------------
# 3. 画面レイアウト（左側：入力、右側：分析・集計）
# -----------------------------------------------------------------------------
col1, col2 = st.columns([1, 1.2])

with col1:
    st.header("1. 現在の資産入力")
    
    # 証券会社の選択（「入力」シート B2セル相当）
    company = st.selectbox("証券会社を選択してください", ["SBI", "楽天"])
    
    # リスク資産の入力欄（動的ドロップダウン）
    st.subheader("🔹 リスク資産の入力")
    risk_data = []
    
    # ユーザーが入力したい行数を指定（初期値5行）
    row_count = st.number_input("入力行数", min_value=1, max_value=20, value=5)
    
    for i in range(int(row_count)):
        st.markdown(f"**【{i+1}件目】**")
        c_a, c_b, c_c = st.columns([1, 1.5, 1])
        
        with c_a:
            asset_type = st.selectbox(f"資産タイプ", ASSET_TYPES, key=f"type_{i}")
        with c_b:
            # 選択された「資産タイプ」と「証券会社」に応じて銘柄を自動で絞り込む（連動ドロップダウン）
            available_brands = MASTER_DATA[asset_type].get(company, ["該当銘柄なし"])
            brand = st.selectbox(f"銘柄名", available_brands, key=f"brand_{i}")
        with c_c:
            amount = st.number_input(f"評価額（円）", min_value=0, value=0, step=10000, key=f"amount_{i}")
            
        risk_data.append({"asset_type": asset_type, "amount": amount})
        
    # 無リスク資産の入力欄（「入力」シート 20行目以下相当）
    st.subheader("🔹 無リスク資産の入力")
    c_cash1, c_cash2 = st.columns(2)
    with c_cash1:
        cash_bank = st.number_input("銀行預金（円）", min_value=0, value=0, step=50000)
    with c_cash2:
        cash_bond = st.number_input("個人向け国債（円）", min_value=0, value=0, step=50000)
        
    cash_total = cash_bank + cash_bond

# -----------------------------------------------------------------------------
# 4. データ集計と分析（「分析」シート相当）
# -----------------------------------------------------------------------------
# 資産タイプごとの現在の合計額を算出（SUMIF関数相当）
current_summary = {atype: 0 for atype in ASSET_TYPES}
current_summary["無リスク資産"] = cash_total

for item in risk_data:
    current_summary[item["asset_type"]] += item["amount"]

total_assets = sum(current_summary.values())

with col2:
    st.header("2. 目標比率の設定と分析結果")
    st.write(f"### 💰 現在の総資産: **{total_assets:,} 円**")
    
    # 比率設定と結果表示のテーブル作成
    st.markdown("---")
    st.markdown("| 資産タイプ | 目標比率 (%) | 現在の合計額 | 現在の比率 | 必要売買額（＋購入 / －売却） |")
    st.markdown("| :--- | :---: | :---: | :---: | :---: |")
    
    target_ratios = {}
    total_target_ratio = 0.0
    
    # 14種類のリスク資産 + 無リスク資産のループ処理
    all_categories = ASSET_TYPES + ["無リスク資産"]
    
    for atype in all_categories:
        cur_amt = current_summary[atype]
        # 現在の比率計算（常に総資産が分母）
        cur_ratio = (cur_amt / total_assets * 100) if total_assets > 0 else 0.0
        
        # 目標比率の入力欄（テーブル風に見せるためのUI工夫）
        # 各行に個別の入力ボックスを配置
        t_ratio = st.sidebar.number_input(f"目標：{atype} (%)", min_value=0.0, max_value=100.0, value=0.0, step=5.0)
        target_ratios[atype] = t_ratio
        total_target_ratio += t_ratio
        
        # 必要売買額の計算（「プラス＝購入」「マイナス＝売却」）
        target_amt = total_assets * (t_ratio / 100.0)
        required_trade = target_amt - cur_amt
        
        # 表の1行を出力
        trade_str = f"+{required_trade:,.0f} 円" if required_trade > 0 else f"{required_trade:,.0f} 円"
        if required_trade == 0:
            trade_str = "0 円"
            
        st.markdown(f"| **{atype}** | {t_ratio} % | {cur_amt:,} 円 | {cur_ratio:.1f} % | **{trade_str}** |")
        
    st.markdown("---")
    st.markdown(f"| **合計** | **{total_target_ratio:.1f} %** | **{total_assets:,} 円** | **{100 if total_assets > 0 else 0} %** | - |")
    
    # 目標比率の合計が100%になっていない場合の警告表示
    if total_target_ratio != 100.0:
        st.warning(f"⚠️ 目標比率の合計が **{total_target_ratio:.1f}%** になっています。100%になるように左メニュー（サイドバー）で調整してください。")
    else:
        st.success("✅ 目標比率の合計が100%です。リバランス指示に従って資産を調整してください。")
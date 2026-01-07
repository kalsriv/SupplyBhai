# excel_analysis.py

import pandas as pd

def analyze_supply_chain_excel(df: pd.DataFrame):
    results = {}

    # 1. Missing values
    results["missing_values"] = df.isna().sum().to_dict()

    # 2. Summary stats for numeric columns
    numeric_cols = df.select_dtypes(include="number").columns
    if len(numeric_cols) > 0:
        results["summary_stats"] = df[numeric_cols].describe().to_dict()

    # 3. SKU count
    for col in ["SKU", "Item", "ItemCode", "Product"]:
        if col in df.columns:
            results["unique_skus"] = df[col].nunique()
            break

    # 4. Items below reorder point
    if {"OnHand", "ReorderPoint"}.issubset(df.columns):
        df["below_reorder"] = df["OnHand"] < df["ReorderPoint"]
        results["items_below_reorder"] = int(df["below_reorder"].sum())

    # 5. Inventory value (if columns exist)
    if {"OnHand", "UnitCost"}.issubset(df.columns):
        df["inventory_value"] = df["OnHand"] * df["UnitCost"]
        results["total_inventory_value"] = float(df["inventory_value"].sum())

    return results

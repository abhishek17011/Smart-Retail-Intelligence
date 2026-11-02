
import pandas as pd
import os

from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules


INPUT_PATH = "data/processed/cleaned_retail.csv"
OUTPUT_PATH = "data/processed/association_rules.csv"


def run_market_basket():

    print("=" * 55)
    print("SMART RETAIL INTELLIGENCE SYSTEM")
    print("APRIORI MARKET BASKET ANALYSIS")
    print("=" * 55)

    # 1. Load dataset
    df = pd.read_csv(INPUT_PATH)

    print("\nTotal transactions:", df["InvoiceNo"].nunique())

    # 2. Select top 50 frequently purchased products
    top_products = (
        df.groupby("StockCode")["InvoiceNo"]
        .nunique()
        .nlargest(50)
        .index
    )

    df = df[df["StockCode"].isin(top_products)]

    # 3. Create transaction baskets
    transactions = (
        df.groupby("InvoiceNo")["StockCode"]
        .apply(lambda x: list(set(x.astype(str))))
    )

    transactions = [
        items for items in transactions if len(items) >= 2
    ]

    print("Valid baskets:", len(transactions))

    if not transactions:
        print("No valid product combinations found.")
        return

    # 4. Convert transactions into one-hot encoded data
    encoder = TransactionEncoder()
    encoded_array = encoder.fit(transactions).transform(
        transactions, sparse=True
    )

    basket_df = pd.DataFrame.sparse.from_spmatrix(
        encoded_array,
        columns=encoder.columns_
    )

    # 5. Apply Apriori algorithm
    print("\nRunning Apriori algorithm...")

    frequent_items = apriori(
        basket_df,
        min_support=0.01,
        use_colnames=True,
        max_len=3,
        low_memory=True
    )

    print("Frequent itemsets found:", len(frequent_items))

    # 6. Generate association rules
    if frequent_items.empty or not (
        frequent_items["itemsets"].apply(len) >= 2
    ).any():
        print("No frequent product combinations found.")
        return

    rules = association_rules(
        frequent_items,
        metric="confidence",
        min_threshold=0.30
    )

    # 7. Sort by confidence
    if rules.empty:
        print("No association rules found.")
        return

    rules = rules.sort_values(
        by="confidence",
        ascending=False
    )

    # 8. Format product combinations
    rules["antecedents"] = rules["antecedents"].apply(
        lambda x: ", ".join(sorted(map(str, x)))
    )

    rules["consequents"] = rules["consequents"].apply(
        lambda x: ", ".join(sorted(map(str, x)))
    )

    # 9. Save results
    os.makedirs("data/processed", exist_ok=True)

    rules.to_csv(OUTPUT_PATH, index=False)

    # 10. Display top 10 rules
    print("\nTOP 10 PRODUCT ASSOCIATION RULES")

    print(
        rules[
            ["antecedents", "consequents",
             "support", "confidence", "lift"]
        ].head(10).to_string(index=False)
    )

    print("\nResults saved:", OUTPUT_PATH)

    print("\n" + "=" * 55)
    print("APRIORI ANALYSIS COMPLETED SUCCESSFULLY")
    print("=" * 55)


if __name__ == "__main__":
    run_market_basket()

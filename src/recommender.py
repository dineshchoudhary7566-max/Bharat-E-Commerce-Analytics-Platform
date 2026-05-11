# Adal's area
# recommendation algorithm will be here as a function.

import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import os

# --- 1. PART TO RUN ONCE ON SYSTEM START (FOR PERFORMANCE) ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MATRIX_PATH = os.path.join(BASE_DIR, 'data', 'user_item_matrix.csv')
# Read the table
# Eren's matrix similarity table.
df_matrix = pd.read_csv(MATRIX_PATH, index_col=0)

# Put products in rows and calculate the massive similarity matrix ONCE
item_matrix = df_matrix.T
# Using those 0s and numbers, we calculated the angle of products to each other:
sim_array = cosine_similarity(item_matrix)
sim_df = pd.DataFrame(sim_array, index=item_matrix.index, columns=item_matrix.index)


# --- 2. FUNCTION TO BE CALLED FROM THE WEBSITE ---
def get_recommendations(product_id, top_n=5):
    # Ensure column names from CSV are strings
    product_id = str(product_id) 
    
    # Step A: Error Handling (If product was never sold or doesn't exist)
    if product_id not in sim_df.columns:
        return ["Product not found in the database."]
    
    # Step B: Get similarity scores of the related product with all other products and sort descending
    similar_scores = sim_df[product_id].sort_values(ascending=False)
    
    # Step C: The most similar product is itself (Score 1.0). Remove it from the list!
    similar_scores = similar_scores.drop(product_id)
    
    # Step D: Return the ID/Name of the top 5 most similar products as a list
    top_products = similar_scores.head(top_n).index.tolist()
    
    return top_products

# A small check just for our testing (This won't run when connected to the website)
if __name__ == "__main__":
    # Let's test a random product code from the database (e.g. product '11')
    # (You can replace this with a real ID from your database)
    sample_products = sim_df.columns[:3] # Let's see the IDs of the first 3 products
    print("Available first 3 product IDs:", sample_products.tolist())
    
    test_id = sample_products[0]
    print(f"\nRecommendations for product ID {test_id}:")
    print(get_recommendations(test_id))
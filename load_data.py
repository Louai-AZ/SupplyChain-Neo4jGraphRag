from neo4j import GraphDatabase  
from langchain_core.documents import Document  
from sentence_transformers import SentenceTransformer 
import json  
import os  
from dotenv import load_dotenv 

# Load environment variables from a .env file
load_dotenv()

# Retrieve Neo4j connection details from environment variables
URI = os.getenv("NEO4J_URI")  
AUTH = (os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")) 

# Initialize Neo4j driver with the provided URI and authentication details
driver = GraphDatabase.driver(URI, auth=AUTH)

# Initialize the SentenceTransformer model for generating embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")

# Define the file paths for the JSON data files (products, suppliers, warehouses, routes, relationships)
PRODUCTS_FILE = 'data/products.json'
SUPPLIERS_FILE = 'data/suppliers.json'
WAREHOUSES_FILE = 'data/warehouses.json'
ROUTES_FILE = 'data/routes.json'
RELATIONSHIPS_FILE = 'data/relationships.json'

# Function to load data from a JSON file
def load_json(file_path):
    """Loads a JSON file and returns its contents."""
    with open(file_path, 'r') as file:
        return json.load(file)

# Load data from JSON files into corresponding variables
products = load_json(PRODUCTS_FILE)
suppliers = load_json(SUPPLIERS_FILE)
warehouses = load_json(WAREHOUSES_FILE)
routes = load_json(ROUTES_FILE)
relationships = load_json(RELATIONSHIPS_FILE)

# Function to load product data into Neo4j
def load_products():
    """Load product data into Neo4j and create embeddings for descriptions."""
    # Create a vector index for the product description embeddings (if it doesn't already exist)
    with driver.session() as session:
        session.run("""
            CREATE VECTOR INDEX product_description_embeddings IF NOT EXISTS
            FOR (p:Product) ON (p.description_embedding)
            OPTIONS {indexConfig: {
                `vector.dimensions`: 384,
                `vector.similarity_function`: 'cosine'
            }}
        """)

    # Loop through the products and create/merge each one in Neo4j
    for product in products:
        doc = Document(page_content=product["description"], metadata={"id": product["id"]})
        # Generate the embedding for the product description using the SentenceTransformer model
        embedding = model.encode([doc.page_content])[0].tolist()

        with driver.session() as session:
            # Insert the product data into Neo4j, including the generated embedding
            session.run("""
                MERGE (p:Product {id: $id})
                SET p.name = $name,
                    p.description = $description,
                    p.price = $price,
                    p.category = $category,
                    p.description_embedding = $embedding
            """, {
                "id": product["id"],
                "name": product["name"],
                "description": product["description"],
                "price": product["price"],
                "category": product["category"],
                "embedding": embedding
            })

# Function to load supplier data into Neo4j
def load_suppliers():
    """Load supplier data into Neo4j."""
    with driver.session() as session:
        for supplier in suppliers:
            # Insert or update the supplier data in Neo4j
            session.run("""
                MERGE (s:Supplier {id: $id})
                SET s.name = $name,
                    s.location = $location,
                    s.specialization = $specialization
            """, supplier)

# Function to load warehouse data into Neo4j
def load_warehouses():
    """Load warehouse data into Neo4j."""
    with driver.session() as session:
        for warehouse in warehouses:
            # Insert or update the warehouse data in Neo4j
            session.run("""
                MERGE (w:Warehouse {id: $id})
                SET w.name = $name,
                    w.location = $location,
                    w.capacity = $capacity
            """, warehouse)

# Function to load transportation route data into Neo4j
def load_transportation_routes():
    """Load transportation route data (connections between warehouses) into Neo4j."""
    with driver.session() as session:
        for route in routes:
            # Create relationships between warehouses based on the transportation routes
            session.run("""
                MATCH (w1:Warehouse {id: $from})
                MATCH (w2:Warehouse {id: $to})
                MERGE (w1)-[r:CONNECTED_TO]->(w2)
                SET r.distance = $distance,
                    r.duration = $duration
            """, route)

# Function to create relationships between suppliers, products, and warehouses in Neo4j
def create_relationships():
    """Create relationships between suppliers, products, and warehouses."""
    with driver.session() as session:
        for rel in relationships:
            # Create the relationship between a supplier and a product (SUPPLIES)
            session.run("""
                MATCH (s:Supplier {id: $supplier_id})
                MATCH (p:Product {id: $product_id})
                MERGE (s)-[:SUPPLIES]->(p)
            """, rel)

            # Create the relationship between a product and a warehouse (STORED_AT)
            session.run("""
                MATCH (p:Product {id: $product_id})
                MATCH (w:Warehouse {id: $warehouse_id})
                MERGE (p)-[:STORED_AT]->(w)
            """, rel)

# Function to load all data (products, suppliers, warehouses, routes, relationships)
def load_all_data():
    """Load all data into Neo4j in sequence."""
    print("Loading products...")
    load_products()  
    print("Loading suppliers...")
    load_suppliers()
    print("Loading warehouses...")
    load_warehouses()  
    print("Loading transportation routes...")
    load_transportation_routes()  
    print("Creating relationships...")
    create_relationships() 
    print("Data loading completed!") 


# Main script execution
if __name__ == "__main__":
    load_all_data()  # Call function to load all data
    driver.close()  # Close the Neo4j driver connection after loading the data
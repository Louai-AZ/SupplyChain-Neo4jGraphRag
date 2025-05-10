# SupplyChain-Neo4jGraphRag
A Graph RAG application using Neo4j as the knowledge graph and Gemini for text generation.


## Dataset Description

The dataset used in this project contains information about the supply chain, including products, suppliers, warehouses, transportation routes, and their relationships. The data is organized into the following categories:

- **Products**: This dataset contains details about various products, including product names, descriptions, prices, and categories.
- **Suppliers**: This dataset includes information about suppliers, including their names, locations, and areas of specialization.
- **Warehouses**: This dataset contains data about warehouses, including their names, locations, and capacities.
- **Transportation Routes**: This dataset includes routes between warehouses, with attributes like distance and duration.
- **Relationships**: This dataset captures the relationships between products, suppliers, and warehouses. Products are supplied by suppliers, and they are stored at specific warehouses.

---

## Knowledge Graph Design and Creation Process

The knowledge graph is designed to represent key entities in the supply chain and the relationships between them. The entities include:

- **Products**: Represented as nodes in the graph with properties such as name, description, price, and category. Each product also has a vector embedding for the product description.
- **Suppliers**: Represented as nodes with properties like name, location, and specialization. Suppliers are connected to products via `SUPPLIES` relationships.
- **Warehouses**: Represented as nodes with properties like name, location, and capacity. Warehouses are connected to products via `STORED_AT` relationships.
- **Transportation Routes**: Represented as relationships between warehouses, with attributes like distance and duration, to represent the transport links between storage locations.

### Process

- **Data Import**: The data from JSON files is loaded into Neo4j, where each entity is represented as a node.
- **Vector Embeddings**: Product descriptions are encoded using a pre-trained sentence transformer model (`all-MiniLM-L6-v2`) to create embeddings, which are stored in the graph.
- **Relationships**: Relationships between products, suppliers, and warehouses are established using `MERGE` operations in Cypher, with `SUPPLIES` and `STORED_AT` relationships.
- **Graph Indexing**: A vector index is created for the `description_embedding` property of the `Product` nodes, enabling efficient similarity searches based on product descriptions.

---

## Graph RAG Pipeline Implementation

The **RAG** pipeline in this application is composed of the following stages:

1. **Question Understanding**:  
   The user asks a question related to the supply chain, such as _"Where are the laptops stored?"_ or _"Which suppliers provide smartphones?"_

2. **Context Retrieval**:  
   The question is transformed into an embedding using the SentenceTransformer model (`all-MiniLM-L6-v2`). The embedding is then used to search for the most relevant context in the Neo4j knowledge graph by querying for products with similar descriptions.

3. **Answer Generation**:  
   Once relevant context is retrieved, the question and context are passed to the **Google Gemini** model, which generates a natural language answer based on the provided context.

4. **Response Display**:  
   The generated answer is displayed to the user via a **Streamlit** web interface.

The RAG pipeline works by combining retrieval from the knowledge graph and generation from a powerful language model, ensuring that answers are both accurate (based on the graph data) and fluent.


---


## Setup

1. Clone the repository:
```bash
git clone https://github.com/Louai-AZ/SupplyChain-Neo4jGraphRag
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```bash
cp .env.example .env
```

5. Edit the `.env` file with your credentials:
```
# Neo4j Database Configuration
NEO4J_URI=
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password

# Gemini API Configuration
GEMINI_API_KEY=your_api_key
```

---

## Testing the Setup

Before proceeding, verify your connections to Neo4j and Gemini:

```bash
python test_connection.py
```

This script will test both the Neo4j database connection and Gemini API connection. You should see success messages for both services.

---

## Loading Data

To load the sample data into Neo4j:

```bash
python load_data.py
```

This will:
- Create product nodes with vector embeddings
- Create supplier nodes
- Create warehouse nodes
- Create transportation routes
- Set up the necessary relationships

---

## Running the Application

To start the application:

```bash
streamlit run app.py
```

---

## Project Structure

- `load_data.py`: Script to load sample data into Neo4j
- `app.py`: Main RAG application
- `test_connection.py`: Script to verify Neo4j and Gemini connections
- `requirements.txt`: Python dependencies
- `.env.example`: Template for environment variables
- `.gitignore`: Specifies files to ignore in version control
import streamlit as st
from neo4j import GraphDatabase
from dotenv import load_dotenv
import os
import logging
import google.generativeai as genai
from sentence_transformers import SentenceTransformer

# Configure logging to track app activity and errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables from the .env file
load_dotenv()

# Initialize session state to track the conversation messages between user and assistant
if "messages" not in st.session_state:
    st.session_state.messages = []

# Set up the page configuration for the Streamlit app 
st.set_page_config(
    page_title="Supply Chain RAG Assistant",
    page_icon="📦",
    layout="wide"
)

# Retrieve Neo4j connection details from environment variables
uri = os.getenv("NEO4J_URI")
username = os.getenv("NEO4J_USERNAME")
password = os.getenv("NEO4J_PASSWORD")

# Initialize Gemini for text generation using the provided API key
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

# Load Sentence Transformer model for embedding-based comparison of questions and data
try:
    print("Loading model...")
    embedding_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
    print("Model loaded successfully")
except Exception as e:
    print(f"Error loading model: {e}")

# Function to retrieve relevant context from Neo4j based on the user's question
def get_relevant_context(question: str) -> str:
    """Retrieve relevant context from Neo4j based on the question."""
    try:
        # Connect to Neo4j using the provided connection details
        driver = GraphDatabase.driver(uri, auth=(username, password))

        with driver.session() as session:
            # Convert the user's question into an embedding for comparison
            question_embedding = embedding_model.encode(question).tolist()

            # Query Neo4j to find products with descriptions similar to the question embedding
            result = session.run("""
                MATCH (p:Product)
                WHERE p.description_embedding IS NOT NULL
                WITH p, 
                     reduce(s = 0, i in range(0, size(p.description_embedding)-1) | 
                           s + p.description_embedding[i] * $embedding[i]) as similarity
                ORDER BY similarity DESC
                LIMIT 3
                OPTIONAL MATCH (p)<-[:SUPPLIES]-(s:Supplier)
                OPTIONAL MATCH (p)-[:STORED_AT]->(w:Warehouse)
                RETURN p.name as product_name, 
                       p.description as product_description,
                       collect(DISTINCT {type: 'SUPPLIES', name: s.name}) as suppliers,
                       collect(DISTINCT {type: 'STORED_AT', name: w.name, location: w.location}) as warehouses
            """, embedding=question_embedding)

            # Format the query results into a readable context
            context = []
            for record in result:
                context.append(f"Product: {record['product_name']}")
                context.append(f"Description: {record['product_description']}")
                if record['suppliers']:
                    for supplier in record['suppliers']:
                        if supplier['name']:
                            context.append(f"Supplied by: {supplier['name']}")
                if record['warehouses']:
                    for warehouse in record['warehouses']:
                        if warehouse['name']:
                            context.append(f"Stored at: {warehouse['name']} in {warehouse['location']}")
                context.append("---")

            # Return the formatted context, or a message if no context was found
            return "\n".join(context) if context else "No relevant context found."

    except Exception as e:
        # Log and return error message in case of an exception
        logger.error(f"Error retrieving context: {e}")
        return "Error retrieving context."
    finally:
        if 'driver' in locals():
            driver.close()

# Function to generate a response using Google Gemini's generative AI model
def generate_gemini_response(context: str, question: str) -> str:
    """Generate a response using the Google Gemini model."""
    try:
        # Initialize the Gemini model and generate a response based on the context and question
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"Use the following context to answer the question.\n\nContext: {context}\nQuestion: {question}\nAnswer:")
        
        # Return the generated response if available, else return a fallback message
        if response and hasattr(response, 'text'):
            return response.text.strip()
        return "No response received from Gemini."
    except Exception as e:
        # Log and return error message if an error occurs during response generation
        logger.error(f"Error generating Gemini response: {e}")
        return "Error generating response."

# Streamlit UI: Title of the app
st.title("📦 Supply Chain RAG Assistant")

# Add sidebar with information about the app
with st.sidebar:
    st.header("About")
    st.write("""
    This application uses Neo4j and Google Gemini to answer questions about the supply chain.
    
    You can ask questions about:
    - Products and their descriptions
    - Suppliers and their locations
    - Warehouse locations and capacities
    - Product storage and distribution
    """)

    # Example questions for users to ask
    st.header("Example Questions")
    st.write("""
    - What products are available?
    - Where are the laptops stored?
    - Which suppliers provide smartphones?
    - What audio products are available?
    - Tell me about the supply chain for tablets
    """)

# Display the chat messages history (user and assistant messages)
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Accept user input for asking a question
if prompt := st.chat_input("Ask a question about the supply chain..."):
    # Add the user's message to the chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    # Display the user's message
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Retrieve relevant context from Neo4j based on the user's question
    context = get_relevant_context(prompt)
    
    # Generate and display the assistant's response using Gemini
    with st.chat_message("assistant"):
        response = generate_gemini_response(context, prompt)
        st.markdown(response)
    
    # Add the assistant's response to the chat history
    st.session_state.messages.append({"role": "assistant", "content": response})

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
import google.generativeai as genai

# Load environment variables
load_dotenv()

def test_neo4j_connection():
    """Test connection to Neo4j database"""
    try:
        uri = os.getenv("NEO4J_URI")
        username = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")

        driver = GraphDatabase.driver(uri, auth=(username, password))

        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            if result.single()["test"] == 1:
                print("✅ Neo4j connection successful!")
            else:
                print("❌ Neo4j connection failed: Unexpected result")
    except Exception as e:
        print(f"❌ Neo4j connection error: {str(e)}")
    finally:
        driver.close()


def test_gemini_connection():
    """Test connection to Google Gemini API"""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is not set")

        # Configure Gemini client
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello!")

        if response and hasattr(response, 'text'):
            print("✅ Gemini API connection successful!")
            print(f"Response: {response.text.strip()}")
        else:
            print("❌ Gemini API connection failed: No response received")
    except Exception as e:
        print(f"❌ Gemini API connection error: {str(e)}")


if __name__ == "__main__":
    print("Testing connections...")
    test_neo4j_connection()
    test_gemini_connection()

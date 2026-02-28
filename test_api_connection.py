"""
Test script to verify Claude API connection
Run this before using the main system
"""
import os
from dotenv import load_dotenv

def test_api_key():
    """Test if API key is properly configured"""
    
    print("="*60)
    print("🔍 TESTING API KEY CONNECTION")
    print("="*60)
    
    # Load environment variables
    load_dotenv()
    
    # Check if .env file exists
    if not os.path.exists(".env"):
        print("\n❌ ERROR: .env file not found!")
        print("\n📝 Create a .env file with:")
        print("   ANTHROPIC_API_KEY=your-api-key-here")
        return False
    
    # Check if API key is set
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        print("\n❌ ERROR: ANTHROPIC_API_KEY not found in .env file!")
        print("\n📝 Add this line to your .env file:")
        print("   ANTHROPIC_API_KEY=your-api-key-here")
        return False
    
    # Verify key format
    if not api_key.startswith("sk-ant-"):
        print(f"\n⚠️  WARNING: API key format looks incorrect")
        print(f"   Expected: sk-ant-...")
        print(f"   Got: {api_key[:10]}...")
        return False
    
    print(f"\n✅ API key found: {api_key[:15]}...{api_key[-4:]}")
    
    # Test actual connection
    print("\n🔄 Testing connection to Claude API...")
    
    try:
        from langchain_anthropic import ChatAnthropic
        from langchain_core.messages import HumanMessage
        
        # Create client
        llm = ChatAnthropic(
            model="claude-sonnet-4-20250514",
            temperature=0.1,
            api_key=api_key
        )
        
        # Send test message
        response = llm.invoke([
            HumanMessage(content="Reply with just the word 'SUCCESS' if you can read this.")
        ])
        
        print(f"\n✅ CONNECTION SUCCESSFUL!")
        print(f"   Model: claude-sonnet-4-20250514")
        print(f"   Response: {response.content[:50]}...")
        print("\n" + "="*60)
        print("✅ YOUR API KEY IS WORKING CORRECTLY!")
        print("="*60)
        return True
        
    except ImportError as e:
        print(f"\n❌ ERROR: Missing required package")
        print(f"   Run: pip install langchain-anthropic")
        return False
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to connect to Claude API")
        print(f"   Error: {str(e)}")
        print("\n🔧 Possible issues:")
        print("   1. API key is invalid or expired")
        print("   2. No internet connection")
        print("   3. Anthropic API is down")
        print("   4. Billing/quota issues with your API key")
        return False

if __name__ == "__main__":
    success = test_api_key()
    
    if success:
        print("\n✅ You can now run: python main.py --target_dir test_cases/case_new")
    else:
        print("\n❌ Fix the issues above before running the main system")

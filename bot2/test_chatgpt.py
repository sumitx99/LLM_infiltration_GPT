"""
Simple test script to analyze ChatGPT page elements
"""
import time
from bs4 import BeautifulSoup
from DrissionPage import ChromiumPage

def analyze_page(driver):
    """Analyze what elements are available on the ChatGPT page"""
    try:
        print("\n🔍 ANALYZING PAGE ELEMENTS...")
        print(f"📄 Page Title: {driver.title}")
        print(f"🌐 Page URL: {driver.url}")
        
        html = driver.html
        soup = BeautifulSoup(html, 'html.parser')
        
        # Check for different types of input elements
        textareas = soup.find_all('textarea')
        inputs = soup.find_all('input') 
        contenteditable = soup.find_all(attrs={'contenteditable': True})
        buttons = soup.find_all('button')
        
        print(f"\n📊 ELEMENT COUNTS:")
        print(f"   - Textareas: {len(textareas)}")
        print(f"   - Input fields: {len(inputs)}")
        print(f"   - Contenteditable elements: {len(contenteditable)}")
        print(f"   - Buttons: {len(buttons)}")
        
        print(f"\n📝 TEXTAREA DETAILS:")
        for i, textarea in enumerate(textareas):
            attrs = dict(textarea.attrs) if hasattr(textarea, 'attrs') else {}
            print(f"   Textarea {i+1}: {attrs}")
            
        print(f"\n✏️ CONTENTEDITABLE DETAILS:")
        for i, elem in enumerate(contenteditable):
            attrs = dict(elem.attrs) if hasattr(elem, 'attrs') else {}
            tag = elem.name if hasattr(elem, 'name') else 'unknown'
            print(f"   Element {i+1} ({tag}): {attrs}")
            
        print(f"\n🔍 INPUT FIELD DETAILS:")
        for i, inp in enumerate(inputs):
            attrs = dict(inp.attrs) if hasattr(inp, 'attrs') else {}
            print(f"   Input {i+1}: {attrs}")
            
        # Look for elements with specific text/placeholders
        print(f"\n🎯 ELEMENTS WITH RELEVANT TEXT:")
        elements_with_send = soup.find_all(string=lambda text: text and 'send' in text.lower())
        elements_with_message = soup.find_all(attrs={'placeholder': lambda x: x and 'message' in x.lower()})
        
        print(f"   Elements with 'send': {len(elements_with_send)}")
        print(f"   Elements with 'message' placeholder: {len(elements_with_message)}")
        
        for elem in elements_with_message:
            print(f"     - {elem.name}: {elem.attrs}")
        
        print(f"\n📄 HTML PREVIEW (first 1000 chars):")
        print(html[:1000])
        print("..." if len(html) > 1000 else "")
        
        print(f"\n✅ ANALYSIS COMPLETE")
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")

if __name__ == "__main__":
    print("🚀 ChatGPT Element Analyzer")
    print("=" * 50)
    
    # Setup browser
    driver = ChromiumPage()
    
    try:
        # Open ChatGPT
        print("🌐 Opening ChatGPT...")
        driver.get("https://chatgpt.com/")
        
        # Wait for manual login
        print("\n🔑 Please log in manually and navigate to the chat interface.")
        print("📍 Make sure you're on the main chat page where you can normally type messages.")
        input("✅ Press Enter when you're ready for analysis...")
        
        # Analyze the page
        analyze_page(driver)
        
        print("\n🎯 Testing element selectors...")
        selectors = [
            "tag:textarea",
            "[data-testid*='input']", 
            "[placeholder*='Send a message']",
            "[placeholder*='Message ChatGPT']",
            "[placeholder*='Message']",
            "#prompt-textarea",
            ".ProseMirror",
            "[contenteditable='true']"
        ]
        
        for selector in selectors:
            try:
                element = driver.ele(selector)
                if element:
                    print(f"✅ FOUND with selector: {selector}")
                else:
                    print(f"❌ NOT FOUND: {selector}")
            except Exception as e:
                print(f"❌ ERROR with {selector}: {e}")
        
        input("\nPress Enter to close browser...")
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        print("🔚 Closing browser...")
        driver.quit() 
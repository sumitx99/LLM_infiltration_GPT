import random
import time
import json
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from DrissionPage import ChromiumPage
from simple_vpn_integration import SimpleVPNManager

# === CONFIGURATION ===
PLATFORM_URL = "https://chatgpt.com/"  # Direct to chat interface
PROMPT_FILE = "prompt.json"
LOG_FILE = "logs.csv"
VPN_CONFIG_FILE = "vpn_config.json"

# === HELPER FUNCTIONS ===
def load_prompts():
    with open(PROMPT_FILE) as f:
        prompts = json.load(f)
        print(f"Loaded {len(prompts)} prompts from {PROMPT_FILE}")
        return prompts

def load_vpn_config():
    """Load VPN configuration from JSON file"""
    try:
        with open(VPN_CONFIG_FILE) as f:
            config = json.load(f)
            print(f"✅ Loaded VPN configuration for {config['vpn_provider'].upper()}")
            return config
    except FileNotFoundError:
        print(f"❌ VPN config file {VPN_CONFIG_FILE} not found")
        return None
    except Exception as e:
        print(f"❌ Error loading VPN config: {e}")
        return None

def initialize_simple_vpn():
    """Initialize Simple VPN management"""
    config = load_vpn_config()
    if not config:
        print("⚠️ No VPN configuration found, proceeding with basic setup")
        config = {
            'settings': {
                'auto_rotate': True,
                'rotation_interval': 5
            }
        }
    
    vpn_manager = SimpleVPNManager()
    
    print("🔍 Checking current IP...")
    initial_ip = vpn_manager.get_current_ip()
    print(f"📍 Current IP: {initial_ip['ip']} | Country: {initial_ip['country']}")
    
    return vpn_manager, config

def type_humanly(element, text, fast=True):
    if fast:
        element.input(text)
    else:
        for char in text:
            element.input(char)
            time.sleep(random.uniform(0.01, 0.03))

def log_session(platform, prompt, response):
    log_entry = {
        "platform": platform,
        "prompt": prompt,
        "response": response,
        "timestamp": datetime.now().isoformat()
    }
    try:
        try:
            df = pd.read_csv(LOG_FILE)
        except (FileNotFoundError, pd.errors.EmptyDataError):
            df = pd.DataFrame()

        df = pd.concat([df, pd.DataFrame([log_entry])], ignore_index=True)
        df.to_csv(LOG_FILE, index=False)
        print(f"📝 Logged session to {LOG_FILE}")
    except Exception as e:
        print(f"⚠️ Error logging session: {e}")

def wait_for_page_ready(driver, max_wait=60):
    print("⏳ Waiting for page to be ready...")

    for i in range(max_wait):
        try:
            title = driver.title
            url = driver.url
            print(f"🔍 Checking readiness - URL: {url}, Title: {title[:50]}...")

            # Check if we're on ChatGPT domain (be more flexible)
            if ("chatgpt.com" in url or "chat.openai.com" in url) and "Cloudflare" not in title:
                # Try multiple selectors for input elements
                selectors_to_try = [
                    "tag:textarea",
                    "[data-testid*='input']", 
                    "[placeholder*='Send a message']",
                    "[placeholder*='Message ChatGPT']",
                    "[placeholder*='Message']",
                    "#prompt-textarea",
                    ".ProseMirror",
                    "[contenteditable='true']"
                ]
                
                found_input = False
                for selector in selectors_to_try:
                    try:
                        input_box = driver.ele(selector)
                        if input_box:
                            print(f"✅ Page ready! Found input with selector: {selector}")
                            print(f"📄 Title: {title[:50]}...")
                            print(f"🌐 URL: {url}")
                            return True
                    except:
                        continue
                
                # If we've been trying for a while and still no input, show debug info
                if not found_input and i > 10 and i % 15 == 0:
                    print(f"⏳ Page loaded but no input found yet... ({i}/{max_wait}s)")
                    print("🔍 Running debug analysis...")
                    debug_page_elements(driver)

            if i % 10 == 0:
                print(f"⏳ Still waiting... ({i}/{max_wait}s) - {title[:30]}...")

            time.sleep(1)
        except Exception as e:
            if i % 15 == 0:
                print(f"⚠️ Page not ready yet: {e}")
            time.sleep(1)

    print("❌ Page did not become ready within timeout")
    print("🔍 Final debug analysis...")
    debug_page_elements(driver)
    return False

def find_and_type(driver, prompt_text):
    """Find input box, type prompt visibly, and submit"""
    try:
        print(f"📝 Typing prompt: {prompt_text[:50]}...")
        
        # Prioritized selectors based on current ChatGPT interface
        selectors = [
            "#prompt-textarea",          # Direct ID - most reliable
            ".ProseMirror",             # Rich text editor class
            "[contenteditable='true']", # Contenteditable div
            "tag:textarea",             # Fallback textarea
            "[data-testid*='input']",
            "[placeholder*='Send a message']",
            "[placeholder*='Message ChatGPT']",
            "[placeholder*='Message']"
        ]
        
        input_box = None
        successful_selector = None
        
        # Try different selectors
        for selector in selectors:
            print(f"🔍 Trying selector: {selector}")
            try:
                input_box = driver.ele(selector)
                if input_box:
                    successful_selector = selector
                    print(f"✅ Found input element with selector: {selector}")
                    break
            except Exception as e:
                print(f"❌ Selector {selector} failed: {e}")
                continue
        
        if not input_box:
            print("❌ No input element found with any selector")
            print("🔍 Running debug analysis...")
            debug_page_elements(driver)
            return False

        # Try to interact with the found element
        print(f"🎯 Attempting to interact with element using selector: {successful_selector}")
        
        # Wait a bit for any animations to complete
        time.sleep(2)
        
        try:
            # First try clicking to focus
            input_box.click()
            print("✅ Clicked on input element")
            time.sleep(1)
            
            # For contenteditable elements, we might need to handle them differently
            is_contenteditable = successful_selector in ["#prompt-textarea", ".ProseMirror", "[contenteditable='true']"]
            
            # Try different methods to input text
            input_success = False
            
            if is_contenteditable:
                print("🎯 Detected contenteditable element, using specialized methods...")
                try:
                    # Method 1: Direct input (works for most contenteditable)
                    input_box.input(prompt_text)
                    print(f"✅ Contenteditable input successful: {prompt_text[:30]}...")
                    input_success = True
                except Exception as e1:
                    print(f"❌ Contenteditable direct input failed: {e1}")
                    try:
                        # Method 2: Clear and type
                        input_box.clear()
                        time.sleep(0.5)
                        input_box.input(prompt_text)
                        print(f"✅ Contenteditable clear+input successful: {prompt_text[:30]}...")
                        input_success = True
                    except Exception as e2:
                        print(f"❌ Contenteditable clear+input failed: {e2}")
                        try:
                            # Method 3: Focus and send keys
                            input_box.focus()
                            time.sleep(0.5)
                            # Clear any existing text first
                            input_box.key('ctrl+a')
                            time.sleep(0.2)
                            input_box.key('Delete')
                            time.sleep(0.5)
                            # Type the text
                            input_box.type(prompt_text)
                            print(f"✅ Contenteditable keyboard input successful: {prompt_text[:30]}...")
                            input_success = True
                        except Exception as e3:
                            print(f"❌ Contenteditable keyboard input failed: {e3}")
            else:
                # Regular textarea handling
                try:
                    # Method 1: Direct input
                    input_box.input(prompt_text)
                    print(f"✅ Regular input successful: {prompt_text[:30]}...")
                    input_success = True
                except Exception as e1:
                    print(f"❌ Regular input failed: {e1}")
                    try:
                        # Method 2: Clear first, then input
                        input_box.clear()
                        time.sleep(0.5)
                        input_box.input(prompt_text)
                        print(f"✅ Regular clear+input successful: {prompt_text[:30]}...")
                        input_success = True
                    except Exception as e2:
                        print(f"❌ Regular clear+input failed: {e2}")
            
            if not input_success:
                print("❌ All input methods failed")
                return False
            
            # Wait a moment before submitting
            time.sleep(2)
            
            # Try to submit - multiple methods
            submit_success = False
            try:
                # Method 1: Send newline character using input method
                input_box.input('\n')
                print("📤 Method 1 - Submitted via newline input")
                submit_success = True
            except Exception as submit_e1:
                print(f"❌ Submit method 1 failed: {submit_e1}")
                try:
                    # Method 2: Try clicking submit/send button 
                    submit_selectors = [
                        "[data-testid='send-button']",
                        "button[aria-label*='Send']",
                        "button[type='submit']",
                        ".send-button",
                        "[aria-label*='Send message']",
                        "button:has-text('Send')",
                        "svg[data-testid='send-button']",
                        "[data-testid='fruitjuice-send-button']"
                    ]
                    
                    for submit_selector in submit_selectors:
                        try:
                            submit_btn = driver.ele(submit_selector)
                            if submit_btn:
                                submit_btn.click()
                                print(f"📤 Method 2 - Submitted via button: {submit_selector}")
                                submit_success = True
                                break
                        except:
                            continue
                            
                except Exception as submit_e2:
                    print(f"❌ Submit method 2 failed: {submit_e2}")
            
            if not submit_success:
                print("⚠️ Could not submit prompt, but text was entered")
                print("💡 Tip: The text might still be in the input box for manual submission")
                return False
                
            time.sleep(3)
            return True

        except Exception as interaction_e:
            print(f"❌ Element interaction failed: {interaction_e}")
            return False

    except Exception as e:
        print(f"❌ General error in find_and_type: {e}")
        return False

def wait_for_response(driver, timeout=90):
    try:
        print("⏳ Waiting for response...")
        
        # Wait a bit for the response to start generating
        time.sleep(3)
        
        response_started = False
        generation_complete = False
        
        for i in range(timeout):
            time.sleep(1)
            try:
                html = driver.html
                soup = BeautifulSoup(html, 'html.parser')
                
                # Look for response elements - ChatGPT uses various containers
                response_selectors = [
                    ".markdown p",  # Original selector
                    "[data-message-author-role='assistant']",  # New interface
                    ".prose p",  # Alternative
                    "[data-testid='conversation-turn-2']",  # Turn-based
                    ".group p",  # Group containers
                    ".message p"  # Generic message
                ]
                
                response_text = ""
                for selector in response_selectors:
                    elements = soup.select(selector)
                    if elements:
                        response_text = " ".join([elem.text for elem in elements])
                        break
                
                # Check if response has started
                if response_text.strip() and len(response_text.strip()) > 10:
                    if not response_started:
                        print("✅ Response generation started!")
                        response_started = True
                
                # Look for indicators that generation is complete
                if response_started:
                    # Check for "stop generating" button (indicates still generating)
                    stop_button = soup.find("button", string=lambda text: text and "stop" in text.lower())
                    regenerate_button = soup.find("button", string=lambda text: text and "regenerate" in text.lower())
                    
                    # Check if input field is enabled (usually disabled during generation)
                    input_selectors = ["#prompt-textarea", ".ProseMirror", "tag:textarea"]
                    input_enabled = False
                    for selector in input_selectors:
                        try:
                            input_element = driver.ele(selector)
                            if input_element:
                                # In modern ChatGPT, the input is usually disabled during generation
                                input_enabled = True
                                break
                        except:
                            continue
                    
                    # Response is likely complete if:
                    # 1. No stop button found AND regenerate button found, OR
                    # 2. Input field is enabled again, OR  
                    # 3. Response text hasn't changed for a few seconds
                    if (not stop_button and regenerate_button) or input_enabled:
                        if not generation_complete:
                            print("✅ Response generation appears complete!")
                            generation_complete = True
                            # Brief wait to ensure completion, then return immediately
                            time.sleep(1)
                            return response_text
                
                # Show progress every 10 seconds
                if i % 10 == 0 and i > 0:
                    status = "started" if response_started else "waiting to start"
                    print(f"⏳ Still waiting for response ({status})... ({i}/{timeout}s)")
                    if response_text:
                        print(f"📝 Current response length: {len(response_text)} chars")

            except Exception as e:
                if i % 15 == 0:
                    print(f"⚠️ Error checking response: {e}")
                continue

        if response_started:
            print(f"⚠️ Response timeout but got partial response: {len(response_text)} chars")
            return response_text
        else:
            print("⚠️ Response timeout - no response detected")
            return "No response received"

    except Exception as e:
        print(f"❌ Error waiting for response: {e}")
        return "Error getting response"

def debug_page_elements(driver):
    """Debug function to check what elements are available on the page"""
    try:
        print("\n🔍 DEBUG: Analyzing page elements...")
        html = driver.html
        soup = BeautifulSoup(html, 'html.parser')
        
        # Check for different types of input elements
        textareas = soup.find_all('textarea')
        inputs = soup.find_all('input') 
        contenteditable = soup.find_all(attrs={'contenteditable': True})
        buttons = soup.find_all('button')
        
        print(f"📊 Found: {len(textareas)} textarea(s), {len(inputs)} input(s), {len(contenteditable)} contenteditable, {len(buttons)} button(s)")
        
        # Show details of textareas
        for i, textarea in enumerate(textareas[:3]):  # Show first 3
            attrs = dict(textarea.attrs) if hasattr(textarea, 'attrs') else {}
            print(f"📝 Textarea {i+1}: {attrs}")
            
        # Show details of contenteditable elements  
        for i, elem in enumerate(contenteditable[:3]):
            attrs = dict(elem.attrs) if hasattr(elem, 'attrs') else {}
            print(f"✏️ Contenteditable {i+1}: {attrs}")
            
        # Look for send/submit buttons
        send_buttons = [btn for btn in buttons if 'send' in str(btn).lower() or 'submit' in str(btn).lower()]
        for i, btn in enumerate(send_buttons[:3]):
            attrs = dict(btn.attrs) if hasattr(btn, 'attrs') else {}
            print(f"📤 Send button {i+1}: {attrs}")
            
        print("🔍 DEBUG: Analysis complete\n")
        
    except Exception as e:
        print(f"⚠️ Debug analysis failed: {e}")

def is_chatgpt_generating(driver):
    """Check if ChatGPT is currently generating a response"""
    try:
        html = driver.html
        soup = BeautifulSoup(html, 'html.parser')
        
        # Look for indicators that ChatGPT is generating
        generating_indicators = [
            # Stop button present
            soup.find("button", string=lambda text: text and "stop" in text.lower()),
            # Loading indicators
            soup.select("[data-testid='stop-button']"),
            soup.select(".animate-spin"),  # Spinning loader
            soup.select("[aria-label*='Stop']"),
            # Input field disabled/aria-disabled
            soup.select("[aria-disabled='true']"),
        ]
        
        # If any indicator is found, ChatGPT is likely generating
        for indicator in generating_indicators:
            if indicator:
                return True
        
        # Check if input field is disabled by trying to interact with it
        try:
            input_element = driver.ele("#prompt-textarea") or driver.ele(".ProseMirror")
            if input_element:
                # If we can't interact with it, it might be disabled
                return False
        except:
            return True  # If we can't access it, assume it's busy
            
        return False
        
    except Exception as e:
        print(f"⚠️ Error checking generation status: {e}")
        return False

def wait_for_generation_complete(driver, max_wait=15):
    """Wait for ChatGPT to finish generating before proceeding"""
    print("🔍 Quick check if ChatGPT is generating...")
    
    for i in range(max_wait):
        if not is_chatgpt_generating(driver):
            print("✅ ChatGPT is ready to receive new prompt")
            return True
        
        if i % 3 == 0 and i > 0:
            print(f"⏳ ChatGPT still generating, waiting... ({i}/{max_wait}s)")
        time.sleep(1)
    
    print("⚠️ Proceeding anyway - generation check timeout")
    return False

# === MAIN LOOP ===
if __name__ == "__main__":
    prompts = load_prompts()
    
    # Initialize Simple VPN
    vpn_setup = initialize_simple_vpn()
    vpn_manager = None
    vpn_config = None
    
    if vpn_setup:
        vpn_manager, vpn_config = vpn_setup
        print("🌐 VPN Manager initialized successfully!")
        
        # Create browser with first profile
        print("🔄 Creating browser with isolated profile...")
        driver = vpn_manager.create_browser_with_profile("chatgpt_session_1")
        
        if driver:
            print("✅ Browser created successfully!")
        else:
            print("❌ Failed to create browser, using regular browser")
            vpn_manager = None
            driver = ChromiumPage()
    else:
        print("⚠️ Proceeding without VPN management")
        vpn_manager = None
        driver = ChromiumPage()

    try:
        # Open ChatGPT
        print("🌐 Opening ChatGPT...")
        driver.get(PLATFORM_URL)

        # Wait for manual login if needed
        print("🔍 Please log in manually if not already logged in.")
        input("✅ Press Enter when you're logged in and on the chat page...")

        # Now wait for ChatGPT to be ready
        if not wait_for_page_ready(driver, max_wait=90):
            print("❌ Could not access ChatGPT. Please check manually.")
            exit(1)

        # Debug: Show what elements are available
        debug_page_elements(driver)

        print("🚀 Starting automatic prompt sending...")

        # Start automatic prompting
        prompt_count = 0
        max_prompts = 50
        failed_attempts = 0
        max_failures = 3

        while prompt_count < max_prompts and failed_attempts < max_failures:
            # VPN rotation logic (with manual VPN change option)
            if vpn_manager and vpn_config['settings']['auto_rotate']:
                rotation_interval = vpn_config['settings']['rotation_interval']
                if prompt_count > 0 and prompt_count % rotation_interval == 0:
                    print(f"\n🔄 Time to rotate session (every {rotation_interval} prompts)...")
                    
                    # Prompt user for manual VPN change
                    vpn_changed = vpn_manager.prompt_for_vpn_change()
                    
                    # Always rotate browser session for isolation
                    print("🔄 Rotating browser session for better isolation...")
                    
                    new_driver = vpn_manager.rotate_session(driver)
                    
                    if new_driver:
                        driver = new_driver
                        
                        # Verify current connection
                        vpn_manager.verify_connection(driver)
                        
                        # Re-navigate to ChatGPT
                        print("🌐 Opening ChatGPT in new session...")
                        driver.get(PLATFORM_URL)
                        
                        # Wait for page to be ready
                        if not wait_for_page_ready(driver, max_wait=30):
                            print("❌ ChatGPT not ready after rotation")
                            continue
                            
                        print("✅ ChatGPT ready in new session!")
                        
                        if vpn_changed:
                            print("✅ Session rotated with new VPN location!")
                        else:
                            print("✅ Session rotated successfully!")
                    else:
                        print("❌ Session rotation failed, creating new browser")
                        driver = ChromiumPage()
                        driver.get(PLATFORM_URL)
            
            # Quick check for any ongoing generation before sending new prompt
            wait_for_generation_complete(driver, max_wait=10)
            
            prompt_data = random.choice(prompts)
            prompt_text = prompt_data["prompt"]

            print(f"\n[PROMPT {prompt_count + 1}/{max_prompts}]")
            print(f"Category: {prompt_data['category']} | Persona: {prompt_data['persona']}")
            if vpn_manager and vpn_manager.current_profile:
                print(f"🌍 Session: {vpn_manager.current_profile}")

            if not find_and_type(driver, prompt_text):
                print("❌ Prompt input failed, skipping session.")
                failed_attempts += 1
                if failed_attempts < max_failures:
                    print("🔄 Retrying in 10 seconds...")
                    time.sleep(10)
                continue

            response = wait_for_response(driver, timeout=90)
            log_session(PLATFORM_URL, prompt_text, response)

            print(f"✅ Session {prompt_count + 1} completed successfully!")

            failed_attempts = 0
            prompt_count += 1

            # Wait longer between prompts to ensure ChatGPT is ready
            delay = random.uniform(15, 25)
            print(f"⏳ Waiting {delay:.1f}s before next prompt...")
            time.sleep(delay)
            
            # Additional check: ensure input field is ready before next prompt
            print("🔍 Ensuring input field is ready for next prompt...")
            input_ready = False
            for attempt in range(10):
                try:
                    input_box = driver.ele("#prompt-textarea") or driver.ele(".ProseMirror")
                    if input_box:
                        # Try to click and check if it's responsive
                        input_box.click()
                        time.sleep(1)
                        input_ready = True
                        break
                except:
                    print(f"⏳ Input field not ready, waiting... (attempt {attempt + 1}/10)")
                    time.sleep(2)
            
            if not input_ready:
                print("⚠️ Input field not responding, but continuing...")
            else:
                print("✅ Input field is ready for next prompt")

        if failed_attempts >= max_failures:
            print(f"⚠️ Stopped after {prompt_count} prompts due to failures")
        else:
            print(f"\n🎉 Successfully completed all {prompt_count} prompts!")

    except KeyboardInterrupt:
        print("\n⚠️ Script stopped by user")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        print("🔚 Cleaning up...")
        
        # Note: Browser sessions will be closed automatically
        if vpn_manager:
            print("🔌 Browser sessions will be closed...")
        
        # Close browser
        print("🔚 Closing browser...")
        try:
            driver.quit()
        except:
            pass  # Ignore errors if browser already closed
        
        print("✅ Cleanup complete!")
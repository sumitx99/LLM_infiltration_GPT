"""
Simple VPN Integration for ChatGPT Automation
Works with any VPN client through browser profile rotation
"""

import random
import time
import requests
import os
import json
from typing import Dict, List, Optional
from DrissionPage import ChromiumPage

class SimpleVPNManager:
    def __init__(self):
        self.current_country = None
        self.current_profile = None
        self.rotation_count = 0
        
        # Countries for rotation tracking
        self.countries = {
            "us": "United States",
            "uk": "United Kingdom", 
            "ca": "Canada",
            "de": "Germany",
            "fr": "France",
            "jp": "Japan",
            "au": "Australia",
            "nl": "Netherlands"
        }
        
        # Browser profiles directory
        self.profiles_dir = os.path.join(os.getcwd(), "browser_profiles")
        self.ensure_profiles_dir()
    
    def ensure_profiles_dir(self):
        """Create profiles directory"""
        if not os.path.exists(self.profiles_dir):
            os.makedirs(self.profiles_dir)
    
    def get_current_ip(self):
        """Get current IP info"""
        try:
            response = requests.get("http://ip-api.com/json/", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    "ip": data.get("query"),
                    "country": data.get("country"),
                    "country_code": data.get("countryCode", "").lower(),
                    "city": data.get("city"),
                    "isp": data.get("isp")
                }
        except Exception as e:
            print(f"⚠️ Error getting IP: {e}")
        return {"ip": "Unknown", "country": "Unknown"}
    
    def create_browser_with_profile(self, profile_name: str):
        """Create browser with isolated profile"""
        try:
            profile_path = os.path.join(self.profiles_dir, f"profile_{profile_name}")
            
            # Use ChromiumOptions for proper configuration
            from DrissionPage import ChromiumOptions
            
            options = ChromiumOptions()
            options.set_user_data_path(profile_path)
            options.set_argument('--disable-blink-features=AutomationControlled')
            options.set_argument('--disable-extensions') 
            options.set_argument('--window-size=1920,1080')
            options.set_argument('--no-sandbox')
            options.set_argument('--disable-dev-shm-usage')
            
            driver = ChromiumPage(addr_or_opts=options)
            self.current_profile = profile_name
            
            return driver
            
        except Exception as e:
            print(f"❌ Error creating browser: {e}")
            return None
    
    def rotate_session(self, driver):
        """Rotate to new browser session"""
        try:
            print("\n🔄 Rotating browser session...")
            
            if driver:
                driver.quit()
                time.sleep(2)
            
            self.rotation_count += 1
            profile_name = f"session_{self.rotation_count}"
            
            new_driver = self.create_browser_with_profile(profile_name)
            
            if new_driver:
                print("✅ Session rotated successfully!")
                return new_driver
            else:
                print("❌ Failed to rotate session")
                return None
                
        except Exception as e:
            print(f"❌ Error rotating: {e}")
            return None
    
    def verify_connection(self, driver):
        """Check current IP"""
        try:
            print("🔍 Checking connection...")
            driver.get("http://ip-api.com/json/")
            time.sleep(3)
            
            page_text = driver.html
            if "query" in page_text:
                start = page_text.find('{')
                end = page_text.rfind('}') + 1
                json_str = page_text[start:end]
                data = json.loads(json_str)
                
                ip = data.get("query")
                country = data.get("country")
                city = data.get("city")
                isp = data.get("isp")
                
                print(f"📍 IP: {ip}")
                print(f"🌍 Location: {city}, {country}")
                print(f"🏢 ISP: {isp}")
                
                return True
        except Exception as e:
            print(f"❌ Error verifying: {e}")
        return False
    
    def prompt_for_vpn_change(self):
        """Ask user if they want to manually change VPN"""
        print("\n🔄 VPN Rotation Point!")
        print("💡 You can manually change your VPN location now")
        print("   (Open ExpressVPN/PIA and connect to different server)")
        
        choice = input("Change VPN location? (y/n): ").strip().lower()
        if choice == 'y':
            input("✅ Connect to different VPN server, then press Enter...")
            return True
        return False

if __name__ == "__main__":
    print("=== Simple VPN Test ===")
    
    manager = SimpleVPNManager()
    
    # Show current IP
    ip_info = manager.get_current_ip()
    print(f"Current IP: {ip_info['ip']} | Country: {ip_info['country']}")
    
    # Test browser creation
    driver = manager.create_browser_with_profile("test")
    if driver:
        print("✅ Browser created!")
        manager.verify_connection(driver)
        driver.quit()
    else:
        print("❌ Browser creation failed") 
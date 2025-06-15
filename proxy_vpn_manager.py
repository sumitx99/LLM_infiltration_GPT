"""
Proxy-based VPN Manager for ChatGPT Automation
Works by configuring browser proxy settings instead of system-wide VPN
"""

import random
import requests
import time
from typing import Dict, List, Optional
from DrissionPage import ChromiumPage

class ProxyVPNManager:
    def __init__(self):
        self.current_proxy = None
        self.current_country = None
        
        # Free proxy services (you can replace with premium proxy services)
        # Format: "ip:port" or "ip:port:username:password" for authenticated proxies
        self.proxy_servers = {
            "us": [
                "51.81.80.44:8080",
                "47.88.87.74:1080",
                "104.248.90.212:80",
                "159.65.69.186:9300",
            ],
            "uk": [
                "139.59.179.147:8080",
                "46.101.49.62:80",
                "178.62.92.63:80",
            ],
            "ca": [
                "159.203.61.169:3128",
                "142.93.179.27:8080",
            ],
            "de": [
                "138.68.60.8:8080",
                "167.172.180.40:41491",
            ],
            "fr": [
                "51.178.49.77:3128",
                "147.135.255.62:8123",
            ],
            "nl": [
                "185.162.251.76:80",
                "194.5.207.148:3128",
            ],
            "jp": [
                "133.18.231.31:8080",
                "150.230.216.58:80",
            ]
        }
        
        # Country names mapping
        self.countries = {
            "us": "United States",
            "uk": "United Kingdom",
            "ca": "Canada", 
            "de": "Germany",
            "fr": "France",
            "nl": "Netherlands",
            "jp": "Japan"
        }
    
    def get_current_ip(self) -> Dict:
        """Get current IP address and location info"""
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
            print(f"⚠️ Error getting IP info: {e}")
            
        return {"ip": "Unknown", "country": "Unknown", "country_code": "unknown"}
    
    def test_proxy(self, proxy: str, timeout: int = 10) -> bool:
        """Test if a proxy is working"""
        try:
            proxy_dict = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
            }
            
            response = requests.get(
                "http://httpbin.org/ip", 
                proxies=proxy_dict, 
                timeout=timeout
            )
            
            if response.status_code == 200:
                return True
        except:
            pass
        
        return False
    
    def get_working_proxy(self, country_code: str) -> Optional[str]:
        """Get a working proxy for the specified country"""
        if country_code not in self.proxy_servers:
            print(f"❌ No proxies available for {country_code}")
            return None
        
        proxies = self.proxy_servers[country_code].copy()
        random.shuffle(proxies)  # Random order
        
        print(f"🔍 Testing proxies for {self.countries.get(country_code, country_code)}...")
        
        for proxy in proxies:
            print(f"   Testing {proxy}...")
            if self.test_proxy(proxy, timeout=8):
                print(f"   ✅ {proxy} is working!")
                return proxy
            else:
                print(f"   ❌ {proxy} failed")
        
        print(f"❌ No working proxies found for {country_code}")
        return None
    
    def create_browser_with_proxy(self, country_code: str) -> Optional[ChromiumPage]:
        """Create a new browser instance with proxy for specified country"""
        proxy = self.get_working_proxy(country_code)
        if not proxy:
            return None
        
        try:
            # Create Chrome options with proxy
            options = {
                'proxy': f'http://{proxy}',
                'args': [
                    f'--proxy-server=http://{proxy}',
                    '--ignore-certificate-errors',
                    '--disable-web-security',
                    '--allow-running-insecure-content'
                ]
            }
            
            print(f"🌐 Creating browser with {self.countries.get(country_code, country_code)} proxy...")
            driver = ChromiumPage(addr_or_opts=options)
            
            self.current_proxy = proxy
            self.current_country = country_code
            
            return driver
            
        except Exception as e:
            print(f"❌ Error creating browser with proxy: {e}")
            return None
    
    def verify_proxy_connection(self, driver: ChromiumPage) -> bool:
        """Verify the proxy connection by checking IP"""
        try:
            print("🔍 Verifying proxy connection...")
            
            # Navigate to IP checking service
            driver.get("http://ip-api.com/json/")
            time.sleep(3)
            
            # Get the JSON response
            page_text = driver.html
            
            if "query" in page_text:
                # Parse the response
                import json
                try:
                    # Extract JSON from page
                    start = page_text.find('{')
                    end = page_text.rfind('}') + 1
                    json_str = page_text[start:end]
                    data = json.loads(json_str)
                    
                    ip = data.get("query")
                    country = data.get("country")
                    country_code = data.get("countryCode", "").lower()
                    city = data.get("city")
                    isp = data.get("isp")
                    
                    print(f"📍 Proxy IP: {ip}")
                    print(f"🌍 Location: {city}, {country}")
                    print(f"🏢 ISP: {isp}")
                    
                    # Check if country matches expected
                    if self.current_country and country_code:
                        expected = self.current_country.lower()
                        actual = country_code.lower()
                        
                        if expected == actual:
                            print("✅ Proxy connection verified successfully!")
                            return True
                        else:
                            print(f"⚠️ Country mismatch: Expected {expected}, got {actual}")
                            return False
                    
                    return True
                    
                except json.JSONDecodeError:
                    print("⚠️ Could not parse IP response")
                    return False
            else:
                print("⚠️ Could not get IP information")
                return False
                
        except Exception as e:
            print(f"❌ Error verifying proxy: {e}")
            return False
    
    def rotate_proxy(self, driver: ChromiumPage, exclude_current: bool = True) -> bool:
        """Rotate to a different proxy/country"""
        available_countries = list(self.countries.keys())
        
        if exclude_current and self.current_country:
            available_countries = [c for c in available_countries if c != self.current_country]
        
        if not available_countries:
            print("❌ No countries available for rotation")
            return False
        
        new_country = random.choice(available_countries)
        print(f"🔄 Rotating to {self.countries[new_country]}...")
        
        # Get new proxy
        new_proxy = self.get_working_proxy(new_country)
        if not new_proxy:
            return False
        
        try:
            # Update proxy settings (this requires restarting the browser)
            print("⚠️ Proxy rotation requires browser restart...")
            return False  # Will need to create new browser instance
            
        except Exception as e:
            print(f"❌ Error rotating proxy: {e}")
            return False
    
    def get_random_country(self, exclude_current: bool = True) -> str:
        """Get a random country code"""
        available_countries = list(self.countries.keys())
        
        if exclude_current and self.current_country:
            available_countries = [c for c in available_countries if c != self.current_country]
        
        return random.choice(available_countries) if available_countries else "us"

class PremiumProxyManager(ProxyVPNManager):
    """Enhanced proxy manager for premium proxy services"""
    
    def __init__(self, proxy_service: str = "smartproxy"):
        super().__init__()
        self.proxy_service = proxy_service
        
        # Premium proxy endpoints (you'll need to sign up for these services)
        self.premium_endpoints = {
            "smartproxy": {
                "endpoint": "gate.smartproxy.com:7000",
                "auth_required": True,
                "countries": {
                    "us": "gate.smartproxy.com:10000",
                    "uk": "gate.smartproxy.com:10001", 
                    "ca": "gate.smartproxy.com:10002",
                    "de": "gate.smartproxy.com:10003",
                    "fr": "gate.smartproxy.com:10004",
                    "jp": "gate.smartproxy.com:10005",
                }
            },
            "brightdata": {
                "endpoint": "brd.superproxy.io:22225",
                "auth_required": True,
                "format": "username-session-{session}:password@endpoint"
            }
        }
    
    def create_premium_browser(self, country_code: str, username: str, password: str) -> Optional[ChromiumPage]:
        """Create browser with premium proxy service"""
        if self.proxy_service not in self.premium_endpoints:
            print(f"❌ Unsupported proxy service: {self.proxy_service}")
            return None
        
        service_config = self.premium_endpoints[self.proxy_service]
        
        if self.proxy_service == "smartproxy":
            endpoint = service_config["countries"].get(country_code, service_config["endpoint"])
            proxy_url = f"http://{username}:{password}@{endpoint}"
        else:
            # Other services
            proxy_url = f"http://{username}:{password}@{service_config['endpoint']}"
        
        try:
            options = {
                'proxy': proxy_url,
                'args': [
                    f'--proxy-server={proxy_url}',
                    '--ignore-certificate-errors'
                ]
            }
            
            driver = ChromiumPage(addr_or_opts=options)
            self.current_country = country_code
            return driver
            
        except Exception as e:
            print(f"❌ Error creating premium proxy browser: {e}")
            return None

# Test function
def test_proxy_connection():
    """Test proxy-based VPN functionality"""
    print("=== Proxy VPN Test ===")
    
    proxy_manager = ProxyVPNManager()
    
    # Show current IP
    print("🔍 Current IP without proxy:")
    ip_info = proxy_manager.get_current_ip()
    print(f"IP: {ip_info['ip']} | Country: {ip_info['country']}")
    
    # Test different countries
    countries_to_test = ["us", "uk", "de"]
    
    for country in countries_to_test:
        print(f"\n--- Testing {country.upper()} Proxy ---")
        
        # Create browser with proxy
        driver = proxy_manager.create_browser_with_proxy(country)
        
        if driver:
            print(f"✅ Browser created with {country.upper()} proxy")
            
            # Verify connection
            if proxy_manager.verify_proxy_connection(driver):
                print(f"✅ {country.upper()} proxy verified!")
            else:
                print(f"⚠️ {country.upper()} proxy verification failed")
            
            # Close browser
            driver.quit()
            time.sleep(2)
        else:
            print(f"❌ Failed to create browser with {country.upper()} proxy")

if __name__ == "__main__":
    test_proxy_connection() 
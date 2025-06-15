"""
VPN Manager for ChatGPT Automation
Supports multiple VPN providers and country rotation
"""

import subprocess
import time
import random
import requests
from typing import List, Dict, Optional

class VPNManager:
    def __init__(self, vpn_type="pia", username=None, password=None):
        self.vpn_type = vpn_type.lower()
        self.current_country = None
        self.current_server = None
        self.username = username
        self.password = password
        
        # Common country codes and their full names for PIA
        self.countries = {
            "us": "United States",
            "uk": "United Kingdom", 
            "ca": "Canada",
            "de": "Germany",
            "fr": "France",
            "jp": "Japan",
            "au": "Australia",
            "nl": "Netherlands",
            "se": "Sweden",
            "ch": "Switzerland",
            "it": "Italy",
            "es": "Spain",
            "br": "Brazil",
            "in": "India",
            "sg": "Singapore",
            "mx": "Mexico",
            "be": "Belgium",
            "at": "Austria",
            "dk": "Denmark",
            "fi": "Finland",
            "no": "Norway",
            "ie": "Ireland",
            "is": "Iceland",
            "ro": "Romania",
            "cz": "Czech Republic",
            "hu": "Hungary",
            "pl": "Poland"
        }
        
        # PIA server regions mapping
        self.pia_regions = {
            "us": ["us-east", "us-west", "us-central", "us-chicago", "us-newyork", "us-california"],
            "uk": ["uk-london", "uk-manchester", "uk-southampton"],
            "ca": ["ca-toronto", "ca-montreal", "ca-vancouver"],
            "de": ["de-berlin", "de-frankfurt"],
            "fr": ["france"],
            "jp": ["japan"],
            "au": ["au-melbourne", "au-perth", "au-sydney"],
            "nl": ["netherlands"],
            "se": ["sweden"],
            "ch": ["switzerland"],
            "it": ["italy"],
            "es": ["spain"],
            "br": ["brazil"],
            "in": ["india"],
            "sg": ["singapore"],
            "mx": ["mexico"],
            "be": ["belgium"],
            "at": ["austria"],
            "dk": ["denmark"],
            "fi": ["finland"],
            "no": ["norway"],
            "ie": ["ireland"],
            "is": ["iceland"],
            "ro": ["romania"],
            "cz": ["czech"],
            "hu": ["hungary"],
            "pl": ["poland"]
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
                    "country_code": data.get("countryCode"),
                    "city": data.get("city"),
                    "isp": data.get("isp")
                }
        except Exception as e:
            print(f"⚠️ Error getting IP info: {e}")
            
        return {"ip": "Unknown", "country": "Unknown"}
    
    def connect_nordvpn(self, country_code: str) -> bool:
        """Connect to NordVPN server in specified country"""
        try:
            print(f"🌐 Connecting to NordVPN server in {self.countries.get(country_code, country_code)}...")
            
            # Disconnect first
            subprocess.run(["nordvpn", "disconnect"], capture_output=True, text=True)
            time.sleep(2)
            
            # Connect to specific country
            result = subprocess.run(
                ["nordvpn", "connect", country_code], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✅ Successfully connected to NordVPN - {country_code}")
                self.current_country = country_code
                return True
            else:
                print(f"❌ Failed to connect to NordVPN: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ NordVPN connection timeout")
            return False
        except Exception as e:
            print(f"❌ Error connecting to NordVPN: {e}")
            return False
    
    def connect_expressvpn(self, country_code: str) -> bool:
        """Connect to ExpressVPN server in specified country"""
        try:
            print(f"🌐 Connecting to ExpressVPN server in {self.countries.get(country_code, country_code)}...")
            
            # Disconnect first
            subprocess.run(["expressvpn", "disconnect"], capture_output=True, text=True)
            time.sleep(2)
            
            # Connect to specific country
            result = subprocess.run(
                ["expressvpn", "connect", country_code], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if "Connected" in result.stdout:
                print(f"✅ Successfully connected to ExpressVPN - {country_code}")
                self.current_country = country_code
                return True
            else:
                print(f"❌ Failed to connect to ExpressVPN: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error connecting to ExpressVPN: {e}")
            return False
    
    def connect_surfshark(self, country_code: str) -> bool:
        """Connect to Surfshark VPN server in specified country"""
        try:
            print(f"🌐 Connecting to Surfshark server in {self.countries.get(country_code, country_code)}...")
            
            # Disconnect first
            subprocess.run(["surfshark-vpn", "down"], capture_output=True, text=True)
            time.sleep(2)
            
            # Connect to specific country
            result = subprocess.run(
                ["surfshark-vpn", "attack", country_code], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✅ Successfully connected to Surfshark - {country_code}")
                self.current_country = country_code
                return True
            else:
                print(f"❌ Failed to connect to Surfshark: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error connecting to Surfshark: {e}")
            return False
    
    def connect_pia(self, country_code: str) -> bool:
        """Connect to Private Internet Access (PIA) VPN server in specified country"""
        try:
            print(f"🌐 Connecting to PIA server in {self.countries.get(country_code, country_code)}...")
            
            if not self.username or not self.password:
                print("❌ PIA credentials not provided")
                return False
            
            # Disconnect first
            try:
                subprocess.run(["piactl", "disconnect"], capture_output=True, text=True, timeout=10)
            except:
                pass  # Ignore disconnect errors
            time.sleep(2)
            
            # Login to PIA first
            login_result = subprocess.run(
                ["piactl", "login", self.username], 
                input=self.password,
                text=True,
                capture_output=True, 
                timeout=15
            )
            
            if login_result.returncode != 0:
                print(f"❌ PIA login failed: {login_result.stderr}")
                return False
            
            print("✅ Successfully logged into PIA")
            
            # Get available regions for the country
            available_regions = self.pia_regions.get(country_code, [country_code])
            selected_region = random.choice(available_regions)
            
            print(f"🎯 Connecting to PIA region: {selected_region}")
            
            # Connect to specific region
            connect_result = subprocess.run(
                ["piactl", "connect", "--region", selected_region], 
                capture_output=True, 
                text=True, 
                timeout=30
            )
            
            if connect_result.returncode == 0:
                print(f"✅ Successfully connected to PIA - {selected_region}")
                self.current_country = country_code
                self.current_server = selected_region
                return True
            else:
                print(f"❌ Failed to connect to PIA: {connect_result.stderr}")
                
                # Try alternative connection method
                print("🔄 Trying alternative PIA connection method...")
                alt_result = subprocess.run(
                    ["piactl", "set", "region", selected_region], 
                    capture_output=True, 
                    text=True, 
                    timeout=15
                )
                
                if alt_result.returncode == 0:
                    connect_result2 = subprocess.run(
                        ["piactl", "connect"], 
                        capture_output=True, 
                        text=True, 
                        timeout=30
                    )
                    
                    if connect_result2.returncode == 0:
                        print(f"✅ Successfully connected to PIA (alternative method) - {selected_region}")
                        self.current_country = country_code
                        self.current_server = selected_region
                        return True
                
                return False
                
        except subprocess.TimeoutExpired:
            print("❌ PIA connection timeout")
            return False
        except Exception as e:
            print(f"❌ Error connecting to PIA: {e}")
            return False
    
    def connect_to_country(self, country_code: str) -> bool:
        """Connect to VPN server in specified country based on VPN type"""
        country_code = country_code.lower()
        
        if country_code not in self.countries:
            print(f"❌ Unsupported country code: {country_code}")
            return False
        
        print(f"🔄 Switching to VPN server in {self.countries[country_code]}...")
        
        if self.vpn_type == "pia":
            return self.connect_pia(country_code)
        elif self.vpn_type == "nordvpn":
            return self.connect_nordvpn(country_code)
        elif self.vpn_type == "expressvpn":
            return self.connect_expressvpn(country_code)
        elif self.vpn_type == "surfshark":
            return self.connect_surfshark(country_code)
        else:
            print(f"❌ Unsupported VPN type: {self.vpn_type}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from VPN"""
        try:
            print("🔌 Disconnecting from VPN...")
            
            if self.vpn_type == "pia":
                result = subprocess.run(["piactl", "disconnect"], capture_output=True, text=True)
            elif self.vpn_type == "nordvpn":
                result = subprocess.run(["nordvpn", "disconnect"], capture_output=True, text=True)
            elif self.vpn_type == "expressvpn":
                result = subprocess.run(["expressvpn", "disconnect"], capture_output=True, text=True)
            elif self.vpn_type == "surfshark":
                result = subprocess.run(["surfshark-vpn", "down"], capture_output=True, text=True)
            else:
                return False
            
            if result.returncode == 0:
                print("✅ Successfully disconnected from VPN")
                self.current_country = None
                return True
            else:
                print(f"❌ Failed to disconnect: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error disconnecting from VPN: {e}")
            return False
    
    def get_random_country(self, exclude_current=True) -> str:
        """Get a random country code, optionally excluding current"""
        available_countries = list(self.countries.keys())
        
        if exclude_current and self.current_country:
            available_countries = [c for c in available_countries if c != self.current_country]
        
        return random.choice(available_countries)
    
    def rotate_country(self) -> bool:
        """Rotate to a random different country"""
        new_country = self.get_random_country(exclude_current=True)
        return self.connect_to_country(new_country)
    
    def verify_connection(self) -> bool:
        """Verify VPN connection by checking IP"""
        print("🔍 Verifying VPN connection...")
        
        # Wait a moment for connection to stabilize
        time.sleep(3)
        
        ip_info = self.get_current_ip()
        print(f"📍 Current IP: {ip_info['ip']}")
        print(f"🌍 Location: {ip_info['city']}, {ip_info['country']}")
        print(f"🏢 ISP: {ip_info['isp']}")
        
        # Basic check: if country matches expected
        if self.current_country and ip_info.get('country_code'):
            expected_country = self.current_country.upper()
            actual_country = ip_info['country_code'].upper()
            
            if expected_country == actual_country:
                print("✅ VPN connection verified successfully!")
                return True
            else:
                print(f"⚠️ Country mismatch: Expected {expected_country}, got {actual_country}")
                return False
        
        return True

class ProxyVPNManager:
    """Alternative VPN manager using proxy servers"""
    
    def __init__(self):
        self.current_proxy = None
        
        # Example proxy servers (you'll need to get real ones)
        self.proxy_servers = {
            "us": ["proxy-us-1.example.com:8080", "proxy-us-2.example.com:8080"],
            "uk": ["proxy-uk-1.example.com:8080", "proxy-uk-2.example.com:8080"],
            "de": ["proxy-de-1.example.com:8080", "proxy-de-2.example.com:8080"],
            "fr": ["proxy-fr-1.example.com:8080", "proxy-fr-2.example.com:8080"],
            "jp": ["proxy-jp-1.example.com:8080", "proxy-jp-2.example.com:8080"],
        }
    
    def get_proxy_for_country(self, country_code: str) -> Optional[str]:
        """Get a random proxy server for the specified country"""
        if country_code in self.proxy_servers:
            return random.choice(self.proxy_servers[country_code])
        return None
    
    def get_chrome_proxy_args(self, country_code: str) -> List[str]:
        """Get Chrome arguments for proxy configuration"""
        proxy = self.get_proxy_for_country(country_code)
        if proxy:
            return [f"--proxy-server=http://{proxy}"]
        return []

# Example usage and testing functions
def test_vpn_connection():
    """Test VPN connection and IP verification"""
    vpn = VPNManager("pia", "p8551263", "Eoxs12345!")  # Using PIA credentials
    
    print("=== VPN Connection Test ===")
    
    # Show current IP
    print("\n🔍 Current IP before VPN:")
    ip_info = vpn.get_current_ip()
    print(f"IP: {ip_info['ip']} | Country: {ip_info['country']}")
    
    # Connect to different countries
    countries_to_test = ["us", "uk", "de"]
    
    for country in countries_to_test:
        print(f"\n--- Testing {country.upper()} ---")
        if vpn.connect_to_country(country):
            if vpn.verify_connection():
                print(f"✅ {country.upper()} connection successful!")
            else:
                print(f"⚠️ {country.upper()} connection issue detected")
        else:
            print(f"❌ Failed to connect to {country.upper()}")
        
        time.sleep(5)  # Wait between connections
    
    # Disconnect
    vpn.disconnect()

if __name__ == "__main__":
    test_vpn_connection() 
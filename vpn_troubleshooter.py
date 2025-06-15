"""
VPN Troubleshooter - Diagnose VPN Connection Issues
"""

import time
import requests
import subprocess
import json
from simple_vpn_integration import SimpleVPNManager

class VPNTroubleshooter:
    def __init__(self):
        self.vpn_manager = SimpleVPNManager()
        self.original_ip = None
        
    def get_detailed_ip_info(self):
        """Get detailed IP information from multiple sources"""
        print("🔍 Checking IP from multiple sources...")
        
        sources = {
            "ip-api.com": "http://ip-api.com/json/",
            "ipify.org": "https://api.ipify.org?format=json",
            "httpbin.org": "https://httpbin.org/ip",
            "whatismyipaddress.com": "https://ipv4bot.whatismyipaddress.com/",
        }
        
        results = {}
        
        for source_name, url in sources.items():
            try:
                print(f"  📡 Checking {source_name}...")
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200:
                    if source_name == "ip-api.com":
                        data = response.json()
                        results[source_name] = {
                            "ip": data.get("query"),
                            "country": data.get("country"),
                            "city": data.get("city"),
                            "isp": data.get("isp"),
                            "region": data.get("regionName")
                        }
                    elif source_name == "ipify.org":
                        data = response.json()
                        results[source_name] = {"ip": data.get("ip")}
                    elif source_name == "httpbin.org":
                        data = response.json()
                        results[source_name] = {"ip": data.get("origin")}
                    elif source_name == "whatismyipaddress.com":
                        results[source_name] = {"ip": response.text.strip()}
                else:
                    results[source_name] = {"error": f"HTTP {response.status_code}"}
                    
            except Exception as e:
                results[source_name] = {"error": str(e)}
        
        return results
    
    def display_ip_results(self, results):
        """Display IP check results"""
        print("\n" + "="*60)
        print("📊 IP CHECK RESULTS")
        print("="*60)
        
        ips = []
        for source, data in results.items():
            if "error" in data:
                print(f"❌ {source}: {data['error']}")
            else:
                ip = data.get("ip", "N/A")
                ips.append(ip)
                
                if source == "ip-api.com" and "country" in data:
                    print(f"✅ {source}:")
                    print(f"   📍 IP: {ip}")
                    print(f"   🌍 Country: {data.get('country', 'N/A')}")
                    print(f"   🏙️ City: {data.get('city', 'N/A')}")
                    print(f"   🏢 ISP: {data.get('isp', 'N/A')}")
                else:
                    print(f"✅ {source}: {ip}")
        
        # Check if all IPs are the same
        unique_ips = list(set([ip for ip in ips if ip and ip != "N/A"]))
        
        if len(unique_ips) == 1:
            print(f"\n✅ All sources show same IP: {unique_ips[0]}")
        elif len(unique_ips) > 1:
            print(f"\n⚠️ Different IPs detected: {unique_ips}")
            print("   This might indicate DNS leaks or proxy issues")
        
        return results
    
    def check_expressvpn_status(self):
        """Check ExpressVPN connection status"""
        print("\n🔍 Checking ExpressVPN status...")
        
        try:
            # Try to get ExpressVPN status using command line
            result = subprocess.run(
                ["powershell", "-Command", "Get-Process | Where-Object {$_.ProcessName -like '*express*'}"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if "ExpressVPN" in result.stdout or "expressvpn" in result.stdout.lower():
                print("✅ ExpressVPN process is running")
                
                # Try to check connection status
                print("💡 To check ExpressVPN status:")
                print("   1. Open ExpressVPN app")
                print("   2. Look for 'Connected' status")
                print("   3. Note which server/country you're connected to")
                
                return True
            else:
                print("❌ ExpressVPN process not found")
                print("💡 Please start ExpressVPN application")
                return False
                
        except Exception as e:
            print(f"⚠️ Could not check ExpressVPN status: {e}")
            return None
    
    def check_dns_leaks(self):
        """Check for DNS leaks"""
        print("\n🔍 Checking for DNS leaks...")
        
        try:
            # Check DNS servers
            result = subprocess.run(
                ["nslookup", "google.com"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                dns_info = result.stdout
                print("📡 DNS Lookup result:")
                print(dns_info[:300] + "..." if len(dns_info) > 300 else dns_info)
                
                # Check if DNS contains local/ISP servers
                if "BHARTI" in dns_info.upper() or "122.173" in dns_info:
                    print("⚠️ Possible DNS leak detected - using local ISP DNS")
                    return False
                else:
                    print("✅ DNS appears to be routed through VPN")
                    return True
            else:
                print("❌ DNS lookup failed")
                return None
                
        except Exception as e:
            print(f"⚠️ DNS check failed: {e}")
            return None
    
    def test_vpn_connection_steps(self):
        """Step-by-step VPN connection test"""
        print("\n" + "="*60)
        print("🧪 VPN CONNECTION TEST")
        print("="*60)
        
        # Step 1: Check initial IP
        print("\n📍 STEP 1: Current IP (before VPN)")
        print("-" * 40)
        initial_results = self.get_detailed_ip_info()
        self.display_ip_results(initial_results)
        self.original_ip = initial_results.get("ip-api.com", {}).get("ip")
        
        # Step 2: Check VPN software status
        print("\n🔧 STEP 2: VPN Software Status")
        print("-" * 40)
        vpn_running = self.check_expressvpn_status()
        
        # Step 3: Manual VPN connection
        print("\n🌐 STEP 3: Connect to VPN")
        print("-" * 40)
        print("Please follow these steps:")
        print("1. Open ExpressVPN application")
        print("2. If not connected, click the power button to connect")
        print("3. Click on 'Choose Location'")
        print("4. Select a country (e.g., United States, Germany, etc.)")
        print("5. Wait for 'Connected' status")
        
        input("\n✅ Press Enter when ExpressVPN shows 'Connected' to a foreign server...")
        
        # Step 4: Test after connection
        print("\n📍 STEP 4: IP After VPN Connection")
        print("-" * 40)
        time.sleep(3)  # Wait for connection to stabilize
        new_results = self.get_detailed_ip_info()
        self.display_ip_results(new_results)
        
        # Step 5: Compare results
        print("\n🔍 STEP 5: Comparison")
        print("-" * 40)
        old_ip = initial_results.get("ip-api.com", {}).get("ip")
        new_ip = new_results.get("ip-api.com", {}).get("ip")
        old_country = initial_results.get("ip-api.com", {}).get("country")
        new_country = new_results.get("ip-api.com", {}).get("country")
        
        print(f"Before VPN: {old_ip} ({old_country})")
        print(f"After VPN:  {new_ip} ({new_country})")
        
        if old_ip != new_ip:
            print("✅ SUCCESS: IP address changed!")
            print("✅ VPN is working correctly")
            return True
        else:
            print("❌ ISSUE: IP address did not change")
            print("❌ VPN may not be working properly")
            return False
    
    def provide_troubleshooting_tips(self):
        """Provide troubleshooting tips"""
        print("\n" + "="*60)
        print("🛠️ TROUBLESHOOTING TIPS")
        print("="*60)
        
        print("If your IP is not changing:")
        print()
        print("1. 🔌 RESTART EXPRESSVPN:")
        print("   • Close ExpressVPN completely")
        print("   • Restart the application")
        print("   • Try connecting again")
        print()
        print("2. 🌐 TRY DIFFERENT SERVERS:")
        print("   • If US doesn't work, try UK or Germany")
        print("   • Some servers might be blocked or slow")
        print()
        print("3. 🔄 CHANGE CONNECTION PROTOCOL:")
        print("   • In ExpressVPN: Settings → Protocol")
        print("   • Try 'Automatic' or 'OpenVPN UDP'")
        print()
        print("4. 🛡️ DISABLE OTHER VPN/PROXY:")
        print("   • Turn off any browser extensions with VPN")
        print("   • Disable Windows proxy settings")
        print()
        print("5. 🔥 CHECK FIREWALL:")
        print("   • Windows Firewall might block VPN")
        print("   • Add ExpressVPN to firewall exceptions")
        print()
        print("6. 🌍 DNS SETTINGS:")
        print("   • In ExpressVPN: Settings → DNS")
        print("   • Enable 'Use ExpressVPN's DNS servers'")
        print()
        print("7. 📱 CONTACT SUPPORT:")
        print("   • ExpressVPN has 24/7 chat support")
        print("   • They can help with connection issues")
    
    def quick_fix_suggestions(self):
        """Quick fix suggestions"""
        print("\n" + "="*40)
        print("⚡ QUICK FIXES TO TRY")
        print("="*40)
        print("1. Disconnect and reconnect ExpressVPN")
        print("2. Try a different server location")
        print("3. Restart your internet connection")
        print("4. Restart ExpressVPN application")
        print("5. Choose 'Automatic' location in ExpressVPN")
        print("="*40)

def main():
    """Main troubleshooting function"""
    troubleshooter = VPNTroubleshooter()
    
    print("🔧 VPN Troubleshooter")
    print("=" * 40)
    print("This tool will help diagnose VPN connection issues")
    print()
    
    while True:
        print("\n📋 TROUBLESHOOTING OPTIONS:")
        print("1. 🧪 Full VPN connection test")
        print("2. 🔍 Quick IP check")
        print("3. 📡 Check ExpressVPN status")
        print("4. 🌐 Check DNS leaks")
        print("5. 💡 Show troubleshooting tips")
        print("6. ⚡ Quick fix suggestions")
        print("0. ❌ Exit")
        
        choice = input("\n🔢 Choose option: ").strip()
        
        if choice == "1":
            troubleshooter.test_vpn_connection_steps()
        elif choice == "2":
            results = troubleshooter.get_detailed_ip_info()
            troubleshooter.display_ip_results(results)
        elif choice == "3":
            troubleshooter.check_expressvpn_status()
        elif choice == "4":
            troubleshooter.check_dns_leaks()
        elif choice == "5":
            troubleshooter.provide_troubleshooting_tips()
        elif choice == "6":
            troubleshooter.quick_fix_suggestions()
        elif choice == "0":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main() 
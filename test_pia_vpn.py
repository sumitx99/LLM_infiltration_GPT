"""
Test script for PIA VPN functionality
"""

import time
from vpn_manager import VPNManager

def test_pia_connection():
    """Test PIA VPN connection with your credentials"""
    print("=== PIA VPN Test ===")
    
    # Initialize with your PIA credentials
    vpn = VPNManager("pia", "p8551263", "Eoxs12345!")
    
    # Show current IP before VPN
    print("\n🔍 Current IP before VPN:")
    ip_info = vpn.get_current_ip()
    print(f"IP: {ip_info['ip']} | Country: {ip_info['country']} | ISP: {ip_info['isp']}")
    
    # Test different countries
    countries_to_test = ["us", "uk", "ca", "de", "fr"]
    
    for country in countries_to_test:
        print(f"\n--- Testing {country.upper()} Connection ---")
        
        if vpn.connect_to_country(country):
            print(f"✅ Connected to {country.upper()}")
            
            # Verify connection
            if vpn.verify_connection():
                print(f"✅ {country.upper()} connection verified!")
            else:
                print(f"⚠️ {country.upper()} connection issues detected")
            
            # Wait a bit before next test
            time.sleep(3)
        else:
            print(f"❌ Failed to connect to {country.upper()}")
    
    # Test rotation functionality
    print("\n--- Testing VPN Rotation ---")
    for i in range(3):
        print(f"\nRotation {i+1}/3:")
        if vpn.rotate_country():
            print("✅ VPN rotation successful")
            vpn.verify_connection()
        else:
            print("❌ VPN rotation failed")
        time.sleep(2)
    
    # Disconnect
    print("\n--- Disconnecting ---")
    if vpn.disconnect():
        print("✅ Successfully disconnected from VPN")
        
        # Check IP after disconnect
        print("\n🔍 IP after disconnecting VPN:")
        final_ip = vpn.get_current_ip()
        print(f"IP: {final_ip['ip']} | Country: {final_ip['country']} | ISP: {final_ip['isp']}")
    else:
        print("❌ Failed to disconnect from VPN")

def quick_connection_test():
    """Quick test for single country connection"""
    print("=== Quick PIA Connection Test ===")
    
    vpn = VPNManager("pia", "p8551263", "Eoxs12345!")
    
    print("🔍 Before VPN:")
    before_ip = vpn.get_current_ip()
    print(f"IP: {before_ip['ip']} | Country: {before_ip['country']}")
    
    # Connect to US
    print("\n🌐 Connecting to US server...")
    if vpn.connect_to_country("us"):
        print("✅ Connected to US!")
        
        print("🔍 After VPN:")
        after_ip = vpn.get_current_ip()
        print(f"IP: {after_ip['ip']} | Country: {after_ip['country']}")
        
        # Test if IP changed
        if before_ip['ip'] != after_ip['ip']:
            print("✅ IP successfully changed!")
        else:
            print("⚠️ IP didn't change - possible VPN issue")
    
    # Disconnect
    vpn.disconnect()

if __name__ == "__main__":
    choice = input("Choose test:\n1. Full VPN test\n2. Quick connection test\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_pia_connection()
    elif choice == "2":
        quick_connection_test()
    else:
        print("Invalid choice, running quick test...")
        quick_connection_test() 
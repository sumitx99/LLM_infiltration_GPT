"""
VPN Country Switcher - Manual VPN Location Changer
Works with ExpressVPN, PIA, or any VPN client
"""

import time
import requests
import json
from simple_vpn_integration import SimpleVPNManager

class VPNCountrySwitcher:
    def __init__(self):
        self.vpn_manager = SimpleVPNManager()
        
        # Popular VPN countries with their common server names
        self.vpn_countries = {
            "1": {"code": "us", "name": "United States", "servers": ["USA - Los Angeles", "USA - New York", "USA - Chicago", "USA - Miami"]},
            "2": {"code": "uk", "name": "United Kingdom", "servers": ["UK - London", "UK - Wembley", "UK - East London"]},
            "3": {"code": "ca", "name": "Canada", "servers": ["Canada - Toronto", "Canada - Vancouver", "Canada - Montreal"]},
            "4": {"code": "de", "name": "Germany", "servers": ["Germany - Frankfurt", "Germany - Berlin", "Germany - Nuremberg"]},
            "5": {"code": "fr", "name": "France", "servers": ["France - Paris", "France - Strasbourg"]},
            "6": {"code": "jp", "name": "Japan", "servers": ["Japan - Tokyo", "Japan - Yokohama"]},
            "7": {"code": "au", "name": "Australia", "servers": ["Australia - Sydney", "Australia - Melbourne", "Australia - Perth"]},
            "8": {"code": "nl", "name": "Netherlands", "servers": ["Netherlands - Amsterdam", "Netherlands - Rotterdam"]},
            "9": {"code": "se", "name": "Sweden", "servers": ["Sweden - Stockholm"]},
            "10": {"code": "ch", "name": "Switzerland", "servers": ["Switzerland - Zurich"]},
            "11": {"code": "sg", "name": "Singapore", "servers": ["Singapore"]},
            "12": {"code": "br", "name": "Brazil", "servers": ["Brazil - Sao Paulo"]},
            "13": {"code": "in", "name": "India", "servers": ["India - Mumbai", "India - Chennai"]},
            "14": {"code": "it", "name": "Italy", "servers": ["Italy - Milan", "Italy - Rome"]},
            "15": {"code": "es", "name": "Spain", "servers": ["Spain - Madrid", "Spain - Barcelona"]},
        }
    
    def get_current_location(self):
        """Get current IP and location"""
        print("🔍 Checking current location...")
        ip_info = self.vpn_manager.get_current_ip()
        
        print(f"📍 Current IP: {ip_info['ip']}")
        print(f"🌍 Country: {ip_info['country']}")
        print(f"🏙️ City: {ip_info['city']}")
        print(f"🏢 ISP: {ip_info['isp']}")
        
        return ip_info
    
    def show_country_menu(self):
        """Display available countries menu"""
        print("\n" + "="*60)
        print("🌍 AVAILABLE VPN COUNTRIES")
        print("="*60)
        
        for key, country in self.vpn_countries.items():
            print(f"{key:2}. 🌍 {country['name']} ({country['code'].upper()})")
        
        print("\n 0. ❌ Exit")
        print("="*60)
    
    def show_vpn_instructions(self, country_info):
        """Show instructions for connecting to specific country"""
        print(f"\n🔧 VPN CONNECTION INSTRUCTIONS for {country_info['name']}")
        print("="*60)
        print("📱 For ExpressVPN:")
        print("  1. Open ExpressVPN app")
        print("  2. Click on the location button")
        print(f"  3. Search for and select: {country_info['name']}")
        print("  4. Choose one of these servers:")
        for server in country_info['servers']:
            print(f"     • {server}")
        print("  5. Click Connect")
        print()
        print("🔒 For PIA VPN:")
        print("  1. Open PIA app")
        print("  2. Click on location dropdown")
        print(f"  3. Select: {country_info['name']}")
        print("  4. Click Connect")
        print()
        print("🌐 For Other VPN Apps:")
        print("  1. Open your VPN app")
        print(f"  2. Connect to a server in: {country_info['name']}")
        print("="*60)
    
    def wait_for_connection(self, target_country):
        """Wait for user to connect and verify"""
        input(f"\n✅ Press Enter when connected to {target_country['name']}...")
        
        print("\n⏳ Verifying new connection...")
        time.sleep(2)
        
        # Check new location
        new_location = self.get_current_location()
        
        # Simple verification - check if country changed
        expected_country = target_country['name'].lower()
        actual_country = new_location['country'].lower()
        
        if expected_country in actual_country or actual_country in expected_country:
            print(f"\n✅ SUCCESS! Connected to {new_location['country']}")
            return True
        else:
            print(f"\n⚠️ Location might not have changed properly")
            print(f"Expected: {target_country['name']}")
            print(f"Detected: {new_location['country']}")
            
            retry = input("Try again? (y/n): ").lower().strip()
            return retry != 'y'
    
    def quick_country_switch(self, country_code):
        """Quick switch to specific country"""
        # Find country by code
        target_country = None
        for country in self.vpn_countries.values():
            if country['code'] == country_code.lower():
                target_country = country
                break
        
        if not target_country:
            print(f"❌ Country code '{country_code}' not found")
            return False
        
        print(f"\n🔄 Quick switch to {target_country['name']}")
        self.show_vpn_instructions(target_country)
        return self.wait_for_connection(target_country)
    
    def interactive_country_selector(self):
        """Interactive country selection menu"""
        while True:
            # Show current location
            print("\n" + "="*60)
            print("🌍 CURRENT LOCATION")
            print("="*60)
            self.get_current_location()
            
            # Show menu
            self.show_country_menu()
            
            # Get user choice
            try:
                choice = input("\n🔢 Enter country number (or 0 to exit): ").strip()
                
                if choice == "0":
                    print("👋 Goodbye!")
                    break
                
                if choice not in self.vpn_countries:
                    print("❌ Invalid choice. Please try again.")
                    continue
                
                target_country = self.vpn_countries[choice]
                
                print(f"\n🎯 Selected: {target_country['name']}")
                self.show_vpn_instructions(target_country)
                
                if self.wait_for_connection(target_country):
                    print(f"\n🎉 Successfully connected to {target_country['name']}!")
                    
                    # Ask if user wants to continue or test ChatGPT
                    next_action = input("\nWhat's next?\n1. Change to another country\n2. Test with ChatGPT\n3. Exit\nChoice (1/2/3): ").strip()
                    
                    if next_action == "2":
                        self.launch_chatgpt_test()
                        break
                    elif next_action == "3":
                        break
                    # Continue loop for option 1
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")
    
    def launch_chatgpt_test(self):
        """Launch ChatGPT automation with current VPN"""
        print("\n🚀 Launching ChatGPT automation...")
        print("💡 Make sure you're logged into ChatGPT in your browser first!")
        
        proceed = input("Ready to start ChatGPT automation? (y/n): ").lower().strip()
        if proceed == 'y':
            print("🔄 Starting main.py...")
            import subprocess
            try:
                subprocess.run(["python", "main.py"], check=True)
            except Exception as e:
                print(f"❌ Error launching main.py: {e}")
        else:
            print("✅ You can run 'python main.py' manually when ready")
    
    def random_country_rotation(self, num_rotations=3):
        """Randomly rotate through countries"""
        import random
        
        print(f"\n🎲 Random Country Rotation ({num_rotations} countries)")
        print("="*60)
        
        # Get random countries
        available_countries = list(self.vpn_countries.values())
        random.shuffle(available_countries)
        selected_countries = available_countries[:num_rotations]
        
        print("🗂️ Selected countries for rotation:")
        for i, country in enumerate(selected_countries, 1):
            print(f"  {i}. {country['name']}")
        
        print("\n🔄 Starting rotation...")
        
        for i, country in enumerate(selected_countries, 1):
            print(f"\n--- Rotation {i}/{num_rotations}: {country['name']} ---")
            self.show_vpn_instructions(country)
            
            if not self.wait_for_connection(country):
                print("❌ Rotation failed, stopping...")
                break
            
            if i < len(selected_countries):
                print(f"⏳ Waiting 10 seconds before next rotation...")
                time.sleep(10)
        
        print("\n✅ Random rotation completed!")

def main():
    """Main function"""
    switcher = VPNCountrySwitcher()
    
    print("🌍 VPN Country Switcher")
    print("="*40)
    print("This tool helps you manually switch VPN countries")
    print("and verify the connection changes.")
    print()
    
    while True:
        print("\n📋 OPTIONS:")
        print("1. 🌍 Interactive country selector")
        print("2. ⚡ Quick switch (enter country code)")
        print("3. 🎲 Random country rotation")
        print("4. 🔍 Just check current location")
        print("5. 🚀 Launch ChatGPT automation")
        print("0. ❌ Exit")
        
        choice = input("\n🔢 Choose an option: ").strip()
        
        if choice == "1":
            switcher.interactive_country_selector()
        elif choice == "2":
            country_code = input("Enter country code (us/uk/ca/de/fr/jp/au/nl/etc.): ").strip()
            switcher.quick_country_switch(country_code)
        elif choice == "3":
            num = input("How many countries to rotate through? (default 3): ").strip()
            try:
                num = int(num) if num else 3
                switcher.random_country_rotation(num)
            except ValueError:
                print("❌ Invalid number, using default (3)")
                switcher.random_country_rotation(3)
        elif choice == "4":
            switcher.get_current_location()
        elif choice == "5":
            switcher.launch_chatgpt_test()
        elif choice == "0":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main() 
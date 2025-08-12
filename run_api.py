#!/usr/bin/env python3
"""
Simple startup script for iMarketPredict Stock API
"""
import subprocess
import sys
import time
import requests

def test_api_endpoint(url, timeout=5):
    """Test if API endpoint is responding"""
    try:
        response = requests.get(url, timeout=timeout)
        return response.status_code == 200
    except:
        return False

def main():
    print("=== iMarketPredict Stock API Launcher ===\n")
    
    print("Choose an option:")
    print("1. Run Full API (with database)")
    print("2. Run Test API (no database required)")
    print("3. Auto-detect and run best option")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice == "1":
        print("\nStarting Full API...")
        try:
            subprocess.run([sys.executable, "main.py"], check=True)
        except KeyboardInterrupt:
            print("\nAPI stopped by user")
        except Exception as e:
            print(f"\nFull API failed: {e}")
            print("Try running: python test_api.py")
    
    elif choice == "2":
        print("\nStarting Test API...")
        try:
            subprocess.run([sys.executable, "test_api.py"], check=True)
        except KeyboardInterrupt:
            print("\nAPI stopped by user")
        except Exception as e:
            print(f"\nTest API failed: {e}")
    
    elif choice == "3":
        print("\nAuto-detecting best option...")
        
        # Try to start main API
        print("Attempting to start Full API...")
        try:
            process = subprocess.Popen([sys.executable, "main.py"])
            
            # Wait a bit for startup
            time.sleep(3)
            
            # Test if it's working
            if test_api_endpoint("http://localhost:8000/health"):
                print("✓ Full API is running successfully!")
                print("API available at: http://localhost:8000")
                print("Test with: http://localhost:8000/stock/AAPL/latest")
                print("\nPress Ctrl+C to stop the API")
                
                try:
                    process.wait()
                except KeyboardInterrupt:
                    process.terminate()
                    print("\nAPI stopped")
            else:
                print("✗ Full API failed to start properly")
                process.terminate()
                
                # Try test API
                print("\nTrying Test API...")
                subprocess.run([sys.executable, "test_api.py"], check=True)
                
        except Exception as e:
            print(f"Full API failed: {e}")
            print("\nTrying Test API...")
            try:
                subprocess.run([sys.executable, "test_api.py"], check=True)
            except Exception as e2:
                print(f"Test API also failed: {e2}")
                print("\nTroubleshooting:")
                print("1. Check if port 8000 is available")
                print("2. Verify all dependencies are installed: pip install -r requirements.txt")
                print("3. Check the logs for specific errors")
    
    else:
        print("Invalid choice. Please run the script again.")

if __name__ == "__main__":
    main()

import requests
import sys

# --- CONFIGURATION ---
LOCAL_URL = "http://127.0.0.1:8000/api/auth/validate-arn"
API_KEY = "3d4c5eb8-9fe0-4458-882d-5750d9a78947"
PAYLOAD = {"arn": "arn:aws:iam::100731996973:user/HackathonUser"}

def run_diagnostics():
    print("🔍 --- CLOUDCFO BACKEND DIAGNOSTICS ---")
    
    # 1. PING ROOT (TRY MULTIPLE HOSTS)
    print("\n[STEP 1] Heartbeat Check...")
    hosts_to_try = ["127.0.0.1:8000", "localhost:8000", "0.0.0.0:8000"]
    connected_url = None
    
    for host in hosts_to_try:
        try:
            url = f"http://{host}/"
            print(f"📡 Probing {url}...")
            root_resp = requests.get(url, timeout=2)
            print(f"✅ Success! Backend found on {host}: {root_resp.status_code}")
            connected_url = f"http://{host}"
            break
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection Refused on {host}")
        except requests.exceptions.Timeout:
            print(f"❌ Connection Timeout on {host}")
        except Exception as e:
            print(f"❌ Error on {host}: {type(e).__name__}")

    if not connected_url:
        print(f"\n❌ CRITICAL: Could not reach backend on any local host. Is uvicorn running?")
        print("   If you see 'Started server process' in your uvicorn terminal, check if its on port 8000.")
        return

    # 2. TEST AUTH LOGIC
    print("\n[STEP 2] IAM Validation Check...")
    auth_url = f"{connected_url}/api/auth/validate-arn"
    headers = {"X-API-KEY": API_KEY}
    try:
        auth_resp = requests.post(LOCAL_URL, json=PAYLOAD, headers=headers, timeout=5)
        if auth_resp.status_code == 200:
            print(f"✅ Auth Logic PASS: {auth_resp.status_code} - Authorized")
        else:
            print(f"❌ Auth Logic FAIL: {auth_resp.status_code} - {auth_resp.text}")
            print(f"   (Check if your backend matches API_KEY: {API_KEY})")
    except Exception as e:
        print(f"❌ Local Connection Error: {e}")

    # 3. TEST TUNNEL (IF URL PROVIDED)
    print("\n[STEP 3] Optional Tunnel Bridge Check...")
    print("If you have a Localtunnel URL, enter it here (or press Enter to skip):")
    tunnel_input = input("> ").strip()
    
    if tunnel_input:
        if not tunnel_input.startswith("http"):
            tunnel_input = f"https://{tunnel_input}"
        
        tunnel_url = f"{tunnel_input.rstrip('/')}/api/auth/validate-arn"
        headers["bypass-tunnel-reminder"] = "true"
        
        print(f"🌉 Testing Bridge: {tunnel_url}...")
        try:
            t_resp = requests.post(tunnel_url, json=PAYLOAD, headers=headers, timeout=10)
            print(f"✅ Tunnel Success: {t_resp.status_code} - {t_resp.json()}")
        except Exception as e:
            print(f"❌ Tunnel Breakdown: {e}")
            print("   (This usually means the tunnel is blocked by your firewall or it has expired.)")

if __name__ == "__main__":
    run_diagnostics()

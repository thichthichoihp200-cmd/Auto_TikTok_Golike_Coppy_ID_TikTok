import time
import requests
import sys
import warnings

warnings.filterwarnings("ignore")

class Color:
    RED="\033[1;91m"; GREEN="\033[1;92m"; YELLOW="\033[1;93m"
    BLUE="\033[1;94m"; PURPLE="\033[1;95m"; CYAN="\033[1;96m"
    RESET="\033[0m"; ORANGE="\033[38;5;208m"

API_BASE = "https://gateway.golike.net/api"
session = requests.Session()
session.headers.update({"User-Agent": "Mozilla/5.0"})

def rq(m, u, **k):
    try:
        r = session.request(m, u, timeout=10, **k)
        if r.status_code == 200: return r.json()
    except: pass
    return None

def get_acc(h): return rq("GET", f"{API_BASE}/tiktok-account", headers=h)
def get_job(h, id): return rq("GET", f"{API_BASE}/advertising/publishers/tiktok/jobs", headers=h, params={"account_id": id})
def complete(h, jid, id): return rq("POST", f"{API_BASE}/advertising/publishers/tiktok/complete-jobs", headers=h, json={"ads_id": jid, "account_id": id})

# Hàm Bỏ qua Job mới theo API report/send
def report_skip(h, d, acc_id):
    try:
        payload = {
            "description": "Tôi không muốn làm Job này",
            "users_advertising_id": d.get("id"),
            "type": "ads",
            "provider": "tiktok",
            "fb_id": acc_id,
            "error_type": 0
        }
        session.post(f"{API_BASE}/report/send", headers=h, json=payload, timeout=10)
    except: pass

def load():
    auth_file = "Authorization.txt"; token_file = "token.txt"
    open(auth_file, "a").close(); open(token_file, "a").close()
    a = open(auth_file).read().strip(); t = open(token_file).read().strip()
    if a and t:
        check = input(f"{Color.CYAN}Dùng Token Cũ? (Enter=OK, 'n'=Nhập mới): {Color.RESET}")
        if check == "": return a, t
    a = input(f"{Color.YELLOW}Nhập Authorization: {Color.RESET}")
    t = input(f"{Color.YELLOW}Nhập Token: {Color.RESET}")
    open(auth_file, "w").write(a); open(token_file, "w").write(t)
    return a, t

def main():
    print(f"\n{Color.PURPLE}=== TOOL GOLIKE MANUAL FOLLOW (V3.5) ==={Color.RESET}")
    auth, token = load()
    h = {"Authorization": auth, "t": token}

    while True:
        accs = get_acc(h)
        if not accs or "data" not in accs:
            print(f"{Color.RED}❌ Lỗi: Không lấy được tài khoản.{Color.RESET}"); return
        
        print(f"\n{Color.CYAN}--- DANH SÁCH TÀI KHOẢN ---{Color.RESET}")
        for i, a in enumerate(accs["data"], 1):
            print(f"{Color.YELLOW}{i}. {Color.GREEN}{a.get('nickname')} {Color.ORANGE}(@{a.get('unique_username')}){Color.RESET}")

        choice = input(f"\n{Color.CYAN}👉 Nhập STT hoặc ID TikTok để chọn: {Color.RESET}").strip()
        acc = next((a for i, a in enumerate(accs["data"], 1) if str(i) == choice or a.get('unique_username') == choice), None)
        
        if not acc:
            print(f"{Color.RED}❌ Không tìm thấy tài khoản!{Color.RESET}"); continue

        acc_id = str(acc["id"])
        print(f"{Color.GREEN}✅ Đã chọn: {acc.get('nickname')}{Color.RESET}")

        while True:
            print(f"{Color.BLUE}🔍 Đang tìm job FOLLOW...{Color.RESET}", end="\r")
            job = get_job(h, acc_id)
            if not job or "data" not in job or not job.get("data"):
                print(f"{Color.YELLOW}⏳ Chưa có job, chờ 10 giây {Color.RESET}", end="\r"); time.sleep(10); continue

            d = job["data"]
            job_type = d.get("type", "").lower()
            
            # Chỉ làm Follow, các job khác report bỏ qua
            if "follow" not in job_type:
                report_skip(h, d, acc_id)
                continue

            link = d.get("link")
            xu_job = d.get("price_after_cost", 0) 
            display_user = link.split('/')[-1]
            
            print(f"\n{Color.YELLOW}🎯 LOẠI JOB: {job_type.upper()}{Color.RESET}")
            print(f"{Color.GREEN}💰 GIÁ TRỊ JOB: {xu_job} xu{Color.RESET}")
            print(f"{Color.CYAN}🔗 COPY USERNAME DƯỚI ĐÂY:{Color.RESET}")
            print(f"{Color.PURPLE}{'='*30}{Color.RESET}")
            print(f"{Color.GREEN}{display_user}{Color.RESET}")
            print(f"{Color.PURPLE}{'='*30}{Color.RESET}")
            
            input(f"\n{Color.YELLOW}👉 Nhấn ENTER sau khi Follow để nhận {xu_job} xu...{Color.RESET}")
            
            res = complete(h, d["id"], acc_id)
            if res and res.get("status") == 200:
                print(f"{Color.GREEN}✅ Nhận thành công! +{xu_job} xu.{Color.RESET}")
            else:
                print(f"{Color.RED}❌ Nhận xu thất bại. Đang báo cáo job lỗi...{Color.RESET}")
                report_skip(h, d, acc_id)

if __name__ == "__main__":
    try: main()
    except KeyboardInterrupt: sys.exit()

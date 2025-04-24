import asyncio
import aiohttp
import time

# Settings
CONCURRENT_REQUESTS = 100  # Adjust if you're using proxies or hitting rate limits
REDEEM_URL = "https://www.roblox.com/redeem"

HEADERS = {
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
}


async def validate_code(session, code):
    try:
        data = {"code": code}
        async with session.post(REDEEM_URL, data=data, headers=HEADERS) as response:
            # Check if the response status is successful and the content indicates valid code
            if response.status == 200:
                text = await response.text()
                # Check for specific indication that the code was successfully redeemed (you can inspect the page response here)
                if "successfully redeemed" in text.lower():  # Look for success message text
                    print(f"[+] VALID CODE: {code}")
                    with open("valid.txt", "a") as vf:
                        vf.write(code + "\n")
                else:
                    print(f"[-] Invalid: {code} (no success message)")
            else:
                print(f"[-] Invalid: {code} (response status {response.status})")
    except Exception as e:
        print(f"[!] Error validating {code}: {e}")


async def run_validator(codes):
    connector = aiohttp.TCPConnector(limit=CONCURRENT_REQUESTS, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [validate_code(session, code.strip()) for code in codes]
        await asyncio.gather(*tasks)


def main():
    try:
        with open("codes.txt", "r") as f:
            codes = f.readlines()
    except FileNotFoundError:
        print("[!] 'codes.txt' not found. Please create it with one code per line.")
        return

    start = time.perf_counter()
    asyncio.run(run_validator(codes))
    end = time.perf_counter()
    print(f"\nDone. Checked {len(codes)} codes in {end - start:.2f} seconds.")


if __name__ == "__main__":
    main()

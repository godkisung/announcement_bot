import os
import telegram
import asyncio
from dotenv import load_dotenv
import bs4
import requests
import hashlib

# bot api 호출
token = os.environ.get("TELEGRAM_API_KEY")

# 메시지 내용을 해시로 변환
def message_to_hash(message):
    return hashlib.sha256(message.encode()).hexdigest()

# 메인 로직
async def main():
    url = "https://www.knou.ac.kr/knou/561/subview.do?epTicket=INV" # 주소 선언
    response = requests.get(url) # 주소 호출
    soup = bs4.BeautifulSoup(response.text, "html.parser")

    links = soup.select("td.td-subject > a ")
  
    seen_notice = "ID.txt"
    seen_hashes = set()

    try:
        with open(seen_notice, "r") as f:
            seen_hashes = set(f.read().splitlines())
    except FileNotFoundError:
        with open(seen_notice, "w") as f:  # 파일이 없으면 생성
            pass

    new_hashes = []
        
    for link_element in links:
        # tr 탐색
        parent_tr = link_element.find_parent("tr")
        
        # "notice" 제외
        if "notice" in parent_tr.get("class", []):
            continue
        
        span_element = link_element.select_one("span")
        if span_element:
            span_element.extract()

        # 링크와 제목 추출
        link = link_element["href"] if link_element.has_attr("href") else None
        title = link_element.text.strip().replace("\n", "").replace("  ", " ")
    
        # "전공"과 "신설" 붙이기
        combined = f"📌 {title} \n 🔗 링크: https://www.knou.ac.kr{link}"
        message_hash = message_to_hash(combined)

        if message_hash in seen_hashes:
            continue  # 중복 메시지 건너뛰기

        print(combined)
        new_hashes.append(message_hash)
        
        try:
            await bot.send_message(chat_id="-4595812781", text=combined)
        except telegram.error.TimedOut:
            print("Timeout occurred. Retrying...")
            # 재시도 로직 추가

    with open(seen_notice, "a") as f:
        for new_hash in new_hashes:
            f.write(new_hash + "\n")

if __name__ == "__main__":
    bot = telegram.Bot(token)
    asyncio.run(main())

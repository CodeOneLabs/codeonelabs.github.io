#!/usr/bin/env python3
"""Builds beatbound/privacy.html (English, default) and its translations.

Edit the text here, then run: python3 tools/build_beatbound_privacy.py
Every language must keep the same sections so the translations stay in sync.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_privacy import SITE, EMAIL, MAIL, CSS_VERSION, ROOT, table  # noqa: E402

DIR = "beatbound"

LINKS = {
    "epic": "https://legal.epicgames.com/epicgames/privacy-policy",
    "unity": "https://unity.com/legal/privacy-policy",
    "levelplay": "https://unity.com/legal/game-player-and-app-user-privacy-policy",
    "apple": "https://www.apple.com/legal/privacy/",
    "google": "https://policies.google.com/privacy",
    "oracle": "https://www.oracle.com/legal/privacy/",
    "cloudflare": "https://www.cloudflare.com/privacypolicy/",
    "github": "https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement",
}

# (code, file, native name)
LANGS = [
    ("en", "privacy.html", "English"),
    ("ko", "privacy-ko.html", "한국어"),
]


def links(names):
    return "<ul>" + "".join(f'<li><a href="{LINKS[k]}">{label}</a></li>' for k, label in names) + "</ul>"


TEXT = {}

# ---------------------------------------------------------------- English
TEXT["en"] = dict(
    title="Privacy Policy",
    game="BeatBound",
    desc="Privacy Policy for BeatBound by MeMe Games.",
    nav_label="Main menu", nav_home="Home", nav_privacy="Privacy", contact="Contact",
    lang_label="Language",
    body=f"""
<p>MeMe Games ("we", "us") makes BeatBound, a rhythm game for PC, Mac, iPhone, iPad and Android. This policy explains what information we process when you play the game and when you visit this website, why we process it, and the choices you have.</p>
<p class="small">Effective date: October 26, 2026 · Controller: MeMe Games · Contact: {MAIL}</p>

<h2>1. Information we process and why</h2>
{table(["Feature", "Information", "Purpose"], [
    ["Offline play", "Nickname, settings, play records, ranks, unlocked items. Stored only on your device.", "Save your progress and settings"],
    ["Online sign-in", "An anonymous device-based identifier and Product User ID created by Epic Online Services, your device model", "Identify players for ranked play, ghosts and versus matches, without an account or password"],
    ["Ranked play and score checks", "Song, difficulty, mode, score, hits, progress, the timing of your inputs, your position on the board during the song, ladder points, rating, win and loss records", "Verify scores against cheating, rank players, match you with opponents and other players' recorded runs (ghosts)"],
    ["Live versus matches", "Product User ID, a generated name (such as PLAYER-1A2B), ladder points, rating, equipped character and in-match play data, network information needed to connect (such as IP address)", "Connect you with an opponent and keep the match in sync"],
    ["Ads (mobile only)", "Advertising identifier (if you allow it), IP address, device and app information, ad views and clicks", "Show ads, measure them and prevent ad fraud"],
    ["Remove-ads purchase (mobile only)", "Purchase status and order information from the App Store or Google Play", "Turn off ads and restore your purchase on reinstall"],
    ["Server security", "IP address, request time, requested address, app version information in web requests", "Prevent abuse, limit request rates, troubleshoot"],
    ["Inquiries", "Your email address and anything you include in your message", "Answer your inquiry"],
])}
<p>Your nickname stays on your device. It is not sent to our server or shown to other players.</p>

<h2>2. Online sign-in</h2>
<p>Online features start only when you first open ranked or versus play. The game then signs in to Epic Online Services (EOS) with a device-based identifier. You do not create an account, and we never ask for an email address, password or real name. The game passes a sign-in token from EOS to our server (api.memegames.dev), which checks it with Epic and recognizes you by your Product User ID.</p>

<h2>3. Advertising (mobile only)</h2>
<p>The iPhone, iPad and Android versions show a full-screen ad after every few songs. Ads are served through Unity LevelPlay, a service of Unity Technologies, with the Unity Ads network. These services may collect the information listed in section 1 under their own privacy policies, and may use it for personalized ads where the law and your choices allow.</p>
<ul>
<li>On iPhone and iPad, the advertising identifier is used only if you allow tracking when the system asks. You can change this at any time in Settings, then Privacy &amp; Security, then Tracking.</li>
<li>On Android, you can reset or delete your advertising ID, or opt out of personalized ads, in your device settings.</li>
<li>Buying "Remove Ads" turns off ads in the game. Apple or Google handles the payment, and we never receive your payment card details.</li>
</ul>
<p>The PC and Mac versions have no ads.</p>

<h2>4. Storage and retention</h2>
<p>Settings, your nickname and offline records are stored on your device until you delete the game or its data.</p>
<p>On our server we keep:</p>
<ul>
<li>Your position-by-time recording of a song for one day, unless it becomes a ghost or belongs to a match still in progress.</li>
<li>Input timing of runs that fail the score check for seven days.</li>
<li>Scores, verified input timing, ghosts, ladder and rating records for as long as the online service runs, or until you ask us to delete them. Ghosts are replaced as newer runs come in.</li>
<li>Backup copies of the server database for up to 30 days.</li>
<li>Web request logs only as long as needed for security and troubleshooting.</li>
</ul>
<p>We keep emails you send us only as long as needed to handle your request, unless the law requires us to keep them longer. When information is no longer needed, we delete electronic files so they cannot be restored.</p>

<h2>5. Service providers and other players</h2>
<p>We use the following providers. Each processes information under its own privacy policy.</p>
<ul>
<li><strong>Epic Games, Inc.</strong> (Epic Online Services): anonymous sign-in, versus lobbies and P2P connections</li>
<li><strong>Oracle Corporation</strong> (Oracle Cloud): hosting our game server</li>
<li><strong>Cloudflare, Inc.</strong> (R2 storage): backups of the server database</li>
<li><strong>Unity Technologies</strong>: the game engine, in-app purchase handling and, on mobile, LevelPlay and Unity Ads. The Unity engine may also send basic, anonymous device statistics (such as hardware and operating system) to Unity.</li>
<li><strong>Apple Inc. and Google LLC</strong>: app stores, in-app purchases and payments</li>
<li><strong>GitHub, Inc.</strong>: hosting this website</li>
</ul>
<p>Other players see your runs as ghosts with a random generated name and character, a short code derived from your Product User ID, and your ladder points. Leaderboards show only that short code. In a live versus match your opponent receives your Product User ID, generated name, ladder points, rating, equipped character and in-match play. Depending on how players are connected, technical information such as your IP address may be visible to the relay service or to your opponent.</p>
<p>We do not sell your personal information. Apart from the ad services described in section 3, we do not share it for advertising.</p>
{links([("epic", "Epic Games Privacy Policy"), ("unity", "Unity Privacy Policy"), ("levelplay", "Unity Game Player and App User Privacy Policy (LevelPlay, Unity Ads)"), ("apple", "Apple Privacy Policy"), ("google", "Google Privacy Policy"), ("oracle", "Oracle Privacy Policy"), ("cloudflare", "Cloudflare Privacy Policy"), ("github", "GitHub Privacy Statement")])}

<h2>6. Website</h2>
<p>This website is served by GitHub Pages. It has no ads, no analytics scripts and no tracking cookies. GitHub may process access information such as IP addresses to provide and secure its hosting service.</p>

<h2>7. Your rights and choices</h2>
<p>You can ask us to access, correct, delete or export your information, or to restrict or object to processing. Send requests to {MAIL}. To help us find your records, include the platform you play on, roughly when you played ranked or versus, and, if you can, your ladder rank or the songs you played. We may ask for more information to confirm the request comes from you.</p>
<p>We reply without undue delay and within the time required by applicable law (for example, one month under the GDPR, or 10 days under Korea's Personal Information Protection Act).</p>
<p>You can play without any online features: if you never open ranked or versus play, the game does not sign in to EOS or contact our server. Deleting the game and its data removes everything stored on your device. On mobile you can also limit ad tracking as described in section 3.</p>

<h2>8. International users</h2>
<h3>8.1 Transfers outside your country</h3>
<p>MeMe Games is based in the Republic of Korea. Our providers process information on servers in Korea, the United States and other countries. Information is sent to them over the network when you use the related feature.</p>
{table(["Recipient", "Country", "Information", "Purpose", "Retention"], [
    ["Epic Games, Inc.", "United States and other EOS regions", "Device-based identifier, Product User ID, device model, versus play data in transit, network information", "Sign-in, versus matches", "As set out in Epic's policy"],
    ["Oracle Corporation", "Oracle Cloud region of our server", "Product User ID, runs, ghosts, ladder and rating records, request logs", "Game server hosting", "As set out in section 4"],
    ["Cloudflare, Inc.", "United States and other regions", "Database backups", "Backups", "Up to 30 days"],
    ["Unity Technologies", "United States and other regions", "Advertising identifier, IP address, device and ad information (mobile), purchase status, device statistics", "Ads, purchases, engine statistics", "As set out in Unity's policies"],
    ["Apple Inc. / Google LLC", "United States", "Purchase information", "In-app purchases", "As set out in Apple's and Google's policies"],
    ["GitHub, Inc.", "United States", "Website access information", "Website hosting", "As set out in GitHub's policy"],
], wide=True)}
<p>Where required, these transfers are protected by safeguards offered by the providers, such as the European Commission's Standard Contractual Clauses. You can refuse a transfer by not using the related feature or by contacting us, but online play, ads-supported play or purchases may then be unavailable.</p>

<h3>8.2 European Economic Area, United Kingdom and Switzerland</h3>
<p>Under the GDPR and UK GDPR, MeMe Games is the controller of your information. We rely on these legal bases:</p>
<ul>
<li><strong>Performance of a contract</strong>: online sign-in, ranked play, ghosts, versus matches, the remove-ads purchase</li>
<li><strong>Consent</strong>: personalized ads and the use of your advertising identifier. You can withdraw consent at any time in your device settings.</li>
<li><strong>Legitimate interests</strong>: score checks against cheating, security and abuse prevention, non-personalized ads that fund the free mobile version, website hosting. You can object at any time.</li>
<li><strong>Legal obligation</strong>: when the law requires us to keep or disclose information</li>
</ul>
<p>You also have the right to data portability and the right to lodge a complaint with your local data protection authority. Score checks are automated, but they only decide whether a run counts for ranking; they have no legal or similarly significant effect on you, and you can contact us if you think a run was rejected by mistake.</p>

<h3>8.3 California and other U.S. states</h3>
<p>We do not sell personal information. Ad services on mobile may receive identifiers that count as "sharing" for cross-context behavioral advertising; you can opt out through your device's ad tracking settings described in section 3. We do not use sensitive personal information to infer characteristics about you. In the past 12 months we collected these categories: identifiers (device-based IDs, advertising identifiers, IP addresses) and internet or other network activity (gameplay data, ad interactions, request logs). You can ask to know, correct or delete your information, directly or through an authorized agent. We will not discriminate against you for exercising these rights.</p>

<h3>8.4 Republic of Korea</h3>
<p>Privacy officer: MeMe Games, {MAIL}. For help with a privacy violation, you can also contact the Personal Information Infringement Report Center (privacy.kisa.or.kr, 118) or the Personal Information Dispute Mediation Committee (www.kopico.go.kr, 1833-6972).</p>

<h2>9. Children</h2>
<p>The game is not directed to children under 13, and we do not knowingly collect information from them. Where a higher age applies (for example under 14 in Korea, or under 16 in some EEA countries), children below that age should use online features only with the consent of a parent or guardian. If you believe a child has given us information without that consent, contact us and we will delete it.</p>

<h2>10. Security</h2>
<p>We collect only what the game needs. Traffic to our server is encrypted (HTTPS), server sessions expire after 12 hours, and access to the server and its backups is restricted. No method of transmission is completely secure, but we work to protect your information.</p>

<h2>11. Changes to this policy</h2>
<p>We update this policy when the game or the law changes and show the new effective date at the top. For significant changes, we will also give notice in the game or on this website.</p>

<h2>12. Languages and contact</h2>
<p>This policy is written in English and translated into other languages. If a translation differs from the English version, the English version prevails unless local law requires otherwise.</p>
<p>MeMe Games · {MAIL}</p>
""",
)

# ---------------------------------------------------------------- Korean
TEXT["ko"] = dict(
    title="개인정보처리방침",
    game="BeatBound",
    desc="미미게임즈(MeMe Games) BeatBound 개인정보처리방침.",
    nav_label="주요 메뉴", nav_home="홈", nav_privacy="개인정보", contact="문의",
    lang_label="언어",
    body=f"""
<p>미미게임즈(MeMe Games, 이하 "회사")는 PC, Mac, iPhone, iPad, Android용 리듬 게임 BeatBound를 만듭니다. 이 방침은 게임을 플레이하거나 이 웹사이트를 방문할 때 회사가 어떤 정보를 왜 처리하는지, 그리고 이용자가 무엇을 선택할 수 있는지 설명합니다.</p>
<p class="small">시행일: 2026년 10월 26일 · 개인정보처리자: 미미게임즈 · 문의: {MAIL}</p>

<h2>1. 처리하는 정보와 목적</h2>
{table(["기능", "정보", "목적"], [
    ["오프라인 플레이", "닉네임, 설정, 플레이 기록, 랭크, 해금 아이템. 기기에만 저장합니다.", "진행 상황과 설정 저장"],
    ["온라인 로그인", "Epic Online Services가 만드는 익명 기기 기반 식별자와 Product User ID, 기기 모델명", "계정이나 비밀번호 없이 랭크전·고스트·대전에서 플레이어 식별"],
    ["랭크전과 점수 검증", "곡, 난이도, 모드, 점수, 피격 수, 진행률, 입력 타이밍, 곡 진행 중 보드 위 위치, 래더 포인트, 레이팅, 승패 기록", "부정행위 방지를 위한 점수 검증, 순위 산정, 상대 및 다른 플레이어의 녹화 기록(고스트) 매칭"],
    ["실시간 대전", "Product User ID, 자동 생성 이름(예: PLAYER-1A2B), 래더 포인트, 레이팅, 장착 캐릭터, 대전 중 플레이 데이터, 연결에 필요한 네트워크 정보(IP 주소 등)", "상대와 연결하고 대전 동기화"],
    ["광고(모바일만)", "광고 식별자(허용한 경우), IP 주소, 기기·앱 정보, 광고 노출·클릭", "광고 표시, 광고 성과 측정, 광고 사기 방지"],
    ["광고 제거 구매(모바일만)", "App Store·Google Play의 구매 상태와 주문 정보", "광고 끄기, 재설치 시 구매 복원"],
    ["서버 보안", "웹 요청의 IP 주소, 요청 시각, 요청 주소, 앱 버전 정보", "남용 방지, 요청 수 제한, 장애 대응"],
    ["문의", "이메일 주소와 메시지에 적은 내용", "문의 답변"],
])}
<p>닉네임은 기기에만 남습니다. 회사 서버로 보내거나 다른 플레이어에게 보여 주지 않습니다.</p>

<h2>2. 온라인 로그인</h2>
<p>온라인 기능은 랭크전이나 대전을 처음 열 때 시작됩니다. 이때 게임이 기기 기반 식별자로 Epic Online Services(EOS)에 로그인합니다. 계정을 만들지 않으며, 이메일 주소·비밀번호·실명을 묻지 않습니다. 게임은 EOS가 발급한 로그인 토큰을 회사 서버(api.memegames.dev)에 전달하고, 서버는 Epic을 통해 토큰을 확인한 뒤 Product User ID로 이용자를 구분합니다.</p>

<h2>3. 광고(모바일만)</h2>
<p>iPhone, iPad, Android 버전은 몇 곡마다 전면 광고를 보여 줍니다. 광고는 Unity Technologies의 Unity LevelPlay와 Unity Ads 네트워크로 제공됩니다. 이 서비스들은 1항의 광고 정보를 각자의 개인정보처리방침에 따라 수집할 수 있고, 법과 이용자의 선택이 허용하는 범위에서 맞춤형 광고에 쓸 수 있습니다.</p>
<ul>
<li>iPhone·iPad에서는 시스템이 물을 때 추적을 허용한 경우에만 광고 식별자를 씁니다. 설정 &gt; 개인정보 보호 및 보안 &gt; 추적에서 언제든 바꿀 수 있습니다.</li>
<li>Android에서는 기기 설정에서 광고 ID를 재설정·삭제하거나 맞춤 광고를 끌 수 있습니다.</li>
<li>"광고 제거"를 구매하면 게임 안 광고가 꺼집니다. 결제는 Apple 또는 Google이 처리하며, 회사는 카드 정보를 받지 않습니다.</li>
</ul>
<p>PC와 Mac 버전에는 광고가 없습니다.</p>

<h2>4. 보관과 파기</h2>
<p>설정, 닉네임, 오프라인 기록은 게임이나 게임 데이터를 지울 때까지 기기에 남습니다.</p>
<p>회사 서버에는 다음과 같이 보관합니다.</p>
<ul>
<li>곡 진행 중 위치 기록: 1일. 단, 고스트로 쓰이거나 진행 중인 매치에 속한 경우는 예외입니다.</li>
<li>점수 검증에 실패한 판의 입력 타이밍: 7일</li>
<li>점수, 검증된 입력 타이밍, 고스트, 래더·레이팅 기록: 온라인 서비스를 운영하는 동안 또는 삭제를 요청할 때까지. 고스트는 새 기록이 들어오면 교체됩니다.</li>
<li>서버 데이터베이스 백업: 최대 30일</li>
<li>웹 요청 로그: 보안과 장애 대응에 필요한 기간만</li>
</ul>
<p>보내 주신 이메일은 요청 처리에 필요한 기간만 보관하며, 법령이 더 긴 보관을 요구하는 경우는 예외입니다. 필요가 없어진 정보는 복구할 수 없는 방법으로 삭제합니다.</p>

<h2>5. 처리 위탁과 다른 플레이어</h2>
<p>회사는 다음 업체를 이용하며, 각 업체는 자체 개인정보처리방침에 따라 정보를 처리합니다.</p>
<ul>
<li><strong>Epic Games, Inc.</strong>(Epic Online Services): 익명 로그인, 대전 로비, P2P 연결</li>
<li><strong>Oracle Corporation</strong>(Oracle Cloud): 게임 서버 호스팅</li>
<li><strong>Cloudflare, Inc.</strong>(R2 스토리지): 서버 데이터베이스 백업</li>
<li><strong>Unity Technologies</strong>: 게임 엔진, 인앱 결제 처리, 모바일 LevelPlay·Unity Ads. Unity 엔진은 하드웨어·운영체제 같은 기본적인 익명 기기 통계를 Unity에 보낼 수 있습니다.</li>
<li><strong>Apple Inc., Google LLC</strong>: 앱 스토어, 인앱 결제</li>
<li><strong>GitHub, Inc.</strong>: 이 웹사이트 호스팅</li>
</ul>
<p>다른 플레이어에게는 내 기록이 고스트로 보이며, 무작위로 만든 이름·캐릭터, Product User ID에서 만든 짧은 코드, 래더 포인트가 함께 표시됩니다. 순위표에는 그 짧은 코드만 표시됩니다. 실시간 대전에서는 상대가 내 Product User ID, 자동 생성 이름, 래더 포인트, 레이팅, 장착 캐릭터, 대전 중 플레이를 받습니다. 연결 방식에 따라 IP 주소 같은 기술 정보가 중계 서비스나 상대에게 보일 수 있습니다.</p>
<p>회사는 개인정보를 판매하지 않으며, 3항의 광고 서비스를 빼면 광고 목적으로 제공하지 않습니다.</p>
{links([("epic", "Epic Games 개인정보처리방침"), ("unity", "Unity 개인정보처리방침"), ("levelplay", "Unity 게임 플레이어·앱 이용자 개인정보처리방침(LevelPlay, Unity Ads)"), ("apple", "Apple 개인정보처리방침"), ("google", "Google 개인정보처리방침"), ("oracle", "Oracle 개인정보처리방침"), ("cloudflare", "Cloudflare 개인정보처리방침"), ("github", "GitHub 개인정보 처리방침")])}

<h2>6. 웹사이트</h2>
<p>이 웹사이트는 GitHub Pages로 제공됩니다. 광고, 분석 스크립트, 추적 쿠키가 없습니다. GitHub는 호스팅 제공과 보안을 위해 IP 주소 같은 접속 정보를 처리할 수 있습니다.</p>

<h2>7. 이용자의 권리와 선택</h2>
<p>정보의 열람, 정정, 삭제, 내보내기, 처리 정지·반대를 요청할 수 있습니다. {MAIL}로 보내 주세요. 기록을 찾을 수 있도록 플레이하는 플랫폼, 랭크전·대전을 한 대략적인 시기, 가능하면 래더 랭크나 플레이한 곡을 함께 적어 주세요. 본인 확인을 위해 추가 정보를 요청할 수 있습니다.</p>
<p>지체 없이, 관련 법령이 정한 기간 안에 답변합니다(예: GDPR 1개월, 개인정보 보호법 10일).</p>
<p>온라인 기능 없이도 플레이할 수 있습니다. 랭크전이나 대전을 열지 않으면 게임은 EOS에 로그인하지 않고 회사 서버에도 접속하지 않습니다. 게임과 데이터를 지우면 기기에 저장된 정보가 모두 삭제됩니다. 모바일에서는 3항처럼 광고 추적을 제한할 수 있습니다.</p>

<h2>8. 해외 이용자</h2>
<h3>8.1 국외 이전</h3>
<p>회사는 대한민국에 있습니다. 위탁 업체는 대한민국, 미국 및 기타 국가의 서버에서 정보를 처리하며, 이용자가 해당 기능을 쓸 때 네트워크로 정보가 전송됩니다.</p>
{table(["이전받는 자", "국가", "항목", "목적", "보유 기간"], [
    ["Epic Games, Inc.", "미국 및 기타 EOS 리전", "기기 기반 식별자, Product User ID, 기기 모델명, 전송 중인 대전 플레이 데이터, 네트워크 정보", "로그인, 대전", "Epic 방침에 따름"],
    ["Oracle Corporation", "회사 서버가 있는 Oracle Cloud 리전", "Product User ID, 판 기록, 고스트, 래더·레이팅 기록, 요청 로그", "게임 서버 호스팅", "4항에 따름"],
    ["Cloudflare, Inc.", "미국 및 기타 리전", "데이터베이스 백업", "백업", "최대 30일"],
    ["Unity Technologies", "미국 및 기타 리전", "광고 식별자, IP 주소, 기기·광고 정보(모바일), 구매 상태, 기기 통계", "광고, 결제, 엔진 통계", "Unity 방침에 따름"],
    ["Apple Inc. / Google LLC", "미국", "구매 정보", "인앱 결제", "Apple·Google 방침에 따름"],
    ["GitHub, Inc.", "미국", "웹사이트 접속 정보", "웹사이트 호스팅", "GitHub 방침에 따름"],
], wide=True)}
<p>필요한 경우 유럽연합 집행위원회 표준계약조항 등 업체가 제공하는 보호 조치가 적용됩니다. 해당 기능을 쓰지 않거나 회사에 연락해 이전을 거부할 수 있으나, 이 경우 온라인 플레이, 광고 지원 플레이 또는 구매를 이용하지 못할 수 있습니다.</p>

<h3>8.2 유럽경제지역, 영국, 스위스</h3>
<p>GDPR과 UK GDPR에 따라 미미게임즈가 개인정보의 컨트롤러입니다. 처리 근거는 다음과 같습니다.</p>
<ul>
<li><strong>계약 이행</strong>: 온라인 로그인, 랭크전, 고스트, 대전, 광고 제거 구매</li>
<li><strong>동의</strong>: 맞춤형 광고와 광고 식별자 사용. 기기 설정에서 언제든 철회할 수 있습니다.</li>
<li><strong>정당한 이익</strong>: 부정행위 방지를 위한 점수 검증, 보안과 남용 방지, 무료 모바일 버전을 위한 비맞춤형 광고, 웹사이트 호스팅. 언제든 반대할 수 있습니다.</li>
<li><strong>법적 의무</strong>: 법령이 보관·제공을 요구하는 경우</li>
</ul>
<p>데이터 이동권과 관할 감독기관에 민원을 제기할 권리도 있습니다. 점수 검증은 자동으로 이루어지지만 판이 순위에 반영되는지만 정하며, 이용자에게 법적 효과나 그에 준하는 중대한 영향을 주지 않습니다. 판이 잘못 거부되었다고 생각되면 회사에 연락해 주세요.</p>

<h3>8.3 미국 캘리포니아 및 기타 주</h3>
<p>회사는 개인정보를 판매하지 않습니다. 모바일 광고 서비스가 받는 식별자는 교차 맥락 행동 광고를 위한 "공유"에 해당할 수 있으며, 3항의 기기 광고 추적 설정으로 거부할 수 있습니다. 민감한 개인정보로 이용자의 특성을 추론하지 않습니다. 지난 12개월 동안 수집한 범주는 식별자(기기 기반 ID, 광고 식별자, IP 주소)와 인터넷·네트워크 활동(플레이 데이터, 광고 반응, 요청 로그)입니다. 직접 또는 대리인을 통해 정보의 열람, 정정, 삭제를 요청할 수 있으며, 권리 행사를 이유로 차별하지 않습니다.</p>

<h3>8.4 대한민국</h3>
<p>개인정보 보호책임자: 미미게임즈, {MAIL}. 개인정보 침해에 대한 도움은 개인정보침해신고센터(privacy.kisa.or.kr, 118) 또는 개인정보분쟁조정위원회(www.kopico.go.kr, 1833-6972)에도 요청할 수 있습니다.</p>

<h2>9. 아동</h2>
<p>이 게임은 만 13세 미만 아동을 대상으로 하지 않으며, 회사는 아동의 정보를 알면서 수집하지 않습니다. 더 높은 연령 기준이 적용되는 곳(예: 대한민국 만 14세 미만, 일부 EEA 국가 만 16세 미만)에서는 해당 연령 미만 아동이 법정대리인의 동의를 받아 온라인 기능을 써야 합니다. 동의 없이 아동의 정보가 제공되었다고 생각되면 연락해 주세요. 삭제하겠습니다.</p>

<h2>10. 안전성 확보 조치</h2>
<p>게임에 필요한 정보만 수집합니다. 서버 통신은 암호화(HTTPS)하고, 서버 세션은 12시간 뒤 만료되며, 서버와 백업에는 접근 권한을 제한합니다. 완벽하게 안전한 전송 방법은 없지만 정보를 보호하기 위해 노력합니다.</p>

<h2>11. 방침 변경</h2>
<p>게임이나 법령이 바뀌면 이 방침을 고치고 위쪽에 새 시행일을 표시합니다. 중요한 변경은 게임 안이나 이 웹사이트에서도 알립니다.</p>

<h2>12. 언어와 문의</h2>
<p>이 방침은 영어로 작성되어 다른 언어로 번역됩니다. 번역본이 영어 원문과 다르면, 현지 법령이 달리 정하지 않는 한 영어 원문이 우선합니다.</p>
<p>미미게임즈 · {MAIL}</p>
""",
)


def lang_switcher(current, label):
    items = []
    for code, file, name in LANGS:
        cur = ' aria-current="page"' if code == current else ""
        items.append(f'<a href="{file}" hreflang="{code}" lang="{code}"{cur}>{name}</a>')
    return f'<p class="langs" role="navigation" aria-label="{label}">' + " <span aria-hidden=\"true\">·</span> ".join(items) + "</p>"


def page(code, file):
    t = TEXT[code]
    alternates = "".join(f'<link rel="alternate" hreflang="{c}" href="{SITE}/{DIR}/{f}">' for c, f, _ in LANGS)
    alternates += f'<link rel="alternate" hreflang="x-default" href="{SITE}/{DIR}/privacy.html">'
    body = " ".join(line.strip() for line in t["body"].strip().splitlines() if line.strip())
    return (
        f'<!doctype html><html lang="{code}"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<meta name="description" content="{t["desc"]}"><title>{t["title"]} · BeatBound · MeMe Games</title>'
        f'<link rel="canonical" href="{SITE}/{DIR}/{file}">{alternates}'
        f'<link rel="icon" type="image/png" href="../assets/beatbound-icon-128.png"><link rel="stylesheet" href="../style.css?v={CSS_VERSION}"></head><body>'
        f'<nav aria-label="{t["nav_label"]}"><a class="brand" href="../index.html">MeMe Games / BeatBound</a>'
        f'<div><a href="../index.html">{t["nav_home"]}</a><a href="{file}">{t["nav_privacy"]}</a></div></nav>'
        f'<main class="policy"><span class="eyebrow">PRIVACY</span><h1>{t["title"]}</h1>'
        f'{lang_switcher(code, t["lang_label"])}{body}</main>'
        f'<footer><span>© 2026 MeMe Games · {t["game"]}</span>'
        f'<span><a href="{file}">{t["title"]}</a> · <a href="mailto:{EMAIL}">{t["contact"]}</a></span></footer>'
        f"</body></html>\n"
    )


if __name__ == "__main__":
    (ROOT / DIR).mkdir(exist_ok=True)
    for code, file, _ in LANGS:
        (ROOT / DIR / file).write_text(page(code, file), encoding="utf-8")
        print("wrote", f"{DIR}/{file}")

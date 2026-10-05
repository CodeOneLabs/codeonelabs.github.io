#!/usr/bin/env python3
"""Builds privacy.html (English, default) and its translations.

Edit the text here, then run: python3 tools/build_privacy.py
Every language must keep the same sections so the translations stay in sync.
"""
from pathlib import Path

SITE = "https://codeonelabs.github.io"
EMAIL = "codeone.unity@gmail.com"
MAIL = f'<a href="mailto:{EMAIL}">{EMAIL}</a>'
# Bump when style.css changes so browsers drop the cached copy.
CSS_VERSION = "20261005c"
ROOT = Path(__file__).resolve().parent.parent

LINKS = {
    "epic": "https://legal.epicgames.com/epicgames/privacy-policy",
    "discord": "https://discord.com/privacy",
    "unity": "https://unity.com/legal/privacy-policy",
    "steam": "https://store.steampowered.com/privacy_agreement/",
    "github": "https://docs.github.com/en/site-policy/privacy-policies/github-general-privacy-statement",
}

# (code, file, native name)
LANGS = [
    ("en", "privacy.html", "English"),
    ("ko", "privacy-ko.html", "한국어"),
    ("ja", "privacy-ja.html", "日本語"),
    ("zh-Hans", "privacy-zh.html", "简体中文"),
    ("fr", "privacy-fr.html", "Français"),
]


def table(head, rows, wide=False):
    th = "".join(f"<th>{h}</th>" for h in head)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    cls = ' class="wide"' if wide else ""
    return f'<div class="table-wrap"><table{cls}><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'


def links(names):
    return "<ul>" + "".join(f'<li><a href="{LINKS[k]}">{label}</a></li>' for k, label in names) + "</ul>"


TEXT = {}

# ---------------------------------------------------------------- English
TEXT["en"] = dict(
    title="Privacy Policy",
    game="Everyone's Dilemma",
    desc="Privacy Policy for Everyone's Dilemma (TrolleyDilemma) by MeMe Games.",
    nav_label="Main menu", nav_game="Game", nav_privacy="Privacy", contact="Contact",
    lang_label="Language",
    body=f"""
<p>MeMe Games ("we", "us") makes Everyone's Dilemma (TrolleyDilemma). This policy explains what information we process when you play the game on any platform and when you visit this website, why we process it, and the choices you have.</p>
<p class="small">Effective date: October 5, 2026 · Controller: MeMe Games · Contact: {MAIL}</p>

<h2>1. Information we process and why</h2>
{table(["Feature", "Information", "Purpose"], [
    ["Basic sign-in", "EOS device-based identifier, Product User ID, sign-in status", "Identify players and provide online services"],
    ["Optional account linking", "Epic or Discord account identifier, basic profile within the requested scope (such as display name), authentication tokens", "Link the external account you choose to your game data"],
    ["Online play", "Nickname, lobby, session and gameplay data, network information needed to connect (such as IP address)", "Connect players and keep the game in sync"],
    ["Voice chat", "Voice you send through your microphone", "Let players in the same voice channel talk to each other"],
    ["Saving and sync", "Nickname, match time, mode, player count, online or offline, score, day reached, win or loss, team, MVP, winner, cumulative records, achievements and equipped cosmetics", "Save your play records and sync them to EOS cloud storage"],
    ["Steam features", "Steam account identifier, unlocked achievements, the room code in invitations you send", "Steam achievements and friend invitations (Steam version only)"],
    ["Crash and error reports", "Error message and stack trace, recent log lines, game version, platform, operating system, device model and hardware details, time of the error, an anonymous device identifier assigned by Unity", "Find and fix crashes and errors"],
    ["Inquiries", "Your email address and anything you include in your message", "Answer your inquiry"],
])}

<h2>2. Account linking and sign-in</h2>
<p>Linking an Epic or Discord account is optional. The game opens the provider's own sign-in page and never asks for or receives your password. We request only Epic's Basic Profile scope and Discord's identify scope; we do not request your friends list or email address. The Discord access token is used only to complete sign-in and is not kept in the game's save files.</p>

<h2>3. Crash and error reports</h2>
<p>The game uses Unity Cloud Diagnostics, a service of Unity Technologies, to send a report when the game crashes or runs into an unexpected error. A report contains the error message and stack trace, the last few lines of the game log, the game version, platform, operating system, device model and hardware details (such as CPU, GPU and memory), the time of the error and an anonymous device identifier assigned by Unity. Reports do not contain your password, email address, voice or chat content. Log lines may include technical details such as your in-game nickname or a room code.</p>
<p>We use reports only to find and fix problems. We do not use them for advertising or to build profiles. Reports are kept only as long as needed to resolve the problem, within the retention period of Unity's service.</p>
<p>Depending on the platform, Apple, Google or Valve may also share crash information with us, for example when you have chosen on your device to share analytics with app developers. Those reports follow the platform's settings and privacy policy.</p>

<h2>4. Storage and retention</h2>
<p>Settings and play records are stored on your device. The game keeps up to 50 recent matches, plus summary records such as total matches, wins and best score. When an EOS account is available, records may sync automatically to Epic Online Services cloud storage. Cloud records are not deleted after a fixed period; they stay until they are overwritten or until you ask us to delete them. Deleting the game or its local files does not delete cloud data.</p>
<p>Voice chat is sent in real time. The game does not record or store it. Processing needed to carry voice and network traffic follows the service provider's policy.</p>
<p>We keep emails you send us only as long as needed to handle your request, unless the law requires us to keep them longer. When information is no longer needed, we delete electronic files so they cannot be restored.</p>

<h2>5. Service providers and other players</h2>
<p>We use the following providers. Each processes information under its own privacy policy.</p>
<ul>
<li><strong>Epic Games, Inc.</strong> (Epic Online Services): sign-in, account linking, lobbies and P2P connections, voice chat, cloud storage of play records</li>
<li><strong>Discord Inc.</strong>: sign-in for the Discord account you choose to link</li>
<li><strong>Unity Technologies</strong> (Unity Cloud Diagnostics): crash and error reports</li>
<li><strong>Valve Corporation</strong> (Steam): achievements and friend invitations in the Steam version</li>
<li><strong>GitHub, Inc.</strong>: hosting this website</li>
</ul>
<p>Apple, Google and Valve handle store purchases, platform accounts and payments under their own policies. We never receive your payment card details.</p>
<p>During online play, your nickname, gameplay data and the voice you send are shared with the other players in the same session. Depending on how players are connected, technical information such as your IP address may be visible to the relay service or to other players.</p>
<p>We do not sell your personal information, and we do not share it for targeted advertising.</p>
{links([("epic", "Epic Games Privacy Policy"), ("discord", "Discord Privacy Policy"), ("unity", "Unity Privacy Policy"), ("steam", "Steam Privacy Policy"), ("github", "GitHub Privacy Statement")])}

<h2>6. Website, advertising and analytics</h2>
<p>This website is served by GitHub Pages. It has no ads, no analytics scripts and no tracking cookies. GitHub may process access information such as IP addresses to provide and secure its hosting service. The game has no advertising or behavioral analytics SDKs. The only diagnostic data it sends are the crash and error reports described in section 3.</p>

<h2>7. Your rights and choices</h2>
<p>You can ask us to access, correct, delete or export your information, to unlink an external account from your game data, or to restrict or object to processing. Send requests to {MAIL}. To help us find your records, include your in-game nickname, the platform you play on and the type of any linked account. We may ask for more information to confirm the request comes from you. Never send passwords, verification codes or access tokens.</p>
<p>We reply without undue delay and within the time required by applicable law (for example, one month under the GDPR, or 10 days under Korea's Personal Information Protection Act).</p>
<p>You can also revoke the game's access in your Epic Games or Discord account settings. Revoking access there and deleting the game's saved data are separate steps. For voice chat, you can use push-to-talk in Options or deny microphone access in your device settings.</p>

<h2>8. International users</h2>
<h3>8.1 Transfers outside your country</h3>
<p>MeMe Games is based in the Republic of Korea. Our providers process information on servers in the United States and other countries. Information is sent to them over the network when you use the related feature.</p>
{table(["Recipient", "Country", "Information", "Purpose", "Retention"], [
    ["Epic Games, Inc.", "United States and other EOS regions", "Identifiers, nickname, gameplay and play records, voice in transit, network information", "Online services, voice chat, cloud saves", "Until you ask us to delete it, or as set out in Epic's policy"],
    ["Discord Inc.", "United States", "Discord account identifier, basic profile", "Account linking", "As set out in Discord's policy"],
    ["Unity Technologies SF", "United States", "Crash and error reports", "Crash diagnosis", "Within Unity's retention period"],
    ["Valve Corporation", "United States", "Steam account identifier, achievements, invitation room code", "Steam features", "As set out in Valve's policy"],
    ["GitHub, Inc.", "United States", "Website access information", "Website hosting", "As set out in GitHub's policy"],
], wide=True)}
<p>Where required, these transfers are protected by safeguards offered by the providers, such as the European Commission's Standard Contractual Clauses. You can refuse a transfer by not using the related feature or by contacting us, but online play, account linking, cloud saves or crash diagnosis may then be unavailable.</p>

<h3>8.2 European Economic Area, United Kingdom and Switzerland</h3>
<p>Under the GDPR and UK GDPR, MeMe Games is the controller of your information. We rely on these legal bases:</p>
<ul>
<li><strong>Performance of a contract</strong>: sign-in, online play, voice chat, saving and syncing records</li>
<li><strong>Consent</strong>: linking an Epic or Discord account. You can withdraw consent at any time by unlinking or by contacting us.</li>
<li><strong>Legitimate interests</strong>: crash and error reports, security and abuse prevention, website hosting, to keep the game stable and safe. You can object at any time.</li>
<li><strong>Legal obligation</strong>: when the law requires us to keep or disclose information</li>
</ul>
<p>You also have the right to data portability and the right to lodge a complaint with your local data protection authority. We do not make decisions based solely on automated processing that have legal or similarly significant effects on you.</p>

<h3>8.3 California and other U.S. states</h3>
<p>We do not sell or share personal information as those terms are defined in the CCPA/CPRA, and we do not use sensitive personal information to infer characteristics about you. In the past 12 months we collected these categories: identifiers (account IDs, device identifiers, IP addresses), internet or other network activity (gameplay and connection data, crash reports) and audio information (voice sent in voice chat, which is not recorded). You can ask to know, correct or delete your information, directly or through an authorized agent. We will not discriminate against you for exercising these rights.</p>

<h3>8.4 Republic of Korea</h3>
<p>Privacy officer: MeMe Games, {MAIL}. For help with a privacy violation, you can also contact the Personal Information Infringement Report Center (privacy.kisa.or.kr, 118) or the Personal Information Dispute Mediation Committee (www.kopico.go.kr, 1833-6972).</p>

<h2>9. Children</h2>
<p>The game is not directed to children under 13. Where a higher age applies (for example under 14 in Korea, or under 16 in some EEA countries), children below that age should use online features, account linking and voice chat only with the consent of a parent or guardian. If you believe a child has given us information without that consent, contact us and we will delete it.</p>

<h2>10. Security</h2>
<p>We collect only what the game needs, rely on our providers' encrypted connections for sign-in and online play, and do not store passwords or Discord access tokens. No method of transmission is completely secure, but we work to protect your information.</p>

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
    game="모두의 딜레마",
    desc="MeMe Games의 모두의 딜레마(TrolleyDilemma) 개인정보처리방침.",
    nav_label="주요 메뉴", nav_game="게임 소개", nav_privacy="개인정보", contact="문의",
    lang_label="언어",
    body=f"""
<p>MeMe Games(이하 "회사")는 모두의 딜레마(TrolleyDilemma)를 만듭니다. 이 방침은 모든 플랫폼에서 게임을 플레이하거나 이 웹사이트를 방문할 때 회사가 어떤 정보를 왜 처리하는지, 이용자가 어떤 선택을 할 수 있는지 설명합니다.</p>
<p class="small">시행일: 2026년 10월 5일 · 개인정보처리자: MeMe Games · 문의: {MAIL}</p>

<h2>1. 처리하는 정보와 목적</h2>
{table(["기능", "정보", "목적"], [
    ["기본 로그인", "EOS 기기 기반 식별자, Product User ID, 로그인 상태", "플레이어 식별 및 온라인 서비스 제공"],
    ["선택적 계정 연결", "Epic 또는 Discord 계정 식별자, 요청 권한 범위의 기본 프로필(표시 이름 등), 인증 토큰", "이용자가 고른 외부 계정을 게임 데이터와 연결"],
    ["온라인 플레이", "닉네임, 로비·세션 및 게임 진행 정보, 연결에 필요한 네트워크 정보(IP 주소 등)", "플레이어 연결과 게임 상태 동기화"],
    ["음성 채팅", "마이크로 전송하는 음성", "같은 음성 채널 플레이어 간 대화"],
    ["저장 및 동기화", "닉네임, 경기 시각·모드·플레이어 수·온라인 여부·점수·진행 일차·승패·진영·MVP·승자, 누적 기록, 업적과 착용한 꾸미기 아이템", "플레이 기록 저장 및 EOS 클라우드 동기화"],
    ["Steam 기능", "Steam 계정 식별자, 달성한 업적, 보낸 초대에 담긴 방 코드", "Steam 업적과 친구 초대(Steam 버전만 해당)"],
    ["크래시·오류 보고", "오류 메시지와 스택 트레이스, 최근 로그 몇 줄, 게임 버전, 플랫폼, 운영체제, 기기 모델과 하드웨어 정보, 오류 발생 시각, Unity가 부여하는 익명 기기 식별자", "충돌과 오류의 원인 파악 및 수정"],
    ["문의", "이메일 주소와 문의에 적은 내용", "문의 확인과 답변"],
])}

<h2>2. 계정 연결과 인증</h2>
<p>Epic·Discord 계정 연결은 이용자가 선택합니다. 게임은 각 서비스의 로그인 화면을 열 뿐 비밀번호를 묻거나 받지 않습니다. Epic은 Basic Profile, Discord는 identify 권한만 요청하며, 친구 목록과 이메일 주소는 요청하지 않습니다. Discord 접근 토큰은 로그인을 마치는 데만 쓰고 게임 저장 파일에 보관하지 않습니다.</p>

<h2>3. 크래시·오류 보고</h2>
<p>게임이 충돌하거나 예상하지 못한 오류가 나면 Unity Technologies의 Unity Cloud Diagnostics로 보고서를 보냅니다. 보고서에는 오류 메시지와 스택 트레이스, 게임 로그의 마지막 몇 줄, 게임 버전, 플랫폼, 운영체제, 기기 모델과 하드웨어 정보(CPU·GPU·메모리 등), 오류 발생 시각, Unity가 부여하는 익명 기기 식별자가 담깁니다. 비밀번호, 이메일 주소, 음성, 채팅 내용은 포함하지 않습니다. 다만 로그에 게임 닉네임이나 방 코드 같은 기술 정보가 섞일 수 있습니다.</p>
<p>보고서는 문제를 찾고 고치는 데만 쓰며 광고나 이용자 프로필 작성에 쓰지 않습니다. 문제 해결에 필요한 기간 동안, Unity 서비스의 보관 기간 안에서만 보관합니다.</p>
<p>플랫폼에 따라 Apple, Google, Valve가 크래시 정보를 회사에 제공할 수 있습니다. 예를 들어 기기에서 앱 개발자와 분석 정보 공유를 허용한 경우입니다. 이 보고는 각 플랫폼의 설정과 개인정보처리방침을 따릅니다.</p>

<h2>4. 저장 위치와 보유 기간</h2>
<p>설정과 플레이 기록은 기기에 저장됩니다. 최근 경기 기록은 최대 50개이며, 누적 경기 수·승리 수·최고 점수 같은 요약 기록은 따로 유지됩니다. EOS 계정이 준비되면 기록이 Epic Online Services 클라우드 저장소에 자동으로 동기화될 수 있습니다. 클라우드 기록은 정해진 기간이 지나도 자동 삭제되지 않으며, 덮어쓰이거나 이용자가 삭제를 요청할 때까지 유지됩니다. 게임이나 로컬 파일을 지워도 클라우드 데이터는 삭제되지 않습니다.</p>
<p>음성 채팅은 실시간으로 전송되며, 게임은 이를 녹음하거나 저장하지 않습니다. 음성과 네트워크 전송에 필요한 처리는 서비스 제공자의 정책을 따릅니다.</p>
<p>문의 이메일은 요청을 처리하는 데 필요한 기간만 보관하며, 법령상 더 오래 보관해야 하는 경우는 예외로 합니다. 보유 기간이 끝난 정보는 복구할 수 없는 방법으로 전자 파일을 삭제합니다.</p>

<h2>5. 처리 위탁 업체와 다른 플레이어</h2>
<p>회사는 아래 업체를 이용하며, 각 업체는 자체 개인정보처리방침에 따라 정보를 처리합니다.</p>
<ul>
<li><strong>Epic Games, Inc.</strong>(Epic Online Services): 로그인, 계정 연결, 로비·P2P 연결, 음성 채팅, 플레이 기록 클라우드 저장</li>
<li><strong>Discord Inc.</strong>: 이용자가 연결한 Discord 계정의 로그인</li>
<li><strong>Unity Technologies</strong>(Unity Cloud Diagnostics): 크래시·오류 보고</li>
<li><strong>Valve Corporation</strong>(Steam): Steam 버전의 업적과 친구 초대</li>
<li><strong>GitHub, Inc.</strong>: 이 웹사이트 호스팅</li>
</ul>
<p>스토어 구매, 플랫폼 계정, 결제는 Apple, Google, Valve가 각자의 정책에 따라 처리합니다. 회사는 결제 카드 정보를 받지 않습니다.</p>
<p>온라인 플레이 중에는 닉네임, 게임 진행 정보, 이용자가 전송한 음성이 같은 세션의 다른 플레이어에게 전달됩니다. 연결 방식에 따라 IP 주소 같은 기술 정보가 중계 서비스나 다른 플레이어에게 보일 수 있습니다.</p>
<p>회사는 개인정보를 판매하지 않으며 맞춤형 광고를 위해 공유하지 않습니다.</p>
{links([("epic", "Epic Games 개인정보처리방침"), ("discord", "Discord 개인정보처리방침"), ("unity", "Unity 개인정보처리방침"), ("steam", "Steam 개인정보처리방침"), ("github", "GitHub 개인정보처리방침")])}

<h2>6. 웹사이트와 광고·분석</h2>
<p>이 웹사이트는 GitHub Pages로 제공됩니다. 광고, 방문 분석 스크립트, 추적 쿠키가 없습니다. GitHub는 호스팅 서비스를 제공하고 보호하기 위해 IP 주소 등 접속 정보를 처리할 수 있습니다. 게임에는 광고나 행동 분석 SDK가 없으며, 게임이 보내는 진단 정보는 3항의 크래시·오류 보고뿐입니다.</p>

<h2>7. 이용자의 권리와 선택</h2>
<p>이용자는 자신의 정보에 대한 열람, 정정, 삭제, 이동(내보내기), 외부 계정 연결 해제, 처리 정지 및 처리 반대를 요청할 수 있습니다. 요청은 {MAIL}로 보내 주세요. 기록을 찾을 수 있도록 게임 닉네임, 플레이하는 플랫폼, 연결한 계정 종류를 함께 적어 주시면 됩니다. 본인 확인을 위해 추가 정보를 요청할 수 있습니다. 비밀번호, 인증 코드, 접근 토큰은 절대 보내지 마세요.</p>
<p>회사는 지체 없이, 관계 법령이 정한 기간 안에 답변합니다(예: 개인정보 보호법상 10일, GDPR상 1개월).</p>
<p>Epic Games나 Discord 계정 설정에서도 게임의 접근 권한을 철회할 수 있습니다. 외부 서비스의 권한 철회와 게임 저장 데이터 삭제는 서로 다른 절차입니다. 음성 채팅은 옵션에서 누르는 동안만 말하기로 바꾸거나, 기기 설정에서 마이크 권한을 거부할 수 있습니다.</p>

<h2>8. 해외 이용자 안내</h2>
<h3>8.1 개인정보의 국외 이전</h3>
<p>회사는 대한민국에 있습니다. 회사가 이용하는 업체는 미국 등 해외 서버에서 정보를 처리합니다. 정보는 이용자가 해당 기능을 사용할 때 네트워크를 통해 전송됩니다.</p>
{table(["이전받는 자", "국가", "이전 항목", "목적", "보유 기간"], [
    ["Epic Games, Inc.", "미국 및 기타 EOS 지역", "식별자, 닉네임, 게임 진행·플레이 기록, 전송 중인 음성, 네트워크 정보", "온라인 서비스, 음성 채팅, 클라우드 저장", "삭제 요청 시까지 또는 Epic 정책에 따름"],
    ["Discord Inc.", "미국", "Discord 계정 식별자, 기본 프로필", "계정 연결", "Discord 정책에 따름"],
    ["Unity Technologies SF", "미국", "크래시·오류 보고", "크래시 진단", "Unity 보관 기간 이내"],
    ["Valve Corporation", "미국", "Steam 계정 식별자, 업적, 초대 방 코드", "Steam 기능", "Valve 정책에 따름"],
    ["GitHub, Inc.", "미국", "웹사이트 접속 정보", "웹사이트 호스팅", "GitHub 정책에 따름"],
], wide=True)}
<p>필요한 경우 각 업체가 제공하는 표준계약조항(EU Standard Contractual Clauses) 등의 보호 조치를 적용합니다. 해당 기능을 쓰지 않거나 회사에 요청해 국외 이전을 거부할 수 있습니다. 이 경우 온라인 플레이, 계정 연결, 클라우드 저장, 크래시 진단을 이용하지 못할 수 있습니다.</p>

<h3>8.2 유럽경제지역(EEA)·영국·스위스</h3>
<p>GDPR 및 UK GDPR에 따라 회사는 이용자 정보의 컨트롤러입니다. 회사는 다음 법적 근거에 따라 처리합니다.</p>
<ul>
<li><strong>계약 이행</strong>: 로그인, 온라인 플레이, 음성 채팅, 기록 저장과 동기화</li>
<li><strong>동의</strong>: Epic·Discord 계정 연결. 연결을 해제하거나 회사에 요청해 언제든 동의를 철회할 수 있습니다.</li>
<li><strong>정당한 이익</strong>: 게임을 안정적이고 안전하게 유지하기 위한 크래시·오류 보고, 보안과 부정 이용 방지, 웹사이트 호스팅. 언제든 반대할 수 있습니다.</li>
<li><strong>법적 의무</strong>: 법령에 따라 정보를 보관하거나 제공해야 하는 경우</li>
</ul>
<p>이용자는 데이터 이동권과 거주 국가 개인정보 감독기관에 민원을 제기할 권리가 있습니다. 회사는 이용자에게 법적 효과나 그와 비슷한 중대한 영향을 주는 자동화된 결정만으로 판단하지 않습니다.</p>

<h3>8.3 미국 캘리포니아 및 기타 주</h3>
<p>회사는 CCPA/CPRA에서 정의하는 개인정보 판매(sell)나 공유(share)를 하지 않으며, 민감한 개인정보로 이용자의 특성을 추론하지 않습니다. 지난 12개월 동안 수집한 범주는 식별자(계정 ID, 기기 식별자, IP 주소), 인터넷·네트워크 활동(게임 진행·연결 정보, 크래시 보고), 음성 정보(음성 채팅으로 전송되며 녹음하지 않음)입니다. 이용자는 직접 또는 대리인을 통해 열람, 정정, 삭제를 요청할 수 있으며, 권리 행사를 이유로 차별받지 않습니다.</p>

<h3>8.4 대한민국</h3>
<p>개인정보 보호책임자: MeMe Games, {MAIL}. 개인정보 침해에 대한 상담이나 구제가 필요하면 개인정보침해 신고센터(privacy.kisa.or.kr, 국번 없이 118)나 개인정보 분쟁조정위원회(www.kopico.go.kr, 1833-6972)에도 문의할 수 있습니다.</p>

<h2>9. 아동</h2>
<p>이 게임은 13세 미만 아동을 대상으로 하지 않습니다. 더 높은 연령 기준이 있는 지역(예: 대한민국 14세 미만, 일부 EEA 국가 16세 미만)에서는 해당 연령 미만 아동이 법정대리인의 동의를 받아야 온라인 기능, 계정 연결, 음성 채팅을 이용할 수 있습니다. 아동이 동의 없이 정보를 제공했다고 생각되면 회사에 알려 주세요. 해당 정보를 삭제합니다.</p>

<h2>10. 안전성 확보 조치</h2>
<p>회사는 게임에 필요한 정보만 수집하고, 로그인과 온라인 플레이에는 업체의 암호화된 연결을 사용하며, 비밀번호와 Discord 접근 토큰을 저장하지 않습니다. 완벽하게 안전한 전송 방법은 없지만 이용자 정보를 보호하기 위해 노력합니다.</p>

<h2>11. 방침 변경</h2>
<p>게임이나 법령이 바뀌면 이 방침을 갱신하고 상단에 새 시행일을 표시합니다. 중요한 변경은 게임이나 이 웹사이트에서도 알립니다.</p>

<h2>12. 언어와 문의</h2>
<p>이 방침의 원문은 영어이며 다른 언어 번역본을 함께 제공합니다. 번역본과 영어 원문의 내용이 다르면 영어 원문을 우선합니다. 다만 현지 법령이 달리 정하는 경우에는 그에 따릅니다.</p>
<p>MeMe Games · {MAIL}</p>
""",
)

# ---------------------------------------------------------------- Japanese
TEXT["ja"] = dict(
    title="プライバシーポリシー",
    game="みんなのジレンマ",
    desc="MeMe Games『みんなのジレンマ（TrolleyDilemma）』のプライバシーポリシー。",
    nav_label="メインメニュー", nav_game="ゲーム紹介", nav_privacy="プライバシー", contact="お問い合わせ",
    lang_label="言語",
    body=f"""
<p>MeMe Games（以下「当社」）は『みんなのジレンマ（TrolleyDilemma）』を制作しています。本ポリシーでは、すべてのプラットフォームでゲームをプレイするとき、および本ウェブサイトを訪れるときに、当社がどのような情報を何のために取り扱うか、またお客様が選べることについて説明します。</p>
<p class="small">施行日：2026年10月5日 · 管理者：MeMe Games · お問い合わせ：{MAIL}</p>

<h2>1. 取り扱う情報と目的</h2>
{table(["機能", "情報", "目的"], [
    ["基本ログイン", "EOSデバイスベースの識別子、Product User ID、ログイン状態", "プレイヤーの識別とオンラインサービスの提供"],
    ["任意のアカウント連携", "EpicまたはDiscordのアカウント識別子、要求する権限の範囲内の基本プロフィール（表示名など）、認証トークン", "お客様が選んだ外部アカウントとゲームデータの連携"],
    ["オンラインプレイ", "ニックネーム、ロビー・セッションおよびゲーム進行の情報、接続に必要なネットワーク情報（IPアドレスなど）", "プレイヤーの接続とゲーム状態の同期"],
    ["ボイスチャット", "マイクから送信する音声", "同じボイスチャンネルのプレイヤー同士の会話"],
    ["保存と同期", "ニックネーム、試合の日時・モード・人数・オンラインかどうか・スコア・到達日数・勝敗・陣営・MVP・勝者、累計記録、実績と装備中のコスメ", "プレイ記録の保存とEOSクラウドへの同期"],
    ["Steam機能", "Steamアカウント識別子、解除した実績、送った招待に含まれるルームコード", "Steam実績とフレンド招待（Steam版のみ）"],
    ["クラッシュ・エラーレポート", "エラーメッセージとスタックトレース、直近のログ数行、ゲームのバージョン、プラットフォーム、OS、端末モデルとハードウェア情報、エラー発生時刻、Unityが付与する匿名の端末識別子", "クラッシュやエラーの原因究明と修正"],
    ["お問い合わせ", "メールアドレスとお問い合わせの内容", "お問い合わせの確認と回答"],
])}

<h2>2. アカウント連携と認証</h2>
<p>EpicやDiscordとの連携は任意です。ゲームは各サービスのログイン画面を開くだけで、パスワードを尋ねたり受け取ったりしません。EpicはBasic Profile、Discordはidentifyの権限のみを要求し、フレンドリストやメールアドレスは要求しません。Discordのアクセストークンはログインの完了にのみ使い、ゲームのセーブファイルには保存しません。</p>

<h2>3. クラッシュ・エラーレポート</h2>
<p>ゲームがクラッシュしたり予期しないエラーが起きたりすると、Unity TechnologiesのサービスであるUnity Cloud Diagnosticsにレポートを送信します。レポートには、エラーメッセージとスタックトレース、ゲームログの最後の数行、ゲームのバージョン、プラットフォーム、OS、端末モデルとハードウェア情報（CPU・GPU・メモリなど）、エラー発生時刻、Unityが付与する匿名の端末識別子が含まれます。パスワード、メールアドレス、音声、チャットの内容は含まれません。ただし、ログにはゲーム内ニックネームやルームコードなどの技術的な情報が含まれることがあります。</p>
<p>レポートは問題の発見と修正にのみ使い、広告やプロフィール作成には使いません。問題の解決に必要な期間、Unityのサービスの保存期間内に限って保管します。</p>
<p>プラットフォームによっては、Apple、Google、Valveがクラッシュ情報を当社に提供することがあります。たとえば、お客様が端末でアプリデベロッパとの解析データ共有を許可している場合です。これらのレポートは各プラットフォームの設定とプライバシーポリシーに従います。</p>

<h2>4. 保存場所と保存期間</h2>
<p>設定とプレイ記録は端末に保存されます。直近の試合記録は最大50件で、累計試合数・勝利数・最高スコアなどの要約記録は別に保持されます。EOSアカウントが準備できると、記録がEpic Online Servicesのクラウドストレージに自動で同期されることがあります。クラウドの記録は一定期間が過ぎても自動では削除されず、上書きされるか、お客様から削除の依頼があるまで保持されます。ゲームやローカルファイルを削除しても、クラウドのデータは削除されません。</p>
<p>ボイスチャットはリアルタイムで送信され、ゲームが録音・保存することはありません。音声やネットワーク通信に必要な処理は、サービス提供者のポリシーに従います。</p>
<p>お問い合わせのメールは、対応に必要な期間に限って保管します（法令でより長い保管が必要な場合を除きます）。不要になった情報は、復元できない方法で電子ファイルを削除します。</p>

<h2>5. 委託先と他のプレイヤー</h2>
<p>当社は次の事業者を利用しており、各事業者はそれぞれのプライバシーポリシーに従って情報を取り扱います。</p>
<ul>
<li><strong>Epic Games, Inc.</strong>（Epic Online Services）：ログイン、アカウント連携、ロビー・P2P接続、ボイスチャット、プレイ記録のクラウド保存</li>
<li><strong>Discord Inc.</strong>：お客様が連携するDiscordアカウントのログイン</li>
<li><strong>Unity Technologies</strong>（Unity Cloud Diagnostics）：クラッシュ・エラーレポート</li>
<li><strong>Valve Corporation</strong>（Steam）：Steam版の実績とフレンド招待</li>
<li><strong>GitHub, Inc.</strong>：本ウェブサイトのホスティング</li>
</ul>
<p>ストアでの購入、プラットフォームのアカウント、決済は、Apple、Google、Valveがそれぞれのポリシーに従って取り扱います。当社がお支払いカードの情報を受け取ることはありません。</p>
<p>オンラインプレイ中は、ニックネーム、ゲーム進行の情報、お客様が送信した音声が同じセッションの他のプレイヤーに共有されます。接続方法によっては、IPアドレスなどの技術的な情報が中継サービスや他のプレイヤーに見えることがあります。</p>
<p>当社は個人情報を販売せず、ターゲティング広告のために共有することもありません。</p>
{links([("epic", "Epic Games プライバシーポリシー"), ("discord", "Discord プライバシーポリシー"), ("unity", "Unity プライバシーポリシー"), ("steam", "Steam プライバシーポリシー"), ("github", "GitHub プライバシーステートメント")])}

<h2>6. ウェブサイトと広告・解析</h2>
<p>本ウェブサイトはGitHub Pagesで提供しています。広告、アクセス解析スクリプト、トラッキングCookieはありません。GitHubはホスティングサービスの提供と保護のため、IPアドレスなどのアクセス情報を取り扱うことがあります。ゲームには広告や行動解析のSDKはなく、ゲームが送信する診断情報は第3項のクラッシュ・エラーレポートのみです。</p>

<h2>7. お客様の権利と選択</h2>
<p>お客様は、ご自身の情報の開示、訂正、削除、エクスポート、外部アカウント連携の解除、処理の制限や処理への異議を当社に求めることができます。ご依頼は{MAIL}までお送りください。記録を探せるよう、ゲーム内ニックネーム、プレイしているプラットフォーム、連携しているアカウントの種類をお書き添えください。ご本人確認のため追加の情報をお願いすることがあります。パスワード、認証コード、アクセストークンは絶対に送らないでください。</p>
<p>当社は遅滞なく、適用される法令が定める期間内（例：GDPRでは1か月、韓国の個人情報保護法では10日）に回答します。</p>
<p>Epic GamesやDiscordのアカウント設定からも、ゲームのアクセス権限を取り消せます。外部サービスでの権限の取り消しと、ゲームの保存データの削除は別の手続きです。ボイスチャットは、オプションでプッシュトゥトークに切り替えるか、端末の設定でマイクへのアクセスを拒否できます。</p>

<h2>8. 海外のお客様へ</h2>
<h3>8.1 国外への移転</h3>
<p>当社は大韓民国に所在しています。当社が利用する事業者は、米国などの国外のサーバーで情報を取り扱います。情報は、お客様が該当する機能を使うときにネットワークを通じて送信されます。</p>
{table(["移転先", "国", "項目", "目的", "保存期間"], [
    ["Epic Games, Inc.", "米国およびその他のEOS地域", "識別子、ニックネーム、ゲーム進行・プレイ記録、送信中の音声、ネットワーク情報", "オンラインサービス、ボイスチャット、クラウド保存", "削除のご依頼まで、またはEpicのポリシーによる"],
    ["Discord Inc.", "米国", "Discordアカウント識別子、基本プロフィール", "アカウント連携", "Discordのポリシーによる"],
    ["Unity Technologies SF", "米国", "クラッシュ・エラーレポート", "クラッシュの診断", "Unityの保存期間内"],
    ["Valve Corporation", "米国", "Steamアカウント識別子、実績、招待のルームコード", "Steam機能", "Valveのポリシーによる"],
    ["GitHub, Inc.", "米国", "ウェブサイトのアクセス情報", "ウェブサイトのホスティング", "GitHubのポリシーによる"],
], wide=True)}
<p>必要な場合、これらの移転には欧州委員会の標準契約条項など、各事業者が提供する保護措置が適用されます。該当する機能を使わないか当社にご連絡いただくことで移転を拒否できますが、その場合はオンラインプレイ、アカウント連携、クラウド保存、クラッシュの診断を利用できないことがあります。</p>

<h3>8.2 欧州経済領域（EEA）・英国・スイス</h3>
<p>GDPRおよびUK GDPRにおいて、当社はお客様の情報の管理者（controller）です。当社は次の法的根拠に基づいて取り扱います。</p>
<ul>
<li><strong>契約の履行</strong>：ログイン、オンラインプレイ、ボイスチャット、記録の保存と同期</li>
<li><strong>同意</strong>：EpicまたはDiscordアカウントの連携。連携の解除または当社へのご連絡により、いつでも同意を撤回できます。</li>
<li><strong>正当な利益</strong>：ゲームを安定・安全に保つためのクラッシュ・エラーレポート、セキュリティと不正利用の防止、ウェブサイトのホスティング。いつでも異議を申し立てられます。</li>
<li><strong>法的義務</strong>：法令により情報の保管や開示が必要な場合</li>
</ul>
<p>お客様には、データポータビリティの権利と、お住まいの国のデータ保護当局に苦情を申し立てる権利もあります。当社は、お客様に法的効果やそれと同等の重大な影響を与える決定を、自動処理のみに基づいて行うことはありません。</p>

<h3>8.3 米国カリフォルニア州およびその他の州</h3>
<p>当社は、CCPA/CPRAで定義される個人情報の販売（sell）や共有（share）を行わず、センシティブな個人情報からお客様の特性を推測することもありません。過去12か月に収集したカテゴリーは、識別子（アカウントID、端末識別子、IPアドレス）、インターネットその他のネットワーク活動（ゲーム進行・接続の情報、クラッシュレポート）、音声情報（ボイスチャットで送信され、録音はしません）です。お客様はご本人または代理人を通じて、開示、訂正、削除を求めることができ、権利の行使を理由に差別されることはありません。</p>

<h3>8.4 大韓民国</h3>
<p>個人情報保護責任者：MeMe Games、{MAIL}。個人情報の侵害について相談や救済が必要な場合は、個人情報侵害申告センター（privacy.kisa.or.kr、118）または個人情報紛争調停委員会（www.kopico.go.kr、1833-6972）にもお問い合わせいただけます。</p>

<h2>9. お子様について</h2>
<p>本ゲームは13歳未満のお子様を対象としていません。より高い年齢基準がある地域（例：韓国では14歳未満、一部のEEA諸国では16歳未満）では、その年齢未満のお子様は保護者の同意を得たうえでオンライン機能、アカウント連携、ボイスチャットをご利用ください。お子様が同意なく情報を提供したと思われる場合はご連絡ください。該当する情報を削除します。</p>

<h2>10. 安全管理</h2>
<p>当社はゲームに必要な情報だけを収集し、ログインとオンラインプレイには事業者の暗号化された接続を利用し、パスワードやDiscordのアクセストークンは保存しません。完全に安全な送信方法はありませんが、お客様の情報の保護に努めます。</p>

<h2>11. 本ポリシーの変更</h2>
<p>ゲームや法令が変わった場合は本ポリシーを更新し、冒頭に新しい施行日を表示します。重要な変更は、ゲーム内または本ウェブサイトでもお知らせします。</p>

<h2>12. 言語とお問い合わせ</h2>
<p>本ポリシーは英語で作成され、他の言語に翻訳されています。翻訳と英語版の内容が異なる場合は英語版が優先します。ただし、現地の法令に別段の定めがある場合はそれに従います。</p>
<p>MeMe Games · {MAIL}</p>
""",
)

# ---------------------------------------------------------------- Simplified Chinese
TEXT["zh-Hans"] = dict(
    title="隐私政策",
    game="大家的困境",
    desc="MeMe Games《大家的困境（TrolleyDilemma）》隐私政策。",
    nav_label="主菜单", nav_game="游戏介绍", nav_privacy="隐私", contact="联系我们",
    lang_label="语言",
    body=f"""
<p>MeMe Games（以下简称"我们"）制作了《大家的困境（TrolleyDilemma）》。本政策说明您在任何平台上游玩本游戏或访问本网站时，我们处理哪些信息、出于什么目的，以及您可以做出的选择。</p>
<p class="small">生效日期：2026年10月5日 · 控制者：MeMe Games · 联系方式：{MAIL}</p>

<h2>1. 我们处理的信息及目的</h2>
{table(["功能", "信息", "目的"], [
    ["基本登录", "EOS 设备标识符、Product User ID、登录状态", "识别玩家并提供在线服务"],
    ["可选的账户关联", "Epic 或 Discord 账户标识符、所请求权限范围内的基本资料（如显示名称）、认证令牌", "将您选择的外部账户与游戏数据关联"],
    ["在线游戏", "昵称、大厅、会话和游戏进度信息、连接所需的网络信息（如 IP 地址）", "连接玩家并同步游戏状态"],
    ["语音聊天", "您通过麦克风发送的语音", "让同一语音频道的玩家相互交谈"],
    ["保存与同步", "昵称、对局时间、模式、人数、是否在线、分数、到达天数、胜负、阵营、MVP、胜者、累计记录、成就及已装备的装扮", "保存游戏记录并同步到 EOS 云存储"],
    ["Steam 功能", "Steam 账户标识符、已解锁的成就、您发送的邀请中包含的房间代码", "Steam 成就和好友邀请（仅限 Steam 版）"],
    ["崩溃和错误报告", "错误信息和堆栈跟踪、最近几行日志、游戏版本、平台、操作系统、设备型号和硬件信息、错误发生时间、Unity 分配的匿名设备标识符", "查找并修复崩溃和错误"],
    ["咨询", "您的电子邮件地址及咨询内容", "确认并回复您的咨询"],
])}

<h2>2. 账户关联与登录</h2>
<p>关联 Epic 或 Discord 账户完全由您选择。游戏只会打开相应服务自己的登录页面，不会询问或接收您的密码。我们只请求 Epic 的 Basic Profile 权限和 Discord 的 identify 权限，不请求您的好友列表或电子邮件地址。Discord 访问令牌仅用于完成登录，不会保存在游戏存档文件中。</p>

<h2>3. 崩溃和错误报告</h2>
<p>当游戏崩溃或出现意外错误时，游戏会通过 Unity Technologies 提供的 Unity Cloud Diagnostics 发送报告。报告包含错误信息和堆栈跟踪、游戏日志的最后几行、游戏版本、平台、操作系统、设备型号和硬件信息（如 CPU、GPU 和内存）、错误发生时间，以及 Unity 分配的匿名设备标识符。报告不包含您的密码、电子邮件地址、语音或聊天内容，但日志中可能含有游戏内昵称或房间代码等技术信息。</p>
<p>我们仅将报告用于查找和修复问题，不会用于广告或建立用户画像。报告仅在解决问题所需的期间内、并在 Unity 服务的保留期限内保存。</p>
<p>根据平台不同，Apple、Google 或 Valve 也可能向我们提供崩溃信息，例如当您在设备上选择与应用开发者共享分析数据时。这些报告遵循各平台的设置和隐私政策。</p>

<h2>4. 存储位置与保留期限</h2>
<p>设置和游戏记录保存在您的设备上。游戏最多保留 50 场最近的对局记录，另外保留总对局数、胜场数和最高分等汇总记录。当 EOS 账户可用时，记录可能会自动同步到 Epic Online Services 云存储。云端记录不会在固定期限后自动删除，而是保留到被覆盖或您要求我们删除为止。删除游戏或本地文件不会删除云端数据。</p>
<p>语音聊天实时传输，游戏不会录制或保存。传输语音和网络流量所需的处理遵循服务提供商的政策。</p>
<p>您发给我们的电子邮件仅在处理请求所需的期间内保存，法律要求更长保存期限的除外。不再需要的信息，我们会以无法恢复的方式删除电子文件。</p>

<h2>5. 服务提供商与其他玩家</h2>
<p>我们使用以下服务提供商，各提供商依照其自身的隐私政策处理信息。</p>
<ul>
<li><strong>Epic Games, Inc.</strong>（Epic Online Services）：登录、账户关联、大厅与 P2P 连接、语音聊天、游戏记录云存储</li>
<li><strong>Discord Inc.</strong>：您选择关联的 Discord 账户登录</li>
<li><strong>Unity Technologies</strong>（Unity Cloud Diagnostics）：崩溃和错误报告</li>
<li><strong>Valve Corporation</strong>（Steam）：Steam 版的成就和好友邀请</li>
<li><strong>GitHub, Inc.</strong>：托管本网站</li>
</ul>
<p>商店购买、平台账户和付款由 Apple、Google 和 Valve 依照其各自政策处理。我们不会收到您的支付卡信息。</p>
<p>在线游戏期间，您的昵称、游戏进度信息和您发送的语音会与同一会话中的其他玩家共享。根据玩家之间的连接方式，IP 地址等技术信息可能会被中继服务或其他玩家看到。</p>
<p>我们不会出售您的个人信息，也不会为定向广告而共享您的个人信息。</p>
{links([("epic", "Epic Games 隐私政策"), ("discord", "Discord 隐私政策"), ("unity", "Unity 隐私政策"), ("steam", "Steam 隐私政策"), ("github", "GitHub 隐私声明")])}

<h2>6. 网站、广告与分析</h2>
<p>本网站由 GitHub Pages 提供。网站上没有广告、访问分析脚本或跟踪 Cookie。GitHub 可能为提供和保护托管服务而处理 IP 地址等访问信息。游戏中没有广告或行为分析 SDK，游戏发送的诊断信息只有第 3 条所述的崩溃和错误报告。</p>

<h2>7. 您的权利与选择</h2>
<p>您可以要求我们查阅、更正、删除或导出您的信息，解除外部账户与游戏数据的关联，或限制处理、反对处理。请将请求发送至 {MAIL}。为便于查找您的记录，请写明游戏内昵称、游玩的平台以及已关联账户的类型。我们可能会要求提供更多信息以确认请求来自您本人。请勿发送密码、验证码或访问令牌。</p>
<p>我们会在不无故拖延的情况下，于适用法律规定的期限内答复（例如 GDPR 规定的一个月，或韩国《个人信息保护法》规定的 10 天）。</p>
<p>您也可以在 Epic Games 或 Discord 的账户设置中撤销游戏的访问权限。在外部服务撤销权限与删除游戏保存的数据是两个独立的步骤。对于语音聊天，您可以在选项中改为按键通话，或在设备设置中拒绝麦克风权限。</p>

<h2>8. 海外用户须知</h2>
<h3>8.1 跨境传输</h3>
<p>MeMe Games 位于大韩民国。我们使用的服务提供商在美国等其他国家的服务器上处理信息。当您使用相关功能时，信息会通过网络传输给这些提供商。</p>
{table(["接收方", "国家", "信息", "目的", "保留期限"], [
    ["Epic Games, Inc.", "美国及其他 EOS 地区", "标识符、昵称、游戏进度与记录、传输中的语音、网络信息", "在线服务、语音聊天、云存档", "直至您要求删除，或依照 Epic 的政策"],
    ["Discord Inc.", "美国", "Discord 账户标识符、基本资料", "账户关联", "依照 Discord 的政策"],
    ["Unity Technologies SF", "美国", "崩溃和错误报告", "崩溃诊断", "在 Unity 的保留期限内"],
    ["Valve Corporation", "美国", "Steam 账户标识符、成就、邀请中的房间代码", "Steam 功能", "依照 Valve 的政策"],
    ["GitHub, Inc.", "美国", "网站访问信息", "网站托管", "依照 GitHub 的政策"],
], wide=True)}
<p>在需要时，这些传输受到提供商所提供的保护措施保障，例如欧盟委员会的标准合同条款。您可以通过不使用相关功能或联系我们来拒绝传输，但届时可能无法使用在线游戏、账户关联、云存档或崩溃诊断。</p>

<h3>8.2 欧洲经济区、英国和瑞士</h3>
<p>根据 GDPR 和英国 GDPR，MeMe Games 是您信息的控制者。我们依据以下法律基础处理信息：</p>
<ul>
<li><strong>履行合同</strong>：登录、在线游戏、语音聊天、保存和同步记录</li>
<li><strong>同意</strong>：关联 Epic 或 Discord 账户。您可以随时通过解除关联或联系我们撤回同意。</li>
<li><strong>正当利益</strong>：为保持游戏稳定和安全而进行的崩溃和错误报告、安全与防止滥用、网站托管。您可以随时提出反对。</li>
<li><strong>法律义务</strong>：法律要求我们保存或披露信息时</li>
</ul>
<p>您还享有数据可携带权，以及向您所在地数据保护机构投诉的权利。我们不会仅基于自动化处理做出对您产生法律效力或类似重大影响的决定。</p>

<h3>8.3 美国加利福尼亚州及其他州</h3>
<p>我们不会进行 CCPA/CPRA 所定义的个人信息出售（sell）或共享（share），也不会利用敏感个人信息推断您的特征。过去 12 个月中，我们收集的信息类别包括：标识符（账户 ID、设备标识符、IP 地址）、互联网或其他网络活动（游戏进度与连接信息、崩溃报告）以及音频信息（通过语音聊天发送，不会录制）。您可以本人或通过授权代理人要求查阅、更正或删除信息，我们不会因您行使这些权利而歧视您。</p>

<h3>8.4 大韩民国</h3>
<p>个人信息保护负责人：MeMe Games，{MAIL}。如需就个人信息侵害寻求咨询或救济，您也可以联系个人信息侵害举报中心（privacy.kisa.or.kr，118）或个人信息纠纷调解委员会（www.kopico.go.kr，1833-6972）。</p>

<h2>9. 儿童</h2>
<p>本游戏不面向 13 岁以下的儿童。在适用更高年龄标准的地区（例如韩国为 14 岁以下，部分欧洲经济区国家为 16 岁以下），未满该年龄的儿童应在父母或监护人同意后才使用在线功能、账户关联和语音聊天。如果您认为有儿童在未经同意的情况下向我们提供了信息，请联系我们，我们将予以删除。</p>

<h2>10. 安全</h2>
<p>我们只收集游戏所需的信息，登录和在线游戏使用服务提供商的加密连接，并且不保存密码或 Discord 访问令牌。没有任何传输方式是绝对安全的，但我们会努力保护您的信息。</p>

<h2>11. 本政策的变更</h2>
<p>当游戏或法律发生变化时，我们会更新本政策，并在顶部标明新的生效日期。对于重大变更，我们还会在游戏内或本网站上发布通知。</p>

<h2>12. 语言与联系方式</h2>
<p>本政策以英文撰写，并翻译为其他语言。如译文与英文版本不一致，以英文版本为准，但当地法律另有规定的除外。</p>
<p>MeMe Games · {MAIL}</p>
""",
)

# ---------------------------------------------------------------- French
TEXT["fr"] = dict(
    title="Politique de confidentialité",
    game="Dilemme collectif",
    desc="Politique de confidentialité de Dilemme collectif (TrolleyDilemma) par MeMe Games.",
    nav_label="Menu principal", nav_game="Le jeu", nav_privacy="Confidentialité", contact="Contact",
    lang_label="Langue",
    body=f"""
<p>MeMe Games (« nous ») développe Dilemme collectif (TrolleyDilemma). Cette politique explique quelles informations nous traitons lorsque vous jouez au jeu sur n'importe quelle plateforme ou visitez ce site, pourquoi nous les traitons et quels choix s'offrent à vous.</p>
<p class="small">Date d'entrée en vigueur : 5 octobre 2026 · Responsable du traitement : MeMe Games · Contact : {MAIL}</p>

<h2>1. Informations traitées et finalités</h2>
{table(["Fonction", "Informations", "Finalité"], [
    ["Connexion de base", "Identifiant EOS lié à l'appareil, Product User ID, état de connexion", "Identifier les joueurs et fournir les services en ligne"],
    ["Liaison de compte facultative", "Identifiant du compte Epic ou Discord, profil de base dans la limite des autorisations demandées (comme le nom affiché), jetons d'authentification", "Lier le compte externe de votre choix à vos données de jeu"],
    ["Jeu en ligne", "Pseudo, données de salon, de session et de partie, informations réseau nécessaires à la connexion (comme l'adresse IP)", "Connecter les joueurs et synchroniser la partie"],
    ["Chat vocal", "La voix que vous transmettez par votre micro", "Permettre aux joueurs d'un même canal vocal de se parler"],
    ["Sauvegarde et synchronisation", "Pseudo, date, mode et nombre de joueurs de la partie, en ligne ou non, score, jour atteint, victoire ou défaite, camp, MVP, gagnant, statistiques cumulées, succès et cosmétiques équipés", "Enregistrer votre historique et le synchroniser avec le stockage cloud EOS"],
    ["Fonctions Steam", "Identifiant du compte Steam, succès débloqués, code de salon contenu dans les invitations que vous envoyez", "Succès Steam et invitations d'amis (version Steam uniquement)"],
    ["Rapports de plantage et d'erreur", "Message d'erreur et trace de pile, dernières lignes du journal, version du jeu, plateforme, système d'exploitation, modèle et matériel de l'appareil, heure de l'erreur, identifiant d'appareil anonyme attribué par Unity", "Trouver et corriger les plantages et les erreurs"],
    ["Demandes", "Votre adresse e-mail et le contenu de votre message", "Répondre à votre demande"],
])}

<h2>2. Liaison de compte et connexion</h2>
<p>La liaison d'un compte Epic ou Discord est facultative. Le jeu ouvre la page de connexion du service concerné et ne demande ni ne reçoit jamais votre mot de passe. Nous demandons uniquement l'autorisation Basic Profile d'Epic et l'autorisation identify de Discord ; nous ne demandons ni votre liste d'amis ni votre adresse e-mail. Le jeton d'accès Discord sert uniquement à finaliser la connexion et n'est pas conservé dans les fichiers de sauvegarde du jeu.</p>

<h2>3. Rapports de plantage et d'erreur</h2>
<p>Lorsque le jeu plante ou rencontre une erreur inattendue, il envoie un rapport via Unity Cloud Diagnostics, un service de Unity Technologies. Le rapport contient le message d'erreur et la trace de pile, les dernières lignes du journal du jeu, la version du jeu, la plateforme, le système d'exploitation, le modèle et le matériel de l'appareil (processeur, carte graphique, mémoire, etc.), l'heure de l'erreur et un identifiant d'appareil anonyme attribué par Unity. Il ne contient ni votre mot de passe, ni votre adresse e-mail, ni votre voix, ni le contenu de vos discussions. Le journal peut toutefois contenir des informations techniques comme votre pseudo ou un code de salon.</p>
<p>Nous utilisons ces rapports uniquement pour trouver et corriger des problèmes, jamais à des fins publicitaires ni de profilage. Ils sont conservés le temps nécessaire pour résoudre le problème, dans la limite de la durée de conservation du service Unity.</p>
<p>Selon la plateforme, Apple, Google ou Valve peuvent aussi nous transmettre des informations de plantage, par exemple si vous avez choisi sur votre appareil de partager les données d'analyse avec les développeurs. Ces rapports relèvent des réglages et de la politique de confidentialité de la plateforme.</p>

<h2>4. Stockage et durée de conservation</h2>
<p>Les réglages et l'historique de jeu sont stockés sur votre appareil. Le jeu conserve jusqu'à 50 parties récentes, ainsi que des statistiques récapitulatives comme le nombre total de parties, de victoires et le meilleur score. Lorsqu'un compte EOS est disponible, l'historique peut être synchronisé automatiquement avec le stockage cloud d'Epic Online Services. Les données cloud ne sont pas supprimées automatiquement après un délai fixe ; elles sont conservées jusqu'à ce qu'elles soient écrasées ou que vous nous demandiez de les supprimer. Supprimer le jeu ou ses fichiers locaux ne supprime pas les données cloud.</p>
<p>Le chat vocal est transmis en temps réel ; le jeu ne l'enregistre ni ne le conserve. Le traitement nécessaire au transport de la voix et du trafic réseau relève de la politique du prestataire.</p>
<p>Nous conservons les e-mails que vous nous envoyez le temps nécessaire pour traiter votre demande, sauf obligation légale de conservation plus longue. Lorsque des informations ne sont plus nécessaires, nous supprimons les fichiers électroniques de manière irréversible.</p>

<h2>5. Prestataires et autres joueurs</h2>
<p>Nous faisons appel aux prestataires suivants, qui traitent les informations selon leur propre politique de confidentialité.</p>
<ul>
<li><strong>Epic Games, Inc.</strong> (Epic Online Services) : connexion, liaison de compte, salons et connexions P2P, chat vocal, stockage cloud de l'historique</li>
<li><strong>Discord Inc.</strong> : connexion du compte Discord que vous choisissez de lier</li>
<li><strong>Unity Technologies</strong> (Unity Cloud Diagnostics) : rapports de plantage et d'erreur</li>
<li><strong>Valve Corporation</strong> (Steam) : succès et invitations d'amis dans la version Steam</li>
<li><strong>GitHub, Inc.</strong> : hébergement de ce site</li>
</ul>
<p>Apple, Google et Valve gèrent les achats en boutique, les comptes de plateforme et les paiements selon leurs propres politiques. Nous ne recevons jamais vos données de carte bancaire.</p>
<p>Pendant le jeu en ligne, votre pseudo, vos données de partie et la voix que vous transmettez sont partagés avec les autres joueurs de la session. Selon le mode de connexion entre joueurs, des informations techniques comme votre adresse IP peuvent être visibles par le service de relais ou par d'autres joueurs.</p>
<p>Nous ne vendons pas vos données personnelles et ne les partageons pas à des fins de publicité ciblée.</p>
{links([("epic", "Politique de confidentialité d'Epic Games"), ("discord", "Politique de confidentialité de Discord"), ("unity", "Politique de confidentialité de Unity"), ("steam", "Politique de confidentialité de Steam"), ("github", "Déclaration de confidentialité de GitHub")])}

<h2>6. Site web, publicité et mesure d'audience</h2>
<p>Ce site est servi par GitHub Pages. Il ne contient ni publicité, ni script de mesure d'audience, ni cookie de suivi. GitHub peut traiter des informations de connexion comme l'adresse IP pour fournir et sécuriser son service d'hébergement. Le jeu n'intègre aucun SDK publicitaire ni d'analyse comportementale ; les seules données de diagnostic qu'il envoie sont les rapports décrits à la section 3.</p>

<h2>7. Vos droits et vos choix</h2>
<p>Vous pouvez nous demander d'accéder à vos informations, de les rectifier, de les supprimer ou de les exporter, de délier un compte externe de vos données de jeu, ou de limiter le traitement ou de vous y opposer. Envoyez votre demande à {MAIL}. Pour nous aider à retrouver vos données, indiquez votre pseudo, la plateforme sur laquelle vous jouez et le type de compte lié, le cas échéant. Nous pouvons vous demander des informations supplémentaires pour vérifier que la demande vient bien de vous. N'envoyez jamais de mot de passe, de code de vérification ni de jeton d'accès.</p>
<p>Nous répondons dans les meilleurs délais et dans le délai prévu par la loi applicable (par exemple un mois selon le RGPD, ou 10 jours selon la loi coréenne sur la protection des informations personnelles).</p>
<p>Vous pouvez aussi révoquer l'accès du jeu dans les paramètres de votre compte Epic Games ou Discord. Révoquer cet accès et supprimer les données sauvegardées par le jeu sont deux démarches distinctes. Pour le chat vocal, vous pouvez activer le mode push-to-talk dans les options ou refuser l'accès au micro dans les réglages de votre appareil.</p>

<h2>8. Utilisateurs hors de Corée</h2>
<h3>8.1 Transferts hors de votre pays</h3>
<p>MeMe Games est établi en République de Corée. Nos prestataires traitent les informations sur des serveurs situés aux États-Unis et dans d'autres pays. Les informations leur sont transmises par le réseau lorsque vous utilisez la fonction concernée.</p>
{table(["Destinataire", "Pays", "Informations", "Finalité", "Conservation"], [
    ["Epic Games, Inc.", "États-Unis et autres régions EOS", "Identifiants, pseudo, données de partie et historique, voix en transit, informations réseau", "Services en ligne, chat vocal, sauvegardes cloud", "Jusqu'à votre demande de suppression, ou selon la politique d'Epic"],
    ["Discord Inc.", "États-Unis", "Identifiant du compte Discord, profil de base", "Liaison de compte", "Selon la politique de Discord"],
    ["Unity Technologies SF", "États-Unis", "Rapports de plantage et d'erreur", "Diagnostic des plantages", "Dans la limite de la durée de conservation de Unity"],
    ["Valve Corporation", "États-Unis", "Identifiant du compte Steam, succès, code de salon des invitations", "Fonctions Steam", "Selon la politique de Valve"],
    ["GitHub, Inc.", "États-Unis", "Informations de connexion au site", "Hébergement du site", "Selon la politique de GitHub"],
], wide=True)}
<p>Lorsque c'est nécessaire, ces transferts sont encadrés par des garanties proposées par les prestataires, comme les clauses contractuelles types de la Commission européenne. Vous pouvez refuser un transfert en n'utilisant pas la fonction concernée ou en nous contactant, mais le jeu en ligne, la liaison de compte, les sauvegardes cloud ou le diagnostic des plantages peuvent alors être indisponibles.</p>

<h3>8.2 Espace économique européen, Royaume-Uni et Suisse</h3>
<p>Au sens du RGPD et du RGPD britannique, MeMe Games est responsable du traitement de vos informations. Nous nous fondons sur les bases légales suivantes :</p>
<ul>
<li><strong>Exécution d'un contrat</strong> : connexion, jeu en ligne, chat vocal, sauvegarde et synchronisation de l'historique</li>
<li><strong>Consentement</strong> : liaison d'un compte Epic ou Discord. Vous pouvez retirer votre consentement à tout moment en déliant le compte ou en nous contactant.</li>
<li><strong>Intérêt légitime</strong> : rapports de plantage et d'erreur, sécurité et prévention des abus, hébergement du site, afin de garder le jeu stable et sûr. Vous pouvez vous y opposer à tout moment.</li>
<li><strong>Obligation légale</strong> : lorsque la loi nous impose de conserver ou de communiquer des informations</li>
</ul>
<p>Vous disposez également du droit à la portabilité des données et du droit d'introduire une réclamation auprès de l'autorité de protection des données de votre pays (en France, la CNIL). Nous ne prenons aucune décision fondée exclusivement sur un traitement automatisé produisant des effets juridiques ou des effets similaires significatifs à votre égard.</p>

<h3>8.3 Californie et autres États américains</h3>
<p>Nous ne vendons ni ne partageons de données personnelles au sens du CCPA/CPRA, et nous n'utilisons pas de données personnelles sensibles pour déduire vos caractéristiques. Au cours des 12 derniers mois, nous avons collecté les catégories suivantes : identifiants (identifiants de compte, identifiants d'appareil, adresses IP), activité sur Internet ou un autre réseau (données de partie et de connexion, rapports de plantage) et informations audio (voix transmise par le chat vocal, non enregistrée). Vous pouvez demander à connaître, rectifier ou supprimer vos informations, vous-même ou par l'intermédiaire d'un mandataire. Nous ne vous traiterons pas différemment parce que vous exercez ces droits.</p>

<h3>8.4 République de Corée</h3>
<p>Responsable de la protection des données : MeMe Games, {MAIL}. En cas d'atteinte à vos données personnelles, vous pouvez aussi contacter le Personal Information Infringement Report Center (privacy.kisa.or.kr, 118) ou le Personal Information Dispute Mediation Committee (www.kopico.go.kr, 1833-6972).</p>

<h2>9. Enfants</h2>
<p>Le jeu ne s'adresse pas aux enfants de moins de 13 ans. Là où un âge plus élevé s'applique (par exemple moins de 14 ans en Corée, ou moins de 15 ans en France et jusqu'à 16 ans dans certains pays de l'EEE), les enfants n'ayant pas atteint cet âge ne doivent utiliser les fonctions en ligne, la liaison de compte et le chat vocal qu'avec le consentement d'un parent ou tuteur. Si vous pensez qu'un enfant nous a fourni des informations sans ce consentement, contactez-nous et nous les supprimerons.</p>

<h2>10. Sécurité</h2>
<p>Nous ne collectons que ce dont le jeu a besoin, nous nous appuyons sur les connexions chiffrées de nos prestataires pour la connexion et le jeu en ligne, et nous ne conservons ni mots de passe ni jetons d'accès Discord. Aucune méthode de transmission n'est totalement sûre, mais nous nous efforçons de protéger vos informations.</p>

<h2>11. Modifications de cette politique</h2>
<p>Nous mettons à jour cette politique lorsque le jeu ou la loi évolue et indiquons la nouvelle date d'entrée en vigueur en haut de la page. En cas de changement important, nous vous en informerons aussi dans le jeu ou sur ce site.</p>

<h2>12. Langues et contact</h2>
<p>Cette politique est rédigée en anglais et traduite dans d'autres langues. En cas de divergence entre une traduction et la version anglaise, la version anglaise prévaut, sauf disposition contraire de la loi locale.</p>
<p>MeMe Games · {MAIL}</p>
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
    alternates = "".join(f'<link rel="alternate" hreflang="{c}" href="{SITE}/{f}">' for c, f, _ in LANGS)
    alternates += f'<link rel="alternate" hreflang="x-default" href="{SITE}/privacy.html">'
    body = " ".join(line.strip() for line in t["body"].strip().splitlines() if line.strip())
    return (
        f'<!doctype html><html lang="{code}"><head><meta charset="utf-8">'
        f'<meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<meta name="description" content="{t["desc"]}"><title>{t["title"]} · MeMe Games</title>'
        f'<link rel="canonical" href="{SITE}/{file}">{alternates}'
        f'<link rel="icon" type="image/png" href="assets/trolley-icon-128.png"><link rel="stylesheet" href="style.css?v={CSS_VERSION}"></head><body>'
        f'<nav aria-label="{t["nav_label"]}"><a class="brand" href="index.html">MeMe Games / TrolleyDilemma</a>'
        f'<div><a href="index.html#game">{t["nav_game"]}</a><a href="{file}">{t["nav_privacy"]}</a></div></nav>'
        f'<main class="policy"><span class="eyebrow">PRIVACY</span><h1>{t["title"]}</h1>'
        f'{lang_switcher(code, t["lang_label"])}{body}</main>'
        f'<footer><span>© 2026 MeMe Games · {t["game"]}</span>'
        f'<span><a href="{file}">{t["title"]}</a> · <a href="mailto:{EMAIL}">{t["contact"]}</a></span></footer>'
        f"</body></html>\n"
    )


if __name__ == "__main__":
    for code, file, _ in LANGS:
        (ROOT / file).write_text(page(code, file), encoding="utf-8")
        print("wrote", file)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════════
#  Atlasoyuncu G233 Vote — Minecraft Vote Bot v2.0
#  © 2026 Atlasoyuncu G233 Vote. Tüm hakları saklıdır.
#  Bu dosyayı değiştirirken / paylaşırken marka adını koru.
# ═══════════════════════════════════════════════════════════════════════
"""
Vote Engine - Orijinal atlas_vote_bot.py'deki üç voter sınıfını içerir.
Mevcut çalışma mantığı korunmuştur; sadece config entegrasyonu eklendi.
"""

import asyncio
import random
import time
from pathlib import Path
from datetime import datetime

from utils.logger import get_logger

logger = get_logger()


# ═══════════════════════════════════════════════════════════════════════════════
# YÖNTEM 1: SELENIUMBASE UC MODE
# ═══════════════════════════════════════════════════════════════════════════════

class SeleniumBaseVoter:
    def __init__(self, cfg):
        self.username      = cfg.get_vote_username()
        self.proxy         = cfg.get("proxy")
        self.headless      = cfg.get("headless", False)
        self.retry_count   = cfg.get("retry_count", 3)
        self.retry_delay   = cfg.get("retry_delay", 30)
        self.reconnect     = cfg.get("seleniumbase_reconnect", 6)
        self.captcha_svc   = cfg.get("captcha_service", "none").lower()
        self.captcha_key   = cfg.get("captcha_api_key", "") or ""
        self.captcha_timeout = cfg.get("captcha_timeout", 180)
        self.screenshots   = Path(cfg.get("screenshot_dir", "screenshots"))
        self.screenshots.mkdir(parents=True, exist_ok=True)

    def vote(self, site_key: str, site_cfg: dict) -> dict:
        from seleniumbase import Driver

        url            = site_cfg["url"]
        username_param = site_cfg.get("username_param")
        reconnect      = site_cfg.get("reconnect", self.reconnect)

        if username_param:
            url = f"{url}?{username_param}={self.username}"
            logger.info(f"📝 [{site_key}] Username parametresi eklendi: {url}")

        logger.info(f"🚀 [{site_key}] SeleniumBase UC Mode başlatılıyor...")

        for attempt in range(1, self.retry_count + 1):
            driver = None
            try:
                driver_kwargs = {"uc": True, "headless": self.headless}
                if self.proxy:
                    driver_kwargs["proxy"] = self.proxy

                driver = Driver(**driver_kwargs)

                logger.info(f"  📄 Sayfa yükleniyor (Deneme {attempt}/{self.retry_count})...")
                driver.uc_open_with_reconnect(url, reconnect_time=reconnect)

                logger.info("  ⏳ Cloudflare challenge çözülüyor...")
                time.sleep(random.uniform(4, 7))

                if not self.headless and site_cfg.get("gui_captcha", True):
                    logger.info("  🖱️ CAPTCHA kontrolü yapılıyor...")
                    driver.uc_gui_click_captcha()
                    time.sleep(random.uniform(2, 4))

                # CAPTCHA (reCAPTCHA/Turnstile) varsa otomatik çöz
                captcha_ok = self._handle_captcha(driver, site_key, site_cfg, url)
                if captcha_ok is False:
                    logger.info("  ⚠️  CAPTCHA çözülemedi, manuel kontrol gerekebilir.")

                # Form etkileşimi
                try:
                    from selenium.webdriver.common.by import By

                    # Kullanıcı adı alanını doldur (nickname/username) — bazı
                    # siteler formu boş gösterir, URL parametresi yetmez.
                    nickname = self._fill_username_field(driver, site_cfg, By)
                    if not nickname and username_param:
                        logger.info("  ⚠️  Kullanıcı adı alanı bulunamadı (URL parametresi denenir).")

                    # Privacy Policy checkbox
                    logger.info("  ☑️  Privacy Policy checkbox kontrol ediliyor...")
                    checkbox_selectors = site_cfg.get("checkbox_selectors") or [
                        "input[name='policy']", "input#policy",
                        "input[name='accept']", "input[type='checkbox']",
                        "//input[@type='checkbox']",
                        "//label[contains(text(), 'Privacy Policy')]//preceding::input[@type='checkbox'][1]"
                    ]
                    checkbox = None
                    for sel in checkbox_selectors:
                        try:
                            by = By.XPATH if sel.startswith("//") else By.CSS_SELECTOR
                            checkbox = driver.find_element(by, sel)
                            if checkbox:
                                break
                        except Exception:
                            continue

                    if checkbox:
                        if not checkbox.is_selected():
                            checkbox.click()
                            logger.info("  ✅ Privacy Policy checkbox işaretlendi")
                        else:
                            logger.info("  ✅ Privacy Policy checkbox zaten işaretli")
                        time.sleep(random.uniform(1, 2))
                    else:
                        logger.info("  ⚠️  Checkbox bulunamadı, devam ediliyor...")

                    # Vote butonu
                    logger.info("  🗳️  Vote butonu aranıyor...")
                    vote_selectors = site_cfg.get("vote_selectors") or [
                        "//button[contains(text(), 'Vote')]",
                        "input[type='submit'][value='Vote']",
                        "button[type='submit']", "input[type='submit']",
                        ".btn.btn-primary", "//input[@value='Vote']"
                    ]
                    vote_button = None
                    for sel in vote_selectors:
                        try:
                            by = By.XPATH if sel.startswith("//") else By.CSS_SELECTOR
                            vote_button = driver.find_element(by, sel)
                            if vote_button:
                                break
                        except Exception:
                            continue

                    if vote_button and vote_button.is_displayed():
                        vote_button.click()
                        logger.info("  ✅ Vote butonuna tıklandı!")
                        time.sleep(random.uniform(3, 5))

                        # Oydan sonra sayfa yönlenebilir; form aramayı bırak.
                        page_source  = driver.page_source
                        title        = driver.title
                        current_url  = driver.current_url
                        logger.info(f"  📊 Başlık: {title}")
                        logger.info(f"  🔗 URL: {current_url}")
                        self._save_screenshot(driver, site_key)

                        result = self._analyze(page_source, title, current_url, site_key)
                        if result["success"]:
                            logger.info(f"  ✅ [{site_key}] {result['message']}")
                            return result
                        elif result["already_voted"]:
                            logger.info(f"  ⏰ [{site_key}] {result['message']}")
                            return result
                        else:
                            logger.warning(f"  ⚠️ [{site_key}] {result['message']}")
                    else:
                        logger.info("  ⚠️  Vote butonu bulunamadı veya görünür değil")
                        # Oy verilmiş olabilir (already_voted) — sayfayı yine de analiz et.
                        page_source  = driver.page_source
                        title        = driver.title
                        current_url  = driver.current_url
                        logger.info(f"  📊 Başlık: {title}")
                        logger.info(f"  🔗 URL: {current_url}")
                        self._save_screenshot(driver, site_key)
                        result = self._analyze(page_source, title, current_url, site_key)
                        if result["already_voted"]:
                            logger.info(f"  ⏰ [{site_key}] {result['message']}")
                            return result

                except Exception as e:
                    logger.info(f"  ⚠️  Form etkileşimi hatası: {e}")

            except Exception as e:
                logger.error(f"  ❌ [{site_key}] Hata (Deneme {attempt}): {e}")
                if driver:
                    try:
                        ss = self.screenshots / f"{site_key}_error_{attempt}.png"
                        driver.save_screenshot(str(ss))
                    except Exception:
                        pass
            finally:
                if driver:
                    try:
                        driver.quit()
                    except Exception:
                        pass

            if attempt < self.retry_count:
                wait = self.retry_delay + random.uniform(0, 15)
                logger.info(f"  🔄 {wait:.0f} saniye sonra tekrar denenecek...")
                time.sleep(wait)

        return {"success": False, "already_voted": False,
                "message": f"Tüm {self.retry_count} deneme başarısız"}

    def _fill_username_field(self, driver, site_cfg, By) -> bool:
        """
        Formdaki kullanıcı adı alanını bulup doldurur.
        Site config'de username_input verilmişse öncelikli kullanılır.
        """
        selectors = site_cfg.get("username_input")
        if not selectors:
            selectors = ["input[name='nickname']", "input[name='username']"]
        if isinstance(selectors, str):
            selectors = [selectors]

        for sel in selectors:
            try:
                by = By.XPATH if sel.startswith("//") else By.CSS_SELECTOR
                el = driver.find_element(by, sel)
                if el and el.is_displayed():
                    el.click()
                    current = el.get_attribute("value") or ""
                    if current != self.username:
                        el.clear()
                        el.send_keys(self.username)
                        logger.info(f"  ✍️  Kullanıcı adı alanına '{self.username}' yazıldı")
                    else:
                        logger.info(f"  ✅ Kullanıcı adı zaten dolu: '{self.username}'")
                    return True
            except Exception:
                continue
        return False

    def _save_screenshot(self, driver, site_key: str):
        try:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            ss = self.screenshots / f"{site_key}_{ts}.png"
            driver.save_screenshot(str(ss))
            logger.info(f"  📸 Ekran görüntüsü: {ss}")
        except Exception as e:
            logger.info(f"  ⚠️  Ekran görüntüsü alınamadı: {e}")

    def _handle_captcha(self, driver, site_key, site_cfg, page_url) -> bool | None:
        """
        Sayfada reCAPTCHA/Turnstile varsa yapılandırılmış servis ile çözer.
        - captcha_service=none  → None (atlanır, uc_gui_click_captcha dener)
        - captcha_service=2captcha/anticaptcha → token enjekte edilir
        Dönen: True=tamam, False=hata, None=servis yok
        """
        if self.captcha_svc in ("none", "") or not self.captcha_key:
            return None

        try:
            from selenium.webdriver.common.by import By
            sitekey = self._find_sitekey(driver, site_cfg)
            if not sitekey:
                logger.info("  🧩 CAPTCHA widget'ı veya sitekey bulunamadı, atlanıyor.")
                return None
        except Exception as e:
            logger.info(f"  🧩 CAPTCHA tespiti başarısız: {e}")
            return None

        logger.info(f"  🧩 CAPTCHA tespit edildi (sitekey={sitekey}). {self.captcha_svc} ile çözülüyor...")
        token = self._solve_via_service(sitekey, page_url)
        if not token:
            return False

        if self._inject_token(driver, token):
            logger.info("  🧩 CAPTCHA token'ı sayfaya enjekte edildi.")
            return True
        return False

    def _find_sitekey(self, driver, site_cfg) -> str | None:
        sitekey = site_cfg.get("captcha_sitekey")
        if sitekey:
            return sitekey
        try:
            from selenium.webdriver.common.by import By
            for sel in (".g-recaptcha", "[data-sitekey]", "iframe[src*='recaptcha']"):
                try:
                    el = driver.find_element(By.CSS_SELECTOR, sel)
                    sk = el.get_attribute("data-sitekey")
                    if sk:
                        return sk
                except Exception:
                    continue
        except Exception:
            pass
        return None

    def _solve_via_service(self, sitekey: str, page_url: str) -> str | None:
        import requests
        if self.captcha_svc == "2captcha":
            return self._solve_2captcha(requests, sitekey, page_url)
        if self.captcha_svc == "anticaptcha":
            return self._solve_anticaptcha(requests, sitekey, page_url)
        return None

    def _solve_2captcha(self, requests, sitekey: str, page_url: str) -> str | None:
        try:
            resp = requests.post("https://2captcha.com/in.php", data={
                "key": self.captcha_key,
                "method": "userrecaptcha",
                "googlekey": sitekey,
                "pageurl": page_url,
                "json": 1,
            }, timeout=30)
            data = resp.json()
            if data.get("status") != 1:
                logger.error(f"  🧩 2captcha in.php hatası: {data}")
                return None
            captcha_id = data["request"]

            deadline = time.time() + self.captcha_timeout
            while time.time() < deadline:
                time.sleep(5)
                res = requests.get("https://2captcha.com/res.php", params={
                    "key": self.captcha_key, "action": "get", "id": captcha_id, "json": 1,
                }, timeout=30).json()
                if res.get("status") == 1:
                    return res["request"]
                if "CAPCHA_NOT_READY" not in str(res.get("request")):
                    logger.error(f"  🧩 2captcha res.php hatası: {res}")
                    return None
            logger.error("  🧩 2captcha zaman aşımı.")
        except Exception as e:
            logger.error(f"  🧩 2captcha hatası: {e}")
        return None

    def _solve_anticaptcha(self, requests, sitekey: str, page_url: str) -> str | None:
        try:
            create = requests.post("https://api.anti-captcha.com/createTask", json={
                "clientKey": self.captcha_key,
                "task": {
                    "type": "RecaptchaV2TaskPro",
                    "websiteURL": page_url,
                    "websiteKey": sitekey,
                },
            }, timeout=30).json()
            if "taskId" not in create:
                logger.error(f"  🧩 anticaptcha createTask hatası: {create}")
                return None
            task_id = create["taskId"]

            deadline = time.time() + self.captcha_timeout
            while time.time() < deadline:
                time.sleep(5)
                res = requests.post("https://api.anti-captcha.com/getTaskResult", json={
                    "clientKey": self.captcha_key, "taskId": task_id,
                }, timeout=30).json()
                if res.get("status") == "ready":
                    return res["solution"].get("gRecaptchaResponse")
                if res.get("status") != "processing":
                    logger.error(f"  🧩 anticaptcha sonuç hatası: {res}")
                    return None
            logger.error("  🧩 anticaptcha zaman aşımı.")
        except Exception as e:
            logger.error(f"  🧩 anticaptcha hatası: {e}")
        return None

    def _inject_token(self, driver, token: str) -> bool:
        """reCAPTCHA token'ını sayfaya enjekte edip formu doldurur."""
        try:
            driver.execute_script("""
                var ta = document.getElementById('g-recaptcha-response');
                if (ta) { ta.value = arguments[0]; ta.style.display = 'block'; }
                var frames = document.querySelectorAll('iframe[src*="recaptcha"]');
                frames.forEach(function(f) {
                    var w = f.contentWindow, d = w && w.document;
                    if (d && d.getElementById('recaptcha-token')) {
                        var t = d.getElementById('recaptcha-token');
                        t.value = arguments[0];
                        var cb = d.querySelector('#recaptcha-verify-button');
                        if (cb) cb.click();
                    }
                });
            """, token)
            time.sleep(2)
            return True
        except Exception as e:
            logger.info(f"  🧩 Token enjeksiyonu başarısız: {e}")
            return False

    def _analyze(self, source: str, title: str, url: str, site_key: str) -> dict:
        combined = (source + " " + title + " " + url).lower()

        if "challenge-platform" in combined or "cf-challenge" in combined:
            return {"success": False, "already_voted": False,
                    "message": "Cloudflare challenge sayfasında takılı kaldı"}

        success_kw  = ["thank", "success", "vote counted", "vote submitted",
                       "oy verildi", "teşekkür", "başarılı", "vote received",
                       "your vote has been", "vote confirmed"]
        already_kw  = ["already voted", "vote again", "24 hours", "once per day",
                       "zaten oy", "tekrar oy", "bugün oy", "already cast",
                       "you have already", "come back tomorrow"]
        captcha_kw  = ["captcha", "recaptcha", "turnstile",
                       "verify you are human", "i'm not a robot"]
        error_kw    = ["error", "failed", "invalid", "banned", "blocked",
                       "forbidden", "access denied", "too many requests"]

        if any(k in combined for k in success_kw):
            return {"success": True,  "already_voted": False, "message": "Oy başarıyla verildi!"}
        if any(k in combined for k in already_kw):
            return {"success": True,  "already_voted": True,  "message": "Bugün zaten oy verilmiş."}
        if any(k in combined for k in captcha_kw):
            return {"success": False, "already_voted": False, "message": "CAPTCHA engeli"}
        if any(k in combined for k in error_kw):
            return {"success": False, "already_voted": False, "message": "Sayfada hata mesajı"}

        return {"success": False, "already_voted": False,
                "message": f"Sonuç belirsiz - ekran görüntüsünü kontrol et"}


# ═══════════════════════════════════════════════════════════════════════════════
# YÖNTEM 2: NODRIVER (Async CDP)
# ═══════════════════════════════════════════════════════════════════════════════

class NodriverVoter:
    def __init__(self, cfg):
        self.username = cfg.get_vote_username()

    async def vote_async(self, site_key: str, site_cfg: dict) -> dict:
        import nodriver as uc
        url = site_cfg["url"]
        if site_cfg.get("username_param"):
            url = f"{url}?{site_cfg['username_param']}={self.username}"

        logger.info(f"🚀 [{site_key}] nodriver (CDP) başlatılıyor...")
        try:
            browser = await uc.start()
            page    = await browser.get(url)
            await asyncio.sleep(random.uniform(5, 8))
            content = await page.get_content()
            title   = await page.evaluate("document.title")
            logger.info(f"  📊 Başlık: {title}")
            combined = (content + " " + title).lower()
            if "thank" in combined or "success" in combined:
                result = {"success": True,  "already_voted": False, "message": "Oy verildi!"}
            elif "already" in combined or "24" in combined:
                result = {"success": True,  "already_voted": True,  "message": "Zaten oy verilmiş."}
            else:
                result = {"success": False, "already_voted": False, "message": "Sonuç belirsiz"}
            browser.stop()
            return result
        except Exception as e:
            logger.error(f"  ❌ [{site_key}] nodriver hatası: {e}")
            return {"success": False, "already_voted": False, "message": str(e)}

    def vote(self, site_key: str, site_cfg: dict) -> dict:
        return asyncio.run(self.vote_async(site_key, site_cfg))


# ═══════════════════════════════════════════════════════════════════════════════
# YÖNTEM 3: CLOUDSCRAPER
# ═══════════════════════════════════════════════════════════════════════════════

class CloudscraperVoter:
    def __init__(self, cfg):
        self.username = cfg.get_vote_username()
        self.proxy    = cfg.get("proxy")

    def vote(self, site_key: str, site_cfg: dict) -> dict:
        import cloudscraper
        url = site_cfg["url"]
        if site_cfg.get("username_param"):
            url = f"{url}?{site_cfg['username_param']}={self.username}"

        logger.info(f"🚀 [{site_key}] cloudscraper deneniyor...")
        try:
            scraper = cloudscraper.create_scraper(
                browser={"browser": "chrome", "platform": "windows", "desktop": True}
            )
            proxies  = {"http": self.proxy, "https": self.proxy} if self.proxy else None
            response = scraper.get(url, proxies=proxies, timeout=30)
            logger.info(f"  📊 Status: {response.status_code}")
            combined = response.text.lower()
            if response.status_code == 200:
                if "thank" in combined or "success" in combined:
                    return {"success": True,  "already_voted": False, "message": "Oy verildi (HTTP)"}
                elif "already" in combined:
                    return {"success": True,  "already_voted": True,  "message": "Zaten oy verilmiş"}
                elif "captcha" in combined:
                    return {"success": False, "already_voted": False, "message": "CAPTCHA engeli"}
                else:
                    return {"success": False, "already_voted": False, "message": "Belirsiz yanıt"}
            return {"success": False, "already_voted": False,
                    "message": f"HTTP {response.status_code}"}
        except Exception as e:
            logger.error(f"  ❌ [{site_key}] cloudscraper hatası: {e}")
            return {"success": False, "already_voted": False, "message": str(e)}


# ═══════════════════════════════════════════════════════════════════════════════
# VOTER FACTORY
# ═══════════════════════════════════════════════════════════════════════════════

def get_voter(cfg):
    """Mevcut kütüphanelere göre en iyi voter'ı seç."""
    try:
        from seleniumbase import Driver  # noqa
        logger.info("✅ SeleniumBase UC Mode kullanılacak")
        return SeleniumBaseVoter(cfg)
    except ImportError:
        pass

    try:
        import nodriver  # noqa
        logger.info("✅ nodriver (CDP) kullanılacak")
        return NodriverVoter(cfg)
    except ImportError:
        pass

    try:
        import cloudscraper  # noqa
        logger.info("✅ cloudscraper kullanılacak")
        return CloudscraperVoter(cfg)
    except ImportError:
        pass

    return None

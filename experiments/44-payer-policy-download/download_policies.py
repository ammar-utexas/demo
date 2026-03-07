#!/usr/bin/env python3
"""
Payer Policy Download Pipeline — Anti-VEGF Prior Authorization Rule Library

Downloads publicly available medical policy documents, coverage criteria,
formularies, and PA requirement lists from 6 major payers for anti-VEGF
intravitreal injection prior authorization.

Usage:
    python download_policies.py                    # Download all payers
    python download_policies.py --payer cms_medicare  # Download one payer
    python download_policies.py --payer uhc aetna     # Download specific payers
    python download_policies.py --list             # List configured payers
    python download_policies.py --verify           # Verify existing downloads
"""

import argparse
import hashlib
import json
import logging
import os
import re
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin, urlparse

import requests
import yaml
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("policy_downloader")

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class DownloadRecord:
    """Tracks a single downloaded file."""
    payer_id: str
    payer_name: str
    document_type: str
    filename: str
    source_url: str
    download_timestamp: str
    file_size_bytes: int
    sha256: str
    content_type: str
    description: str
    status: str  # "success", "failed", "skipped"
    error: Optional[str] = None


@dataclass
class Manifest:
    """Tracks all downloads across all payers."""
    generated_at: str = ""
    total_files: int = 0
    total_bytes: int = 0
    payers_attempted: list = field(default_factory=list)
    payers_succeeded: list = field(default_factory=list)
    downloads: list = field(default_factory=list)

    def add(self, record: DownloadRecord):
        self.downloads.append(asdict(record))
        if record.status == "success":
            self.total_files += 1
            self.total_bytes += record.file_size_bytes

    def save(self, path: Path):
        self.generated_at = datetime.now(timezone.utc).isoformat()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2)
        log.info(f"Manifest saved: {path} ({self.total_files} files, {self.total_bytes:,} bytes)")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_filename(name: str) -> str:
    """Sanitize a string for use as a filename."""
    name = re.sub(r'[<>:"/\\|?*]', '_', name)
    name = re.sub(r'\s+', '_', name)
    name = re.sub(r'_+', '_', name)
    return name[:200].strip('_')


def download_file(url: str, dest: Path, session: requests.Session,
                  delay: float = 2.0, timeout: int = 30) -> tuple[bool, str, int, str]:
    """
    Download a file from url to dest.
    Returns (success, content_type, file_size, error_message).
    """
    try:
        time.sleep(delay)
        resp = session.get(url, timeout=timeout, stream=True, allow_redirects=True)
        resp.raise_for_status()

        content_type = resp.headers.get("Content-Type", "unknown")
        dest.parent.mkdir(parents=True, exist_ok=True)

        with open(dest, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        file_size = dest.stat().st_size
        return True, content_type, file_size, ""

    except requests.exceptions.HTTPError as e:
        return False, "", 0, f"HTTP {e.response.status_code}: {e}"
    except requests.exceptions.ConnectionError as e:
        return False, "", 0, f"Connection error: {e}"
    except requests.exceptions.Timeout:
        return False, "", 0, f"Timeout after {timeout}s"
    except Exception as e:
        return False, "", 0, str(e)


def download_page(url: str, session: requests.Session,
                  delay: float = 2.0, timeout: int = 30) -> tuple[Optional[str], str]:
    """
    Download an HTML page and return (html_content, error_message).
    """
    try:
        time.sleep(delay)
        resp = session.get(url, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        return resp.text, ""
    except Exception as e:
        return None, str(e)


def find_pdf_links(html: str, base_url: str, keywords: list[str]) -> list[tuple[str, str]]:
    """
    Parse HTML and find PDF links matching keywords.
    Returns list of (url, link_text) tuples.
    """
    soup = BeautifulSoup(html, "html.parser")
    results = []

    for a in soup.find_all("a", href=True):
        href = a["href"]
        text = a.get_text(strip=True)
        combined = f"{href} {text}".lower()

        is_pdf = href.lower().endswith(".pdf") or "pdf" in combined
        matches_keyword = any(kw.lower() in combined for kw in keywords)

        if is_pdf and matches_keyword:
            full_url = urljoin(base_url, href)
            results.append((full_url, text))

    return results


def save_page_as_html(html: str, dest: Path, url: str):
    """Save an HTML page with a source header."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    with open(dest, "w", encoding="utf-8") as f:
        f.write(f"<!-- Source: {url} -->\n")
        f.write(f"<!-- Downloaded: {datetime.now(timezone.utc).isoformat()} -->\n\n")
        f.write(html)


# ---------------------------------------------------------------------------
# Payer-specific downloaders
# ---------------------------------------------------------------------------

def download_cms_medicare(config: dict, session: requests.Session,
                          manifest: Manifest, base_dir: Path, settings: dict):
    """Download CMS Medicare Traditional policy documents."""
    payer_id = "cms_medicare"
    payer_name = config["name"]
    payer_dir = base_dir / payer_id
    payer_dir.mkdir(parents=True, exist_ok=True)
    delay = settings["request_delay_seconds"]
    timeout = settings["timeout_seconds"]

    log.info(f"=== {payer_name} ===")

    # 1. Download LCD L33346 page
    log.info("Downloading LCD L33346 (Intravitreal Injections — Novitas)...")
    lcd_url = "https://www.cms.gov/medicare-coverage-database/view/lcd.aspx?lcdid=33346"
    html, err = download_page(lcd_url, session, delay, timeout)
    if html:
        dest = payer_dir / "LCD_L33346_intravitreal_injections.html"
        save_page_as_html(html, dest, lcd_url)
        record = DownloadRecord(
            payer_id=payer_id, payer_name=payer_name,
            document_type="lcd", filename=str(dest.relative_to(base_dir)),
            source_url=lcd_url, download_timestamp=datetime.now(timezone.utc).isoformat(),
            file_size_bytes=dest.stat().st_size, sha256=sha256_file(dest),
            content_type="text/html", description="LCD L33346 — Intravitreal Injections (Novitas, JH)",
            status="success"
        )
        manifest.add(record)

        # Find PDF links within the LCD page
        pdf_links = find_pdf_links(html, lcd_url, ["lcd", "intravitreal", "injection", "article"])
        for pdf_url, link_text in pdf_links[:5]:
            fname = safe_filename(link_text or urlparse(pdf_url).path.split("/")[-1]) + ".pdf"
            dest_pdf = payer_dir / fname
            log.info(f"  Downloading linked PDF: {fname}")
            ok, ct, size, err = download_file(pdf_url, dest_pdf, session, delay, timeout)
            manifest.add(DownloadRecord(
                payer_id=payer_id, payer_name=payer_name,
                document_type="lcd_attachment", filename=str(dest_pdf.relative_to(base_dir)),
                source_url=pdf_url, download_timestamp=datetime.now(timezone.utc).isoformat(),
                file_size_bytes=size, sha256=sha256_file(dest_pdf) if ok else "",
                content_type=ct, description=f"LCD attachment: {link_text}",
                status="success" if ok else "failed", error=err or None
            ))
    else:
        log.warning(f"  Failed to download LCD page: {err}")
        manifest.add(DownloadRecord(
            payer_id=payer_id, payer_name=payer_name,
            document_type="lcd", filename="",
            source_url=lcd_url, download_timestamp=datetime.now(timezone.utc).isoformat(),
            file_size_bytes=0, sha256="", content_type="",
            description="LCD L33346", status="failed", error=err
        ))

    # 2. Search CMS Medicare Coverage Database
    log.info("Searching CMS Medicare Coverage Database...")
    search_terms = ["intravitreal+injection", "anti-VEGF", "aflibercept", "bevacizumab"]
    for term in search_terms:
        search_url = f"https://www.cms.gov/medicare-coverage-database/search.aspx?q={term}"
        html, err = download_page(search_url, session, delay, timeout)
        if html:
            dest = payer_dir / f"search_results_{safe_filename(term)}.html"
            save_page_as_html(html, dest, search_url)
            manifest.add(DownloadRecord(
                payer_id=payer_id, payer_name=payer_name,
                document_type="search_results", filename=str(dest.relative_to(base_dir)),
                source_url=search_url, download_timestamp=datetime.now(timezone.utc).isoformat(),
                file_size_bytes=dest.stat().st_size, sha256=sha256_file(dest),
                content_type="text/html", description=f"Coverage DB search: {term}",
                status="success"
            ))

            # Download any PDFs found in search results
            pdf_links = find_pdf_links(html, search_url,
                                       ["lcd", "ncd", "intravitreal", "ophthalmology",
                                        "injection", "VEGF", "aflibercept", "bevacizumab"])
            for pdf_url, link_text in pdf_links[:3]:
                fname = safe_filename(link_text or urlparse(pdf_url).path.split("/")[-1])
                if not fname.endswith(".pdf"):
                    fname += ".pdf"
                dest_pdf = payer_dir / fname
                if not dest_pdf.exists():
                    log.info(f"  Downloading: {fname}")
                    ok, ct, size, err2 = download_file(pdf_url, dest_pdf, session, delay, timeout)
                    manifest.add(DownloadRecord(
                        payer_id=payer_id, payer_name=payer_name,
                        document_type="lcd_pdf", filename=str(dest_pdf.relative_to(base_dir)),
                        source_url=pdf_url, download_timestamp=datetime.now(timezone.utc).isoformat(),
                        file_size_bytes=size, sha256=sha256_file(dest_pdf) if ok else "",
                        content_type=ct, description=f"Search result PDF: {link_text}",
                        status="success" if ok else "failed", error=err2 or None
                    ))

    # 3. Download ASP pricing page
    log.info("Downloading ASP Drug Pricing page...")
    asp_url = "https://www.cms.gov/medicare/payment/part-b-drugs/average-sales-price"
    html, err = download_page(asp_url, session, delay, timeout)
    if html:
        dest = payer_dir / "asp_drug_pricing.html"
        save_page_as_html(html, dest, asp_url)
        manifest.add(DownloadRecord(
            payer_id=payer_id, payer_name=payer_name,
            document_type="asp_pricing", filename=str(dest.relative_to(base_dir)),
            source_url=asp_url, download_timestamp=datetime.now(timezone.utc).isoformat(),
            file_size_bytes=dest.stat().st_size, sha256=sha256_file(dest),
            content_type="text/html", description="Part B Drug ASP Pricing",
            status="success"
        ))

        # Find ASP pricing file downloads (Excel/CSV)
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.find_all("a", href=True):
            href = a["href"].lower()
            if any(ext in href for ext in [".xlsx", ".csv", ".zip"]) and "asp" in href:
                full_url = urljoin(asp_url, a["href"])
                fname = urlparse(full_url).path.split("/")[-1]
                dest_file = payer_dir / fname
                if not dest_file.exists():
                    log.info(f"  Downloading ASP file: {fname}")
                    ok, ct, size, err2 = download_file(full_url, dest_file, session, delay, timeout)
                    manifest.add(DownloadRecord(
                        payer_id=payer_id, payer_name=payer_name,
                        document_type="asp_data", filename=str(dest_file.relative_to(base_dir)),
                        source_url=full_url, download_timestamp=datetime.now(timezone.utc).isoformat(),
                        file_size_bytes=size, sha256=sha256_file(dest_file) if ok else "",
                        content_type=ct, description=f"ASP pricing data: {fname}",
                        status="success" if ok else "failed", error=err2 or None
                    ))


def download_payer_generic(payer_id: str, config: dict, session: requests.Session,
                           manifest: Manifest, base_dir: Path, settings: dict):
    """Generic downloader for MA payers — downloads source pages and linked PDFs."""
    payer_name = config["name"]
    payer_dir = base_dir / payer_id
    payer_dir.mkdir(parents=True, exist_ok=True)
    delay = settings["request_delay_seconds"]
    timeout = settings["timeout_seconds"]
    keywords = config.get("search_keywords", [])

    log.info(f"=== {payer_name} ===")

    for source in config.get("sources", []):
        doc_type = source["type"]
        url = source["url"]
        description = source["description"]

        log.info(f"  [{doc_type}] {description}")
        log.info(f"    URL: {url}")

        # Download the page
        html, err = download_page(url, session, delay, timeout)
        if not html:
            log.warning(f"    Failed: {err}")
            manifest.add(DownloadRecord(
                payer_id=payer_id, payer_name=payer_name,
                document_type=doc_type, filename="",
                source_url=url, download_timestamp=datetime.now(timezone.utc).isoformat(),
                file_size_bytes=0, sha256="", content_type="",
                description=description, status="failed", error=err
            ))
            continue

        # Save the HTML page
        fname = safe_filename(f"{doc_type}_{description}") + ".html"
        dest = payer_dir / fname
        save_page_as_html(html, dest, url)
        manifest.add(DownloadRecord(
            payer_id=payer_id, payer_name=payer_name,
            document_type=doc_type, filename=str(dest.relative_to(base_dir)),
            source_url=url, download_timestamp=datetime.now(timezone.utc).isoformat(),
            file_size_bytes=dest.stat().st_size, sha256=sha256_file(dest),
            content_type="text/html", description=description,
            status="success"
        ))

        # Find and download linked PDFs matching our keywords
        pdf_links = find_pdf_links(html, url, keywords + [
            "intravitreal", "anti-VEGF", "VEGF", "ophthalmology", "retina",
            "injection", "aflibercept", "bevacizumab", "ranibizumab",
            "faricimab", "prior auth", "formulary", "step therapy",
            "67028", "J0178", "J9035"
        ])

        if pdf_links:
            log.info(f"    Found {len(pdf_links)} relevant PDF links")
            for pdf_url, link_text in pdf_links[:10]:
                pdf_fname = safe_filename(link_text or urlparse(pdf_url).path.split("/")[-1])
                if not pdf_fname.endswith(".pdf"):
                    pdf_fname += ".pdf"
                dest_pdf = payer_dir / pdf_fname
                if dest_pdf.exists():
                    log.info(f"    Already exists: {pdf_fname}")
                    continue
                log.info(f"    Downloading: {pdf_fname}")
                ok, ct, size, err2 = download_file(pdf_url, dest_pdf, session, delay, timeout)
                manifest.add(DownloadRecord(
                    payer_id=payer_id, payer_name=payer_name,
                    document_type=f"{doc_type}_pdf", filename=str(dest_pdf.relative_to(base_dir)),
                    source_url=pdf_url, download_timestamp=datetime.now(timezone.utc).isoformat(),
                    file_size_bytes=size, sha256=sha256_file(dest_pdf) if ok else "",
                    content_type=ct, description=f"{description}: {link_text}",
                    status="success" if ok else "failed", error=err2 or None
                ))
        else:
            log.info("    No matching PDF links found on page (may need Playwright for JS-rendered content)")


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_downloads(base_dir: Path, manifest_path: Path):
    """Verify integrity of all downloaded files against the manifest."""
    if not manifest_path.exists():
        log.error(f"Manifest not found: {manifest_path}")
        return False

    with open(manifest_path) as f:
        manifest_data = json.load(f)

    downloads = manifest_data.get("downloads", [])
    total = len([d for d in downloads if d["status"] == "success"])
    passed = 0
    failed = 0

    log.info(f"Verifying {total} downloaded files...")

    for record in downloads:
        if record["status"] != "success":
            continue

        filepath = base_dir / record["filename"]
        if not filepath.exists():
            log.error(f"  MISSING: {record['filename']}")
            failed += 1
            continue

        actual_sha = sha256_file(filepath)
        if actual_sha != record["sha256"]:
            log.error(f"  CHECKSUM MISMATCH: {record['filename']}")
            log.error(f"    Expected: {record['sha256']}")
            log.error(f"    Actual:   {actual_sha}")
            failed += 1
            continue

        actual_size = filepath.stat().st_size
        if actual_size != record["file_size_bytes"]:
            log.warning(f"  SIZE MISMATCH: {record['filename']} ({actual_size} vs {record['file_size_bytes']})")

        passed += 1

    log.info(f"\nVerification: {passed}/{total} PASSED, {failed} FAILED")
    return failed == 0


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Download payer policy documents for anti-VEGF PA rules")
    parser.add_argument("--payer", nargs="*", help="Specific payer(s) to download (default: all)")
    parser.add_argument("--list", action="store_true", help="List configured payers and exit")
    parser.add_argument("--verify", action="store_true", help="Verify existing downloads against manifest")
    parser.add_argument("--config", default="config.yaml", help="Config file path (default: config.yaml)")
    args = parser.parse_args()

    # Load config
    config_path = Path(args.config)
    if not config_path.exists():
        log.error(f"Config file not found: {config_path}")
        sys.exit(1)

    with open(config_path) as f:
        config = yaml.safe_load(f)

    payers = config["payers"]
    settings = config["settings"]
    output = config["output"]
    base_dir = Path(output["base_dir"])
    manifest_path = Path(output["manifest_file"])

    # List mode
    if args.list:
        print("\nConfigured payers:")
        for pid, pconfig in payers.items():
            source_count = len(pconfig.get("sources", []))
            print(f"  {pid:20s}  {pconfig['name']:45s}  ({source_count} sources)")
        print(f"\nTotal: {len(payers)} payers")
        return

    # Verify mode
    if args.verify:
        ok = verify_downloads(base_dir, manifest_path)
        sys.exit(0 if ok else 1)

    # Download mode
    target_payers = args.payer if args.payer else list(payers.keys())
    invalid = [p for p in target_payers if p not in payers]
    if invalid:
        log.error(f"Unknown payer(s): {', '.join(invalid)}")
        log.error(f"Valid payers: {', '.join(payers.keys())}")
        sys.exit(1)

    # Create HTTP session
    session = requests.Session()
    session.headers.update({
        "User-Agent": settings["user_agent"],
        "Accept": "text/html,application/xhtml+xml,application/pdf,*/*",
        "Accept-Language": "en-US,en;q=0.9",
    })

    manifest = Manifest()
    manifest.payers_attempted = target_payers

    log.info(f"Starting policy download for {len(target_payers)} payer(s): {', '.join(target_payers)}")
    log.info(f"Output directory: {base_dir.resolve()}")
    print()

    for payer_id in target_payers:
        payer_config = payers[payer_id]
        try:
            if payer_id == "cms_medicare":
                download_cms_medicare(payer_config, session, manifest, base_dir, settings)
            else:
                download_payer_generic(payer_id, payer_config, session, manifest, base_dir, settings)
            manifest.payers_succeeded.append(payer_id)
        except Exception as e:
            log.error(f"Error downloading {payer_id}: {e}")
        print()

    # Save manifest
    manifest.save(manifest_path)

    # Summary
    print("\n" + "=" * 60)
    print("DOWNLOAD SUMMARY")
    print("=" * 60)
    success = [d for d in manifest.downloads if d["status"] == "success"]
    failed = [d for d in manifest.downloads if d["status"] == "failed"]
    print(f"  Payers attempted:  {len(manifest.payers_attempted)}")
    print(f"  Payers succeeded:  {len(manifest.payers_succeeded)}")
    print(f"  Files downloaded:  {len(success)}")
    print(f"  Files failed:      {len(failed)}")
    print(f"  Total size:        {manifest.total_bytes:,} bytes ({manifest.total_bytes / 1024 / 1024:.1f} MB)")
    print(f"  Manifest:          {manifest_path}")

    if failed:
        print(f"\n  Failed downloads:")
        for d in failed:
            print(f"    - [{d['payer_id']}] {d['description']}: {d.get('error', 'unknown')}")

    # Per-payer breakdown
    print(f"\n  Per-payer breakdown:")
    for pid in manifest.payers_attempted:
        payer_files = [d for d in success if d["payer_id"] == pid]
        payer_bytes = sum(d["file_size_bytes"] for d in payer_files)
        status = "OK" if pid in manifest.payers_succeeded else "FAILED"
        print(f"    {pid:20s}  {len(payer_files):3d} files  {payer_bytes:>10,} bytes  [{status}]")

    print()

    # Verify
    log.info("Running post-download verification...")
    verify_downloads(base_dir, manifest_path)


if __name__ == "__main__":
    main()

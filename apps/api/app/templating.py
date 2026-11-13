"""Jinja2 setup. Autoescape is ON for every template, so customer-supplied
text (addresses, notes, names) is always HTML-escaped by default."""

from __future__ import annotations

import hashlib
from pathlib import Path

from fastapi.templating import Jinja2Templates

from . import sms
from .config import STATIC_DIR

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"

templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
# Jinja2Templates enables autoescape for .html templates. Make that explicit
# so a future change cannot silently turn it off.
templates.env.autoescape = True


def asset_version() -> str:
    """Short content hash of the built front-end files.

    Appended to asset URLs as ?v=... so a deploy always busts the browser cache,
    even though /static/ is served with a long max-age.
    """
    digest = hashlib.sha256()  # noqa: S324 - a cache key, not a security control
    seen = False
    for rel in ("js/main.js", "styles.css", "vendor/htmx.min.js"):
        try:
            digest.update((STATIC_DIR / rel).read_bytes())
            seen = True
        except OSError:
            continue
    return digest.hexdigest()[:10] if seen else "dev"


templates.env.globals["asset_v"] = asset_version()
templates.env.globals["sms_live"] = sms.configured()[0]


def naira(value: int | float) -> str:
    return "₦" + f"{int(value):,}"


def local_time(iso: str) -> str:
    """'2026-11-10T14:30:00.000Z' -> '10 Nov 2026, 14:30' (UTC)."""
    from datetime import datetime

    try:
        dt = datetime.fromisoformat(str(iso).replace("Z", "+00:00"))
        return dt.strftime("%d %b %Y, %H:%M")
    except ValueError:
        return str(iso)


templates.env.filters["naira"] = naira
templates.env.filters["local_time"] = local_time

from . import order_status  # noqa: E402

templates.env.globals["progress_map"] = order_status.PROGRESS
templates.env.globals["cancellable"] = order_status.CUSTOMER_CAN_CANCEL_FROM

from markupsafe import Markup  # noqa: E402

from . import illustrations  # noqa: E402


def product_art(product: dict) -> Markup:
    return Markup(illustrations.svg_for(product["id"], product["name"]))  # noqa: S704


templates.env.filters["product_art"] = product_art

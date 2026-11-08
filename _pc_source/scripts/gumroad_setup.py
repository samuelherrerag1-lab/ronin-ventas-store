"""Configuración real de Gumroad: login único, 52 borradores con entrega y 5 publicados.

Uso (PowerShell, desde la raíz del repo):
  .\\.venv\\Scripts\\python.exe scripts\\gumroad_setup.py probe
  .\\.venv\\Scripts\\python.exe scripts\\gumroad_setup.py login --wait 3600
  .\\.venv\\Scripts\\python.exe scripts\\gumroad_setup.py token
  .\\.venv\\Scripts\\python.exe scripts\\gumroad_setup.py create [--only E01,B01] [--limit N]
  .\\.venv\\Scripts\\python.exe scripts\\gumroad_setup.py publish [--skus E01,B01,A01,K01,M06]
  .\\.venv\\Scripts\\python.exe scripts\\gumroad_setup.py apply-catalog
  .\\.venv\\Scripts\\python.exe scripts\\gumroad_setup.py verify
  .\\.venv\\Scripts\\python.exe scripts\\gumroad_setup.py sync      (token + crear + publicar + catálogo + verificar)
  .\\.venv\\Scripts\\python.exe scripts\\gumroad_setup.py report
"""

import argparse
import json
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

EXIT_OK, EXIT_LOGIN, EXIT_ERROR = 0, 2, 3


def _print(payload) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False, default=str))


def _token() -> str:
    from backend.services.connect_jobs import get_secret

    token = (os.environ.get("GUMROAD_ACCESS_TOKEN") or "").strip() or get_secret("gumroad", "access_token")
    return token or ""


def _client():
    from backend.services.gumroad_products import GumroadClient

    token = _token()
    if not token:
        raise SystemExit("Sin access token de Gumroad. Ejecuta antes: gumroad_setup.py login --wait 3600")
    return GumroadClient(token)


def _sync(state=None, catalog=None, delay=None):
    from backend.services import gumroad_catalog as cat
    from backend.services.gumroad_catalog_sync import GumroadSync

    state = state if state is not None else cat.load_state()
    catalog = catalog if catalog is not None else cat.load_catalog()
    engine = GumroadSync(_client(), state=state, catalog=catalog, delay=0.8 if delay is None else delay)
    return engine


def cmd_probe(_: argparse.Namespace) -> int:
    from backend.services.gumroad_token import probe_session

    result = probe_session()
    _print(result)
    return EXIT_OK if result.get("logged_in") else EXIT_LOGIN


def cmd_login(args: argparse.Namespace) -> int:
    from backend.services.gumroad_token import wait_for_login

    result = wait_for_login(timeout_sec=args.wait)
    _print(result)
    return EXIT_OK if result.get("status") == "connected" else EXIT_LOGIN


def cmd_token(args: argparse.Namespace) -> int:
    from backend.services.gumroad_token import acquire_token

    result = acquire_token(force=args.force)
    _print(result)
    return EXIT_OK if result.get("status") == "connected" else EXIT_LOGIN


def cmd_create(args: argparse.Namespace) -> int:
    from backend.services import gumroad_catalog as cat

    engine = _sync(delay=args.delay)
    account = _client().get_user()
    engine.state["account"] = {"email": account.get("email"), "user_id": account.get("user_id") or account.get("id"),
                               "name": account.get("name"), "validated_at": cat.utc_now()}
    cat.save_state(engine.state)
    only = [s.strip().upper() for s in args.only.split(",")] if args.only else None
    catalog = engine.catalog if not args.limit else engine.catalog[: len(engine.catalog)]
    if args.limit:
        engine.catalog = [s for s in catalog if s.get("format") != "lead_magnet"][: args.limit]
        engine.catalog += [s for s in catalog if s.get("format") == "lead_magnet"]
    results = engine.run(only=only)
    cat.save_state(engine.state)
    _print({"account": engine.state["account"], "results": results, "summary": cat.summarize(engine.state)})
    return EXIT_OK if not results["failed"] and not results["blocked_quota"] else EXIT_ERROR


def cmd_publish(args: argparse.Namespace) -> int:
    from backend.services import gumroad_catalog as cat

    engine = _sync()
    skus = [s.strip().upper() for s in args.skus.split(",")] if args.skus else None
    result = engine.publish_flagships(skus)
    _print({"publish": result, "summary": cat.summarize(engine.state)})
    return EXIT_OK if not result["failed"] else EXIT_ERROR


def cmd_apply(args: argparse.Namespace) -> int:
    from backend.services import gumroad_catalog as cat

    state = cat.load_state()
    result = cat.apply_urls_to_catalog(state, published_only=not args.all)
    _print({"catalog": result, "summary": cat.summarize(state)})
    return EXIT_OK if result["applied"] else EXIT_ERROR


def cmd_verify(_: argparse.Namespace) -> int:
    from backend.services import gumroad_catalog as cat

    state = cat.load_state()
    checks = cat.verify_stored_urls(state)
    published = [c for c in checks if c.get("published")]
    ok = [c for c in published if c.get("ok")]
    _print({"published": len(published), "verified_ok": len(ok), "checks": checks})
    return EXIT_OK if published and ok else EXIT_ERROR


def cmd_retry_blocked(args: argparse.Namespace) -> int:
    """Reintenta SOLO los SKUs bloqueados por el cupo diario (10/día)."""
    from backend.services import gumroad_catalog as cat

    state = cat.load_state()
    blocked = [sku for sku, entry in (state.get("products") or {}).items() if entry.get("status") == "blocked_quota"]
    if not blocked:
        _print({"retry": "nada bloqueado por cupo", "blocked": []})
        return EXIT_OK
    engine = _sync(state=state)
    targets = blocked[: args.max] if args.max else blocked
    results = engine.run(only=targets)
    cat.save_state(engine.state)
    _print({"attempted": targets, "results": results, "summary": cat.summarize(engine.state)})
    return EXIT_OK if not results["failed"] else EXIT_ERROR


def cmd_report(args: argparse.Namespace) -> int:
    from backend.services import gumroad_catalog as cat

    state = cat.load_state()
    summary = cat.summarize(state)
    catalog = cat.load_catalog()
    with_url = sum(1 for sku in catalog if sku.get("gumroad_url"))
    readiness = {}
    try:
        import urllib.request

        with urllib.request.urlopen("http://127.0.0.1:8765/api/publish/readiness", timeout=15) as response:
            readiness = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        readiness = {"error": f"{type(exc).__name__}: {exc}"}
    _print(
        {
            "summary": summary,
            "catalog_with_gumroad_url": with_url,
            "readiness_counts": readiness.get("counts"),
            "readiness_blockers": readiness.get("blockers"),
            "products": state.get("products"),
        }
    )
    return EXIT_OK


def cmd_sync(args: argparse.Namespace) -> int:
    from backend.services import gumroad_catalog as cat
    from backend.services.gumroad_token import acquire_token

    token_result = acquire_token()
    if token_result.get("status") != "connected":
        _print({"token": token_result})
        return EXIT_LOGIN
    engine = _sync()
    account = _client().get_user()
    engine.state["account"] = {"email": account.get("email"), "user_id": account.get("user_id") or account.get("id"),
                               "name": account.get("name"), "validated_at": cat.utc_now()}
    cat.save_state(engine.state)
    create_result = engine.run()
    publish_result = engine.publish_flagships()
    applied = cat.apply_urls_to_catalog(engine.state)
    checks = cat.verify_stored_urls(engine.state)
    _print(
        {
            "token": token_result,
            "account": engine.state["account"],
            "create": create_result,
            "publish": publish_result,
            "catalog": applied,
            "summary": cat.summarize(engine.state),
            "verified": [c for c in checks if c.get("published")],
        }
    )
    return EXIT_OK if not create_result["failed"] and not publish_result["failed"] else EXIT_ERROR


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Alta real de productos en Gumroad")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("probe").set_defaults(func=cmd_probe)

    p_login = sub.add_parser("login")
    p_login.add_argument("--wait", type=int, default=3600, help="Segundos de espera al login humano")
    p_login.set_defaults(func=cmd_login)

    p_token = sub.add_parser("token")
    p_token.add_argument("--force", action="store_true")
    p_token.set_defaults(func=cmd_token)

    p_create = sub.add_parser("create")
    p_create.add_argument("--only", default="")
    p_create.add_argument("--limit", type=int, default=0)
    p_create.add_argument("--delay", type=float, default=0.8)
    p_create.set_defaults(func=cmd_create)

    p_publish = sub.add_parser("publish")
    p_publish.add_argument("--skus", default="")
    p_publish.set_defaults(func=cmd_publish)

    p_apply = sub.add_parser("apply-catalog")
    p_apply.add_argument("--all", action="store_true", help="Incluye borradores (aún no comprables)")
    p_apply.set_defaults(func=cmd_apply)
    sub.add_parser("verify").set_defaults(func=cmd_verify)
    p_retry = sub.add_parser("retry-blocked")
    p_retry.add_argument("--max", type=int, default=0, help="Máximo de SKUs a intentar (0 = todos)")
    p_retry.set_defaults(func=cmd_retry_blocked)
    sub.add_parser("report").set_defaults(func=cmd_report)
    sub.add_parser("sync").set_defaults(func=cmd_sync)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

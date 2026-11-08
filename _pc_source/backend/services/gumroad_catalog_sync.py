"""Alta idempotente de los 52 productos de pago en Gumroad (borradores + flagship).

Flujo real por SKU:
1. Busca el producto por `custom_permalink` (slug) o por el id guardado; nunca duplica.
2. Sube el entregable HTML (`/v2/files/*`) y lo adjunta como `files[][url]`.
3. Convierte la portada webp a JPEG y la adjunta con `direct_uploads` + `/covers`.
4. Crea en modo borrador (`draft=true`). Solo los flagship se publican con `/enable`.
5. Guarda el mapa {sku: product_id, gumroad_url, published, file_attached} en
   `data/gumroad_products.json` y puede persistir las URLs en `data/catalog.json`.
"""

import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

from backend.services import gumroad_catalog as cat
from backend.services.gumroad_media import cover_to_jpeg_bytes, slug_of
from backend.services.gumroad_products import GumroadClient, GumroadError

PUBLISH_LIST = list(cat.FLAGSHIP_SKUS)


class GumroadSync:
    def __init__(
        self,
        client: GumroadClient,
        state: Optional[Dict[str, Any]] = None,
        catalog: Optional[List[Dict[str, Any]]] = None,
        delay: float = 0.8,
        image_converter: Callable[[Path], bytes] = cover_to_jpeg_bytes,
    ):
        self.client = client
        self.state = state if state is not None else cat.load_state()
        self.catalog = catalog if catalog is not None else cat.load_catalog()
        self.delay = delay
        self.image_converter = image_converter
        self.existing_by_slug: Dict[str, Dict[str, Any]] = {}
        self.log: List[Dict[str, Any]] = []

    def _note(self, message: str, **extra: Any) -> None:
        self.log.append({"at": cat.utc_now(), "msg": message, **extra})

    def _sleep(self) -> None:
        if self.delay > 0:
            time.sleep(self.delay)

    # -- descubrimiento -----------------------------------------------------
    def load_existing(self) -> Dict[str, Dict[str, Any]]:
        for product in self.client.list_products():
            slug = slug_of(product)
            if slug:
                self.existing_by_slug[slug] = product
        self._note("productos existentes en la cuenta", count=len(self.existing_by_slug))
        return self.existing_by_slug

    def _find_product(self, sku: Dict[str, Any], entry: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        product_id = entry.get("product_id")
        if product_id:
            try:
                product = self.client.get_product(product_id)
                if product.get("id"):
                    return product
            except GumroadError:
                pass
        found = self.existing_by_slug.get(sku["slug"])
        if not found:
            return None
        try:
            return self.client.get_product(found["id"])
        except GumroadError:
            return found

    def _attach_file(self, product_id: str, path: Path) -> str:
        file_url = self.client.upload_file(path)
        self.client.update_product(product_id, {"files[][url]": file_url})
        return file_url

    def _attach_cover(self, product_id: str, sku_id: str) -> bool:
        path = cat.cover_path(sku_id)
        if not path.is_file():
            return False
        data = self.image_converter(path)
        signed_id = self.client.direct_upload_image(data, f"{sku_id}_cover.jpg", "image/jpeg")
        self.client.add_cover(product_id, signed_id)
        return True

    def ensure_draft(self, sku: Dict[str, Any]) -> Dict[str, Any]:
        """Crea (o completa) el producto en borrador. Devuelve la entrada de estado."""
        sku_id = sku["sku_id"]
        entry = cat.product_entry(self.state, sku_id)
        entry.setdefault("sku_id", sku_id)
        entry.setdefault("slug", sku["slug"])
        entry["last_attempt_at"] = cat.utc_now()

        path = cat.deliverable_path(sku_id, sku["slug"])
        if not path.is_file():
            entry.update({"status": "missing_file", "error": f"Falta {path.name} en data/deliverables"})
            self._note("entregable ausente, no se crea producto", sku=sku_id)
            return entry

        product = self._find_product(sku, entry)
        created = False
        warnings: List[str] = []
        if product:
            entry["status"] = "existing"
            entry["product_id"] = product.get("id")
        else:
            # Subir archivo ANTES de crear: si falla, no queda un producto sin entrega.
            file_url = self.client.upload_file(path)
            self._sleep()
            payload = {
                "name": sku["title"],
                "native_type": "digital",
                "description": cat.build_description(sku),
                "custom_permalink": sku["slug"],
                "price": str(cat.price_cents(sku["price_usd"])),
                "price_currency_type": "usd",
                "draft": "true",
                "published": "false",
                "tags[]": cat.tags_for(sku),
                "files[][url]": file_url,
            }
            result = self.client.create_product(payload)
            product = result["product"]
            created = True
            if result.get("warning"):
                warnings.append(str(result["warning"]))
            entry.update({"status": "created", "file_url": file_url})
            self._note("producto creado en borrador", sku=sku_id, product_id=product.get("id"))
            self._sleep()

        product_id = product.get("id") or entry.get("product_id")
        if not product_id:
            entry.update({"status": "failed", "error": "Gumroad no devolvió id de producto"})
            return entry

        files = product.get("files") if isinstance(product.get("files"), list) else None
        if files is None:
            try:
                product = self.client.get_product(product_id)
                files = product.get("files") or []
            except GumroadError:
                files = []
        if not files and not entry.get("file_url"):
            try:
                entry["file_url"] = self._attach_file(product_id, path)
                self._note("archivo adjuntado a producto existente", sku=sku_id)
                files = [{"name": path.name}]
            except GumroadError as exc:
                warnings.append(f"archivo: {exc}")
        entry["file_attached"] = bool(files)
        entry["file_name"] = path.name
        entry["file_size"] = path.stat().st_size

        covers = product.get("covers") if isinstance(product.get("covers"), list) else []
        if not covers and not entry.get("cover_attached"):
            try:
                entry["cover_attached"] = self._attach_cover(product_id, sku_id)
                self._note("portada adjuntada", sku=sku_id)
            except GumroadError as exc:
                warnings.append(f"portada: {exc}")
        else:
            entry["cover_attached"] = bool(covers) or bool(entry.get("cover_attached"))

        entry.update({"product_id": product_id, "gumroad_url": product.get("short_url") or entry.get("gumroad_url") or "",
                      "price_cents": cat.price_cents(sku["price_usd"]), "published": bool(product.get("published")),
                      "created_now": created, "warnings": warnings})
        if created:
            entry["created_at"] = cat.utc_now()
        if not entry.get("gumroad_url"):
            entry.update({"status": "failed", "error": "Producto sin short_url; no hay URL de checkout verificable"})
        elif entry["status"] not in ("failed",):
            entry["status"] = "draft_ready" if entry["file_attached"] else "draft_no_file"
            if entry["status"] == "draft_ready":
                entry.pop("error", None)
        cat.save_state(self.state)
        return entry

    def publish(self, sku_id: str) -> Dict[str, Any]:
        entry = cat.product_entry(self.state, sku_id)
        if not entry.get("file_attached"):
            entry.setdefault("errors", []).append("no se publica sin archivo adjunto")
            cat.save_state(self.state)
            return entry
        if entry.get("published"):
            return entry
        product = self.client.enable_product(entry["product_id"])
        entry["published"] = bool(product.get("published"))
        if entry["published"]:
            entry["published_at"] = cat.utc_now()
            entry["status"] = "published"
            self._note("producto publicado", sku=sku_id, url=entry.get("gumroad_url"))
        else:
            entry.setdefault("errors", []).append("Gumroad no confirmó published=true al habilitar")
        cat.save_state(self.state)
        return entry

    def run(self, only: Optional[List[str]] = None) -> Dict[str, Any]:
        self.existing_by_slug = {}
        self.load_existing()
        targets = [sku for sku in cat.paid_skus(self.catalog) if not only or sku["sku_id"] in only]
        results: Dict[str, Any] = {"created": [], "existing": [], "failed": [], "missing_file": [], "blocked_quota": []}
        quota_hit = False
        for sku in targets:
            if quota_hit:
                entry = cat.product_entry(self.state, sku["sku_id"])
                entry.update({"status": "blocked_quota", "error": "Límite diario de Gumroad: 10 productos/día hasta que la cuenta sea compliant"})
                results["blocked_quota"].append(sku["sku_id"])
                continue
            try:
                entry = self.ensure_draft(sku)
            except GumroadError as exc:
                entry = cat.product_entry(self.state, sku["sku_id"])
                entry.update({"status": "failed", "error": str(exc), "last_attempt_at": cat.utc_now()})
                cat.save_state(self.state)
            if "create 10 products per day" in str(entry.get("error") or ""):
                quota_hit = True
                entry["status"] = "blocked_quota"
                self._note("cupo diario de creación agotado", sku=sku["sku_id"])
                cat.save_state(self.state)
                results["blocked_quota"].append(sku["sku_id"])
                continue
            status = entry.get("status")
            bucket = {"created": "created", "existing": "existing", "missing_file": "missing_file",
                      "draft_ready": "created" if entry.get("created_now") else "existing"}.get(status or "", "failed")
            results[bucket].append(sku["sku_id"])
        return results

    def publish_flagships(self, skus: Optional[List[str]] = None) -> Dict[str, Any]:
        out: Dict[str, Any] = {"published": [], "skipped": [], "failed": []}
        for sku_id in skus or PUBLISH_LIST:
            entry = (self.state.get("products") or {}).get(sku_id) or {}
            if not entry.get("product_id"):
                out["skipped"].append(sku_id)
                continue
            try:
                entry = self.publish(sku_id)
            except GumroadError as exc:
                entry.setdefault("errors", []).append(str(exc))
                out["failed"].append(sku_id)
                cat.save_state(self.state)
                continue
            (out["published"] if entry.get("published") else out["failed"]).append(sku_id)
        return out

import json
import re
from pathlib import Path

DATA_FILE = Path("data/products.json")
INDEX_FILE = Path("index.html")


def price_label(price):
    return "$" + f"{int(price):,}".replace(",", ".")


def main():
    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    products = data.get("products", [])

    for product in products:
        product["priceLabel"] = price_label(product.get("price", 0))

    index = INDEX_FILE.read_text(encoding="utf-8")
    generated = "const products = " + json.dumps(products, ensure_ascii=False, indent=2) + ";"

    # Repara la versión que insertaba un <script> dentro del <script> principal.
    malformed = re.compile(
        r"<script>\s*window\.LUNA_PRODUCTS\s*=\s*\[.*?\];\s*</script>\s*const products\s*=\s*window\.LUNA_PRODUCTS\s*\|\|\s*\[\];",
        re.DOTALL,
    )
    if malformed.search(index):
        updated = malformed.sub(generated, index, count=1)
    else:
        generated_window = re.compile(r"window\.LUNA_PRODUCTS\s*=\s*\[.*?\];\s*", re.DOTALL)
        if generated_window.search(index):
            updated = generated_window.sub("", index, count=1)
            legacy_window = re.compile(r"const products\s*=\s*window\.LUNA_PRODUCTS\s*\|\|\s*\[\];")
            updated, count = legacy_window.subn(generated, updated, count=1)
            if count != 1:
                raise SystemExit("No se encontró la declaración de productos para reemplazar")
        else:
            legacy = re.compile(r"const products\s*=\s*\[.*?\n\];", re.DOTALL)
            updated, count = legacy.subn(generated, index, count=1)
            if count != 1:
                raise SystemExit("No se encontró el bloque de productos en index.html")

    if updated != index:
        INDEX_FILE.write_text(updated, encoding="utf-8")
        print(f"Catálogo sincronizado: {len(products)} productos.")
    else:
        print("El catálogo ya está sincronizado.")


if __name__ == "__main__":
    main()

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
    generated = "window.LUNA_PRODUCTS = " + json.dumps(products, ensure_ascii=False, indent=2) + ";"
    pattern = re.compile(r"window\.LUNA_PRODUCTS\s*=\s*\[.*?\];", re.DOTALL)
    if pattern.search(index):
        updated = pattern.sub(generated, index, count=1)
    else:
        legacy = re.compile(r"const products\s*=\s*\[.*?\n\];", re.DOTALL)
        updated, count = legacy.subn("const products = window.LUNA_PRODUCTS || [];", index, count=1)
        if count != 1:
            raise SystemExit("No se encontró el bloque de productos en index.html")
        declaration = "const products = window.LUNA_PRODUCTS || [];"
        pos = updated.find(declaration)
        script = "<script>\n" + generated + "\n</script>\n"
        updated = updated[:pos] + script + updated[pos:]

    if updated != index:
        INDEX_FILE.write_text(updated, encoding="utf-8")
        print(f"Catálogo sincronizado: {len(products)} productos.")
    else:
        print("El catálogo ya está sincronizado.")


if __name__ == "__main__":
    main()

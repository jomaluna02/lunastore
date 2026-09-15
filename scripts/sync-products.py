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
    pattern = r"const products\s*=\s*\[.*?\n\];"
    updated, count = re.subn(pattern, generated, index, count=1, flags=re.DOTALL)

    if count != 1:
        raise SystemExit("No se encontró exactamente el bloque const products=[...] en index.html")

    if updated == index:
        print("El catálogo ya está sincronizado.")
        return

    INDEX_FILE.write_text(updated, encoding="utf-8")
    print(f"Catálogo sincronizado: {len(products)} productos.")


if __name__ == "__main__":
    main()

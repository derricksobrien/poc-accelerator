from ingestion.scraper import CatalogScraper

s = CatalogScraper('catalog.json')
c = s.load_catalog()
print("Available Accelerators in Catalog:")
for a in c.solution_accelerators:
    print(f"  - {a.name} ({a.id})")

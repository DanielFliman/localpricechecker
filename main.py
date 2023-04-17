import csv
import re
from pprint import pprint
from pyzipcode import ZipCodeDatabase
from BrickseekScraper import BrickseekScraper

def extract_skus_from_urls(urls):
    skus = []
    for url in urls:
        sku_match = re.search(r'/(\d{9})', url)
        if sku_match:
            skus.append(sku_match.group(1))
    return skus

if __name__ == '__main__':
    zcdb = ZipCodeDatabase()

    decode_option = input("Do you want to decode URLs to extract SKUs? (y/n): ").strip().lower()
    skus = []
    if decode_option == 'y':
        print("Enter the URLs (one per line). Press Enter on a blank line when finished:")
        while True:
            url = input()
            if not url:
                break
            skus.extend(extract_skus_from_urls([url]))
    else:
        skus_input = input("Enter SKU (for multiple SKUs, separate by spaces): ")
        skus = [sku.strip() for sku in skus_input.split(' ')]

    Stores = ["Walmart", "Lowes", "Home-Depot", "All-Stores"]
    while True:
        try:
            StoreNo = int(input("Select Store:\r\n\t" + "\r\n\t".join([store+" ["+str(index+1)+"]"  for index, store in enumerate(Stores)]) + "\r\nEnter selection #: "))
            store = Stores[StoreNo-1]
            break
        except:
            print("Invalid option! Please enter a number from list above.\r\n\r\n")

    input_zip = input("Enter source zip code: ")
    input_radius = input("Enter radius from entered zip code (in miles): ")
    sleep_duration = 0

    # Use the ZipCodeDatabase to generate a list of zip codes within the requested radius of a source zip code.
    in_radius = [z.zip for z in zcdb.get_zipcodes_around_radius(input_zip, input_radius)]
    zipcodes = in_radius

    for sku in skus:
        print(f"Processing SKU: {sku}")

        # Create a copy of the zipcodes list
        zipcodes_copy = zipcodes.copy()

        if store == "All-Stores":
            stores_to_check = Stores[:-1]
        else:
            stores_to_check = [store]

        for store_to_check in stores_to_check:
            result = BrickseekScraper.GetBrickseekInventory(store_to_check, sku, zipcodes_copy, sleep_duration)
            print(f"\r\nResults for {store_to_check}:\r\n")
            pprint(result)

            if result:
                # Find the store with the cheapest price
                cheapest_store = min(result, key=lambda x: float(x['Price'].replace('$', '').replace(',', '')))
                print("\r\nCheapest Price and Location:")
                print("Price: {}".format(cheapest_store['Price']))
                print("Location: {} ({})".format(cheapest_store['Store-name'], cheapest_store['Store-address']))
                print("")

                # Save results as csv
                keys = result[0].keys()
                with open(store_to_check + '-' + sku + '.csv', 'w', newline='') as output_file:
                    dict_writer = csv.DictWriter(output_file, keys)
                    dict_writer.writeheader()
                    dict_writer.writerows(result)
            else:
                print("No results found for SKU: {}".format(sku))

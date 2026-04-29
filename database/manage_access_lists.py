import argparse

from database.db_manager import DBManager


def main():
    parser = argparse.ArgumentParser(description="SmartCampus erisim listesi yonetimi")
    parser.add_argument("action", choices=["add", "remove"], help="Yapilacak islem")
    parser.add_argument("list_type", choices=["authorized", "blacklist"], help="Liste tipi")
    parser.add_argument("plate", help="Plaka numarasi")
    args = parser.parse_args()

    db = DBManager()
    if args.action == "add":
        ok = db.plaka_listesine_ekle(args.plate, args.list_type)
    else:
        ok = db.plaka_listesinden_cikar(args.plate, args.list_type)

    if ok:
        print("✅ Islem basarili")
    else:
        print("❌ Islem basarisiz")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test script to verify BIP report template generation works correctly.
"""

import datetime
from pathlib import Path

from src.html_generator import HTMLGenerator
from src.models import ContentItem


def test_bip_report_generation():
    """Test BIP report template generation with extensive sample data."""

    # Create sample content items with realistic BIP data
    # Mix of articles and file attachments across multiple dates and categories
    items = [
        # ============ Data: 2025-10-01 ============
        # Zawiadomienia o sesjach - 2 items
        ContentItem(
            url="https://bip.nadarzyn.pl/88,zawiadomienia-o-zwolaniu-sesji?tresc=20001",
            main_title="Zawiadomienia o zwołaniu Sesji Rady Gminy",
            title="Zawiadomienie o zwołaniu XX Sesji Rady Gminy Nadarzyn",
            description="Zawiadomienie o zwołaniu XX Sesji Rady Gminy Nadarzyn na dzień 15 października 2025 roku",
            created_at=datetime.date(2025, 10, 1),
            published_at=datetime.date(2025, 10, 1),
            last_modified_at=datetime.date(2025, 10, 1),
        ),
        ContentItem(
            url="https://bip.nadarzyn.pl/88,zawiadomienia-o-zwolaniu-sesji?tresc=20002",
            main_title="Zawiadomienia o zwołaniu Sesji Rady Gminy",
            title="zawiadomienie_o_sesji_XX.pdf",
            description="Załącznik nr 1 do zawiadomienia o zwołaniu XX Sesji - porządek obrad",
            attachment_url="https://bip.nadarzyn.pl/download/zawiadomienie_XX.pdf",
            created_at=datetime.date(2025, 10, 1),
            published_at=datetime.date(2025, 10, 1),
            last_modified_at=datetime.date(2025, 10, 1),
        ),
        # Przetargi - 3 items
        ContentItem(
            url="https://bip.nadarzyn.pl/przetargi/2025-10-001",
            main_title="Przetargi i zamówienia publiczne",
            title="Przetarg na budowę placu zabaw w Kajetanach",
            description="Ogłoszenie o przetargu nieograniczonym na wykonanie placu zabaw przy ul. Sportowej w "
            "Kajetanach",
            created_at=datetime.date(2025, 10, 1),
            published_at=datetime.date(2025, 10, 1),
            last_modified_at=datetime.date(2025, 10, 1),
        ),
        ContentItem(
            url="https://bip.nadarzyn.pl/przetargi/2025-10-002",
            main_title="Przetargi i zamówienia publiczne",
            title="SIWZ - Budowa placu zabaw",
            description="Specyfikacja Istotnych Warunków Zamówienia dla przetargu na budowę placu zabaw",
            attachment_url="https://bip.nadarzyn.pl/download/SIWZ_plac_zabaw.pdf",
            created_at=datetime.date(2025, 10, 1),
            published_at=datetime.date(2025, 10, 1),
            last_modified_at=datetime.date(2025, 10, 1),
        ),
        ContentItem(
            url="https://bip.nadarzyn.pl/przetargi/2025-10-003",
            main_title="Przetargi i zamówienia publiczne",
            title="Wyniki konsultacji społecznych projektu placu zabaw",
            description="Raport z konsultacji społecznych dotyczących projektu placu zabaw w Kajetanach",
            attachment_url="https://bip.nadarzyn.pl/download/konsultacje_plac.pdf",
            created_at=datetime.date(2025, 10, 1),
            published_at=datetime.date(2025, 10, 1),
            last_modified_at=datetime.date(2025, 10, 1),
        ),
        # ============ Data: 2025-09-28 ============
        # Uchwały - 2 items
        ContentItem(
            url="https://bip.nadarzyn.pl/uchwal/XIX-401-2025",
            main_title="Uchwały Rady Gminy Nadarzyn podjęte na XIX Sesji",
            title="Uchwała Nr XIX.401.2025 w sprawie budżetu gminy",
            description="Uchwała budżetowa Gminy Nadarzyn na rok 2026 - projekt budżetu i założenia",
            created_at=datetime.date(2025, 9, 28),
            published_at=datetime.date(2025, 9, 28),
            last_modified_at=datetime.date(2025, 9, 28),
        ),
        ContentItem(
            url="https://bip.nadarzyn.pl/uchwal/XIX-402-2025",
            main_title="Uchwały Rady Gminy Nadarzyn podjęte na XIX Sesji",
            title="uchwala_XIX_401_2025.pdf",
            description="Uchwała Nr XIX.401.2025 w sprawie uchwalenia budżetu gminy Nadarzyn na rok 2026",
            attachment_url="https://bip.nadarzyn.pl/download/uchwala_XIX_401.pdf",
            created_at=datetime.date(2025, 9, 28),
            published_at=datetime.date(2025, 9, 28),
            last_modified_at=datetime.date(2025, 9, 28),
        ),
        # Komunikaty - 1 item
        ContentItem(
            url="https://bip.nadarzyn.pl/komunikaty/2025-09-28-01",
            main_title="Komunikaty Wójta Gminy",
            title="Informacja o godzinach pracy Urzędu w okresie jesiennym",
            description="Wójt Gminy Nadarzyn informuje o zmianie godzin pracy Urzędu Gminy w okresie od 1 października"
            " do 31 marca",
            created_at=datetime.date(2025, 9, 28),
            published_at=datetime.date(2025, 9, 28),
            last_modified_at=datetime.date(2025, 9, 28),
        ),
        # ============ Data: 2025-09-20 ============
        # Protokoły - 2 items
        ContentItem(
            url="https://bip.nadarzyn.pl/protokoly/2025/XVIII",
            main_title="Protokoły z Sesji Rady Gminy Nadarzyn",
            title="Protokół z XVIII Sesji Rady Gminy Nadarzyn",
            description="Protokół z XVIII Sesji Rady Gminy Nadarzyn odbytej w dniu 18 września 2025 roku",
            created_at=datetime.date(2025, 9, 20),
            published_at=datetime.date(2025, 9, 20),
            last_modified_at=datetime.date(2025, 9, 20),
        ),
        ContentItem(
            url="https://bip.nadarzyn.pl/protokoly/2025/XVIII-pdf",
            main_title="Protokoły z Sesji Rady Gminy Nadarzyn",
            title="protokol_XVIII_sesji.pdf",
            description="Załącznik - pełna treść protokołu z XVIII Sesji w formacie PDF",
            attachment_url="https://bip.nadarzyn.pl/download/protokol_XVIII.pdf",
            created_at=datetime.date(2025, 9, 20),
            published_at=datetime.date(2025, 9, 20),
            last_modified_at=datetime.date(2025, 9, 20),
        ),
        # ============ Data: 2025-09-15 ============
        # Ogłoszenia - 3 items
        ContentItem(
            url="https://bip.nadarzyn.pl/ogloszenia/2025-09-15-01",
            main_title="Ogłoszenia i obwieszczenia",
            title="Obwieszczenie o wszczęciu postępowania administracyjnego",
            description="Wójt Gminy Nadarzyn obwieszcza o wszczęciu postępowania w sprawie wydania decyzji o "
            "środowiskowych uwarunkowaniach",
            created_at=datetime.date(2025, 9, 15),
            published_at=datetime.date(2025, 9, 15),
            last_modified_at=datetime.date(2025, 9, 15),
        ),
        ContentItem(
            url="https://bip.nadarzyn.pl/ogloszenia/2025-09-15-02",
            main_title="Ogłoszenia i obwieszczenia",
            title="Wykaz nieruchomości przeznaczonych do sprzedaży",
            description="Wykaz nieruchomości stanowiących własność Gminy Nadarzyn przeznaczonych do sprzedaży w trybie"
            " przetargu",
            created_at=datetime.date(2025, 9, 15),
            published_at=datetime.date(2025, 9, 15),
            last_modified_at=datetime.date(2025, 9, 15),
        ),
        ContentItem(
            url="https://bip.nadarzyn.pl/ogloszenia/2025-09-15-03",
            main_title="Ogłoszenia i obwieszczenia",
            title="wykaz_nieruchomosci_IX_2025.pdf",
            description="Szczegółowy wykaz nieruchomości z opisem i cenami wywoławczymi",
            attachment_url="https://bip.nadarzyn.pl/download/wykaz_nieruchomosci_IX_2025.pdf",
            created_at=datetime.date(2025, 9, 15),
            published_at=datetime.date(2025, 9, 15),
            last_modified_at=datetime.date(2025, 9, 15),
        ),
        # ============ Data: 2025-09-01 ============
        # Zarządzenia Wójta - 2 items
        ContentItem(
            url="https://bip.nadarzyn.pl/zarzadzenia/2025/089",
            main_title="Zarządzenia Wójta Gminy Nadarzyn",
            title="Zarządzenie Nr 89/2025 w sprawie organizacji pracy Urzędu",
            description="Zarządzenie Wójta Gminy Nadarzyn w sprawie wprowadzenia zmian w regulaminie organizacyjnym "
            "Urzędu Gminy",
            created_at=datetime.date(2025, 9, 1),
            published_at=datetime.date(2025, 9, 1),
            last_modified_at=datetime.date(2025, 9, 1),
        ),
        ContentItem(
            url="https://bip.nadarzyn.pl/zarzadzenia/2025/090",
            main_title="Zarządzenia Wójta Gminy Nadarzyn",
            title="Zarządzenie Nr 90/2025 w sprawie powołania komisji rekrutacyjnej",
            description="Zarządzenie w sprawie powołania komisji rekrutacyjnej do naboru na wolne stanowisko w Urzędzie"
            " Gminy",
            created_at=datetime.date(2025, 9, 1),
            published_at=datetime.date(2025, 9, 1),
            last_modified_at=datetime.date(2025, 9, 1),
        ),
        # Konkursy i nabory - 1 item
        ContentItem(
            url="https://bip.nadarzyn.pl/nabory/2025-09-01",
            main_title="Konkursy i nabory",
            title="Nabór na stanowisko informatyka w Urzędzie Gminy",
            description="Wójt Gminy Nadarzyn ogłasza nabór na wolne stanowisko urzędnicze - informatyk systemowy",
            created_at=datetime.date(2025, 9, 1),
            published_at=datetime.date(2025, 9, 1),
            last_modified_at=datetime.date(2025, 9, 1),
        ),
        # ============ Data: 2025-08-26 ============
        # Organizacje pozarządowe - 1 item
        ContentItem(
            url="https://bip.nadarzyn.pl/34,organizacje?nobreakup#akapit_562",
            main_title="Lista organizacji pozarządowych",
            title='Stowarzyszenie na Rzecz Dzieci i Osób Niepełnosprawnych „SZLAKIEM TĘCZY"',
            description=(
                "Aktualizacja danych kontaktowych: Stowarzyszenie na Rzecz Dzieci i Osób Niepełnosprawnych „SZLAKIEM"
                ' TĘCZY" '
                "Kajetany, ul. Karola Łoniewskiego 11, 05-830 Nadarzyn tel. 793 003 898 "
                "e-mail: szlakiemteczy@nadarzyn.pl"
            ),
            created_at=datetime.date(2025, 8, 26),
            published_at=datetime.date(2025, 8, 26),
            last_modified_at=datetime.date(2025, 8, 26),
        ),
        # Obwieszczenia - 2 items
        ContentItem(
            url="https://bip.nadarzyn.pl/73,komunikaty-i-ogloszenia?nobreakup#plik_21282",
            main_title="Obwieszczenia Wójta Gminy Nadarzyn",
            title="Obwieszczenie Wójta Gminy Nadarzyn z dnia 26.08.2025",
            description=(
                "Wójt Gminy Nadarzyn obwieszcza o decyzji środowiskowej dla przedsięwzięcia polegającego "
                "na budowie drogi gminnej w miejscowości Kajetany"
            ),
            created_at=datetime.date(2025, 8, 20),
            published_at=datetime.date(2025, 8, 20),
            last_modified_at=datetime.date(2025, 8, 26),
        ),
        ContentItem(
            url="https://bip.nadarzyn.pl/73,komunikaty-i-ogloszenia?nobreakup#plik_21283",
            main_title="Obwieszczenia Wójta Gminy Nadarzyn",
            title="obwieszczenie_26_08_2025.pdf",
            description="Pełna treść obwieszczenia wraz z załącznikami mapowymi",
            attachment_url="https://bip.nadarzyn.pl/download/obwieszczenie_26_08_2025.pdf",
            created_at=datetime.date(2025, 8, 20),
            published_at=datetime.date(2025, 8, 20),
            last_modified_at=datetime.date(2025, 8, 26),
        ),
        # ============ Data: 2025-08-15 ============
        # Plan zagospodarowania - 2 items
        ContentItem(
            url="https://bip.nadarzyn.pl/mpzp/kajetany-2025",
            main_title="Miejscowy Plan Zagospodarowania Przestrzennego",
            title="Projekt MPZP dla obszaru Kajetany-Zachód",
            description="Projekt miejscowego planu zagospodarowania przestrzennego dla rejonu Kajetany-Zachód wyłożony"
            " do publicznego wglądu",
            created_at=datetime.date(2025, 8, 15),
            published_at=datetime.date(2025, 8, 15),
            last_modified_at=datetime.date(2025, 8, 15),
        ),
        ContentItem(
            url="https://bip.nadarzyn.pl/mpzp/kajetany-2025-pdf",
            main_title="Miejscowy Plan Zagospodarowania Przestrzennego",
            title="mpzp_kajetany_zachod_projekt.pdf",
            description="Projekt planu wraz z rysunkiem planu i prognozą oddziaływania na środowisko",
            attachment_url="https://bip.nadarzyn.pl/download/mpzp_kajetany_zachod.pdf",
            created_at=datetime.date(2025, 8, 15),
            published_at=datetime.date(2025, 8, 15),
            last_modified_at=datetime.date(2025, 8, 15),
        ),
        # ============ Data: 2025-08-01 ============
        # Budżet i finanse - 3 items
        ContentItem(
            url="https://bip.nadarzyn.pl/finanse/sprawozdanie-II-kw-2025",
            main_title="Budżet i finanse gminy",
            title="Sprawozdanie z wykonania budżetu za II kwartał 2025",
            description="Informacja o przebiegu wykonania budżetu Gminy Nadarzyn za okres od 1 stycznia do 30 czerwca "
            "2025 roku",
            created_at=datetime.date(2025, 8, 1),
            published_at=datetime.date(2025, 8, 1),
            last_modified_at=datetime.date(2025, 8, 1),
        ),
        ContentItem(
            url="https://bip.nadarzyn.pl/finanse/sprawozdanie-II-kw-2025-pdf",
            main_title="Budżet i finanse gminy",
            title="sprawozdanie_budzet_II_kw_2025.pdf",
            description="Szczegółowe sprawozdanie finansowe z tabelami i wykresami",
            attachment_url="https://bip.nadarzyn.pl/download/sprawozdanie_II_kw_2025.pdf",
            created_at=datetime.date(2025, 8, 1),
            published_at=datetime.date(2025, 8, 1),
            last_modified_at=datetime.date(2025, 8, 1),
        ),
        ContentItem(
            url="https://bip.nadarzyn.pl/finanse/analiza-II-kw-2025",
            main_title="Budżet i finanse gminy",
            title="Analiza wykonania budżetu za I półrocze 2025",
            description="Prezentacja analityczna wykonania budżetu Gminy Nadarzyn w podziale na dochody, wydatki i "
            "zadania inwestycyjne",
            created_at=datetime.date(2025, 8, 1),
            published_at=datetime.date(2025, 8, 1),
            last_modified_at=datetime.date(2025, 8, 1),
        ),
        # ============ Data: 2025-07-15 ============
        # Konsultacje społeczne - 2 items
        ContentItem(
            url="https://bip.nadarzyn.pl/konsultacje/2025-program-wspolpracy-ngo",
            main_title="Konsultacje społeczne",
            title="Konsultacje programu współpracy z organizacjami pozarządowymi na 2026 rok",
            description="Zaproszenie do konsultacji projektu programu współpracy Gminy Nadarzyn z organizacjami "
            "pozarządowymi",
            created_at=datetime.date(2025, 7, 15),
            published_at=datetime.date(2025, 7, 15),
            last_modified_at=datetime.date(2025, 7, 15),
        ),
        ContentItem(
            url="https://bip.nadarzyn.pl/konsultacje/2025-program-wspolpracy-ngo-formularz",
            main_title="Konsultacje społeczne",
            title="formularz_konsultacji_ngo_2026.pdf",
            description="Formularz zgłaszania uwag do projektu programu współpracy z NGO",
            attachment_url="https://bip.nadarzyn.pl/download/formularz_konsultacji_ngo.pdf",
            created_at=datetime.date(2025, 7, 15),
            published_at=datetime.date(2025, 7, 15),
            last_modified_at=datetime.date(2025, 7, 15),
        ),
        # ============ Data: 2025-07-01 ============
        # Inwestycje gminne - 3 items
        ContentItem(
            url="https://bip.nadarzyn.pl/inwestycje/2025/droga-kajetany",
            main_title="Inwestycje gminne",
            title="Rozpoczęcie budowy drogi gminnej w Kajetanach",
            description="Informacja o rozpoczęciu robót budowlanych związanych z budową nowej drogi gminnej łączącej "
            "ul. Sportową z ul. Łoniewskiego",
            created_at=datetime.date(2025, 7, 1),
            published_at=datetime.date(2025, 7, 1),
            last_modified_at=datetime.date(2025, 7, 1),
        ),
        ContentItem(
            url="https://bip.nadarzyn.pl/inwestycje/2025/oswietlenie",
            main_title="Inwestycje gminne",
            title="Modernizacja oświetlenia ulicznego - etap III",
            description="Ogłoszenie o modernizacji oświetlenia ulicznego w miejscowościach Kajetany, Rusiec i Młochów -"
            " wymiana na LED",
            created_at=datetime.date(2025, 7, 1),
            published_at=datetime.date(2025, 7, 1),
            last_modified_at=datetime.date(2025, 7, 1),
        ),
        ContentItem(
            url="https://bip.nadarzyn.pl/inwestycje/2025/oswietlenie-harmonogram",
            main_title="Inwestycje gminne",
            title="harmonogram_modernizacji_oswietlenia.pdf",
            description="Szczegółowy harmonogram prac modernizacyjnych z podziałem na ulice",
            attachment_url="https://bip.nadarzyn.pl/download/harmonogram_oswietlenie.pdf",
            created_at=datetime.date(2025, 7, 1),
            published_at=datetime.date(2025, 7, 1),
            last_modified_at=datetime.date(2025, 7, 1),
        ),
    ]

    print("=== BIP Report Template Generation Test ===\n")

    # Generate BIP report
    generator = HTMLGenerator()
    output_path = generator.generate_report(
        items=items,
        output_path="tests/test_bip_report_output.html",
        template_name="bip_report.html",
        custom_context={
            "page_title": "Test BIP Nadarzyn - Raport",
            "subtitle": "Raport testowy wygenerowany automatycznie",
            "new_items_count": 3,
            "last_updated": "22 września 2025",
        },
    )

    print("✅ BIP report generated successfully!")
    print(f"📄 Report contains {len(items)} items")
    print(f"💾 Saved to: {Path(output_path).absolute()}")

    # Show basic statistics
    grouped_count = {}
    date_count = {}
    entry_types = {"new": 0, "update": 0}

    for item in items:
        # Group by main_title
        main_title = item.main_title or "Różne"
        grouped_count[main_title] = grouped_count.get(main_title, 0) + 1

        # Group by date
        item_date = item.last_modified_at or item.created_at or item.published_at
        if item_date:
            date_str = item_date.strftime("%Y-%m-%d")
            date_count[date_str] = date_count.get(date_str, 0) + 1

        # Count entry types
        entry_type = generator._get_entry_type(item)
        entry_types[entry_type] = entry_types.get(entry_type, 0) + 1

    print("\n📊 Content breakdown by category:")
    for title, count in sorted(grouped_count.items()):
        print(f"  • {title}: {count} item(s)")

    print("\n📅 Content breakdown by date:")
    for date_str, count in sorted(date_count.items(), reverse=True):
        print(f"  • {date_str}: {count} item(s)")

    print("\n🏷️  Entry types:")
    print(f"  • Nowe wpisy: {entry_types.get('new', 0)}")
    print(f"  • Aktualizacje: {entry_types.get('update', 0)}")

    print("\n🌐 Open in browser:")
    print(f"  file://{Path(output_path).absolute()}")

    return output_path


if __name__ == "__main__":
    test_bip_report_generation()

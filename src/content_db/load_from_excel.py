# load_from_excel.py
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from models import (
    Base, Member, MemberNameHistory, MembershipPeriod, Activity, Location,
    ActivityLocation, Role, MediaType, MediaItem, MediaAppearance, MediaMention
)

# Helper function (add this near the top of the file)
def safe_to_date(val):
    """Convert possible Excel date (serial or string) → datetime.date or None"""
    if pd.isna(val):
        return None

    # Try pandas conversion (handles Excel serial numbers)
    try:
        dt = pd.to_datetime(val, unit='D', origin='1899-12-30', errors='coerce')
        if pd.notna(dt):
            return dt.date()          # return date object (SQLite likes this)
    except:
        pass

    # Fallback: try parsing as string (if someone wrote e.g. "15-3-1965")
    try:
        return pd.to_datetime(val, dayfirst=True, errors='coerce').date()
    except:
        return None

def normalize_id(s: str) -> str:
    """Create clean, consistent primary keys from titles/names"""
    return "" if pd.isna(s) else s.strip().replace(" - ", " ").replace("  ", " ")


def load_excel_to_db(excel_path="/home/mark/Downloads/kna_database.xlsx", db_path="data/kna_archive.db"):
    engine = create_engine(f"sqlite:///{db_path}")
    # Make sure tables exist
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # 1. Media types (simple lookup)
        df_types = pd.read_excel(excel_path, sheet_name="Type_Media")
        for _, row in df_types.iterrows():
            t = MediaType(
                type_code=row["type_media"].strip().lower(),
                description=row["type_media"].strip()
            )
            session.merge(t)

        # 2. Members (basic – name history can be added later)
        df_members = pd.read_excel(excel_path, sheet_name="Leden")

        for _, row in df_members.iterrows():
            birth_date_raw = row["Geboortedatum"]

            # Convert Excel serial date → datetime, and NaT → None
            if pd.isna(birth_date_raw):
                birth_dt = None
            else:
                try:
                    # Excel dates are days since 1899-12-30
                    birth_dt = pd.to_datetime(birth_date_raw, unit="D", origin="1899-12-30", errors="coerce")
                    if pd.isna(birth_dt):
                        birth_dt = None
                except:
                    birth_dt = None

            m = Member(
                id_member=str(row["id_lid"]).strip(),
                current_first_name=str(row["Voornaam"]).strip(),
                current_last_name=str(row["Achternaam"]).strip(),
                birth_date=birth_dt,           # now safe: datetime or None
                gdpr_permission=1 if str(row["gdpr_permission"]).lower() in ["true", "1", "yes"] else 0,
                notes=None
            )
            session.merge(m)

        # 3. Activities (performances + events)
        df_uitv = pd.read_excel(excel_path, sheet_name="Uitvoering")
        df_uitv["start_date"] = df_uitv["datum_van"].apply(safe_to_date)
        df_uitv["end_date"]   = df_uitv["datum_tot"].apply(safe_to_date)
        for _, row in df_uitv.iterrows():
            act_id = normalize_id(row["uitvoering"])

            a = Activity(
                id_activity=act_id,
                title=str(row["titel"]).strip() if pd.notna(row["titel"]) else "",
                type=str(row["type"]).strip() if pd.notna(row["type"]) else "Uitvoering",
                start_date=safe_to_date(row["datum_van"]),
                end_date=safe_to_date(row["datum_tot"]),
                year=int(row["jaar"]) if pd.notna(row["jaar"]) and str(row["jaar"]).strip().isdigit() else None,
                author=str(row["auteur"]).strip() if pd.notna(row["auteur"]) else None,
                director=None,
                folder=str(row["folder"]).strip() if pd.notna(row["folder"]) else None,
                description=str(row.get("Notitie", "")) if pd.notna(row.get("Notitie")) else None
            )
            session.merge(a)

        # 4. Locations (from Uitvoering Locaties + some from Uitvoering)
        locations_seen = set()
        df_loc = pd.read_excel(excel_path, sheet_name="Uitvoering Locaties", dtype=str)
        for _, row in df_loc.iterrows():
            loc_name = str(row["locatie"]).strip()
            if loc_name and loc_name not in locations_seen:
                loc = Location(id_location=loc_name, name=loc_name)
                session.merge(loc)
                locations_seen.add(loc_name)

            act_id = normalize_id(row["ref_uitvoering"])
            session.merge(ActivityLocation(id_activity=act_id, id_location=loc_name))

        # 5. Roles
        df_rollen = pd.read_excel(excel_path, sheet_name="Rollen")
        for _, row in df_rollen.iterrows():
            act_id = normalize_id(row["ref_uitvoering"])
            member_id = str(row["id_lid"]).strip()
            r = Role(
                id_activity=act_id,
                id_member=member_id,
                role_name=str(row["rol"]).strip() if pd.notna(row["rol"]) else None,
                character_name=str(row["rol_bijnaam"]).strip() if pd.notna(row["rol_bijnaam"]) else None,
                role_type=None,
                notes=None
            )
            session.add(r)  # we allow duplicates for now – later deduplicate if needed

        # Commit everything
        session.commit()
        print("Initial load completed.")

        # Quick stats
        print("Counts:")
        for cls, name in [
            (Member, "members"),
            (Activity, "activities"),
            (Role, "roles"),
            (MediaType, "media types"),
            (Location, "locations")
        ]:
            count = session.execute(text(f"SELECT COUNT(*) FROM {cls.__tablename__}")).scalar()
            print(f"  {name}: {count}")


if __name__ == "__main__":
    load_excel_to_db()
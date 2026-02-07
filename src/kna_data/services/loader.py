"""
KNA Data Loader

ETL operations for loading Excel data into KNA content database.
Works exclusively with the KNA content database (not users).
"""

import os
from pathlib import Path
import pandas as pd
from PIL import Image

from ..config import BaseConfig
from logging_kna import logger


class KnaDataLoader:
    """
    ETL service for loading Excel data into KNA database.

    Works exclusively with KNA content database.
    Does NOT touch users database.
    """

    def __init__(self, config: BaseConfig):
        """Initialize with configuration"""
        self.config = config
        self.engine = config.get_kna_engine()
        self.dir_resources = config.DIR_RESOURCES

        logger.info(f"KnaDataLoader initialized: {config.SQLITE_KNA_PATH}")

    def load_from_excel(self, file_path: str) -> dict:
        """
        Load all data from Excel into KNA content database.

        Args:
            file_path: Path to Excel file

        Returns:
            dict: Load statistics (rows per table)
        """
        logger.info(f"Starting data load from {file_path}")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Excel file not found: {file_path}")

        # Load tables in dependency order
        stats = {"lid": self._load_leden(file_path)}
        stats["uitvoering"] = self._load_uitvoeringen(file_path)
        stats["media_type"] = self._load_media_types(file_path)
        stats["file"], stats["file_leden"] = self._load_files(file_path)
        stats["rol"] = self._load_rollen(file_path)
        stats["thumbnails"] = self._generate_thumbnails()

        logger.info("Data load completed successfully")
        return stats

    def _load_leden(self, file_path: str) -> int:
        """Load members table with Dutch name sorting"""
        logger.info("Loading leden...")

        df = pd.read_excel(file_path, sheet_name="Leden")

        # Add sortable name field
        df["achternaam_sort"] = df["Achternaam"].apply(self._calculate_sort_name)

        # Write to database
        df.to_sql("lid", con=self.engine, if_exists="replace", index=False)
        logger.info(f"Loaded {len(df)} members")

        return len(df)

    @staticmethod
    def _calculate_sort_name(achternaam: str) -> str:
        """Calculate sortable name handling Dutch prefixes"""
        if pd.isnull(achternaam):
            return "zzzzzzzz"

        prefixes = ["van der", "van den", "van de", "van", "de", "v.d."]
        achternaam_lower = achternaam.lower()

        for prefix in prefixes:
            if achternaam_lower.startswith(prefix + " "):
                rest = achternaam[len(prefix) + 1 :]
                return f"{rest}, {prefix}"

        return achternaam

    def _load_uitvoeringen(self, file_path: str) -> int:
        """Load performances with director enrichment"""
        logger.info("Loading uitvoeringen...")

        df = pd.read_excel(file_path, sheet_name="Uitvoering")
        df.rename(columns={"uitvoering": "ref_uitvoering"}, inplace=True)

        # Get director from roles
        df_rollen = pd.read_excel(file_path, sheet_name="Rollen")
        df_regie = (
            df_rollen[df_rollen["rol"] == "Regie"]
            .groupby("ref_uitvoering")["id_lid"]
            .first()
            .reset_index()
        )
        df_regie.columns = ["ref_uitvoering", "regie"]

        # Merge and add media count placeholder
        df = df.merge(df_regie, how="left", on="ref_uitvoering")
        df["qty_media"] = 0

        df.to_sql("uitvoering", con=self.engine, if_exists="replace", index=False)
        logger.info(f"Loaded {len(df)} performances")

        return len(df)

    def _load_media_types(self, file_path: str) -> int:
        """Load media types lookup table"""
        logger.info("Loading media types...")

        df = pd.read_excel(file_path, sheet_name="Type_Media")
        df.to_sql("media_type", con=self.engine, if_exists="replace", index=False)
        logger.info(f"Loaded {len(df)} media types")

        return len(df)

    def _load_files(self, file_path: str) -> tuple[int, int]:
        """
        Load files and file-member associations.

        Returns:
            tuple: (file_count, file_leden_count)
        """
        logger.info("Loading files...")

        # Get folder mapping
        df_uitvoering = pd.read_excel(file_path, sheet_name="Uitvoering")
        df_uitvoering.rename(columns={"uitvoering": "ref_uitvoering"}, inplace=True)
        folder_map = df_uitvoering[["ref_uitvoering", "folder"]]

        # Load and enrich files
        df_files = pd.read_excel(file_path, sheet_name="Bestand")
        df_files = df_files.merge(folder_map, how="left", on="ref_uitvoering")
        df_files["file_ext"] = df_files["bestand"].str.split(".").str[-1].str.lower()

        # Create member associations (unpivot lid_* columns)
        df_leden = df_files.melt(
            id_vars=["ref_uitvoering", "bestand", "type_media", "file_ext", "folder"],
            var_name="vlnr",
            value_name="lid",
        ).dropna(subset=["lid"])

        df_leden.to_sql("file_leden", con=self.engine, if_exists="replace", index=False)
        logger.info(f"Loaded {len(df_leden)} file-member associations")

        # Save files table (without lid_* columns)
        df_files = df_files.drop(
            columns=[c for c in df_files.columns if c.startswith("lid_")]
        )
        df_files.to_sql("file", con=self.engine, if_exists="replace", index=False)
        logger.info(f"Loaded {len(df_files)} files")

        # Update performance media counts
        self._update_media_counts(df_files)

        return len(df_files), len(df_leden)

    def _update_media_counts(self, df_files: pd.DataFrame):
        """Update qty_media in uitvoering table"""
        counts = df_files.groupby("ref_uitvoering").size()

        with self.engine.begin() as conn:
            for ref, qty in counts.items():
                conn.execute(
                    f"UPDATE uitvoering SET qty_media = {qty} "
                    f"WHERE ref_uitvoering = '{ref}'"
                )

    def _load_rollen(self, file_path: str) -> int:
        """Load roles with media counts"""
        logger.info("Loading rollen...")

        df_rollen = pd.read_excel(file_path, sheet_name="Rollen")

        # Get media counts per member-performance
        df_file_leden = pd.read_sql("SELECT * FROM file_leden", con=self.engine)
        media_counts = (
            df_file_leden.groupby(["ref_uitvoering", "lid"])
            .size()
            .reset_index(name="qty_media")
        )
        media_counts.rename(columns={"lid": "id_lid"}, inplace=True)

        # Merge and save
        df_rollen = df_rollen.merge(
            media_counts, how="left", on=["ref_uitvoering", "id_lid"]
        )
        df_rollen["qty_media"] = df_rollen["qty_media"].fillna(0).astype(int)

        df_rollen.to_sql("rol", con=self.engine, if_exists="replace", index=False)
        logger.info(f"Loaded {len(df_rollen)} roles")

        return len(df_rollen)

    def _generate_thumbnails(self) -> int:
        """Generate thumbnail images for photos"""
        logger.info("Generating thumbnails...")

        count = 0

        for root, dirs, files in os.walk(self.dir_resources):
            if "thumbnails" in root:
                continue  # Skip thumbnail directories

            thumb_dir = Path(root) / "thumbnails"
            thumb_dir.mkdir(exist_ok=True)

            for file in files:
                if not file.lower().endswith((".png", ".jpg", ".jpeg")):
                    continue

                src = Path(root) / file
                dst = thumb_dir / file

                if dst.exists():
                    continue  # Skip existing thumbnails

                try:
                    with Image.open(src) as img:
                        img.thumbnail((300, 300), Image.LANCZOS)
                        img.save(dst, quality=95)
                        count += 1
                except Exception as e:
                    logger.error(f"Failed thumbnail for {file}: {e}")

        logger.info(f"Generated {count} new thumbnails")
        return count

    def validate_excel(self, file_path: str) -> dict:
        """
        Validate Excel file structure.

        Args:
            file_path: Path to Excel file

        Returns:
            dict: Validation results with 'valid', 'errors', 'warnings', 'info'
        """
        logger.info(f"Validating: {file_path}")

        result = {"valid": True, "errors": [], "warnings": [], "info": {}}

        if not os.path.exists(file_path):
            result["valid"] = False
            result["errors"].append(f"File not found: {file_path}")
            return result

        try:
            required_sheets = ["Leden", "Uitvoering", "Rollen", "Bestand", "Type_Media"]
            xl = pd.ExcelFile(file_path)

            # Check sheets exist
            for sheet in required_sheets:
                if sheet not in xl.sheet_names:
                    result["valid"] = False
                    result["errors"].append(f"Missing sheet: {sheet}")
                else:
                    df = pd.read_excel(file_path, sheet_name=sheet)
                    result["info"][sheet] = len(df)

            # Check required columns
            if "Leden" in xl.sheet_names:
                df_leden = pd.read_excel(file_path, sheet_name="Leden")
                required_cols = ["id_lid", "Voornaam", "Achternaam"]
                for col in required_cols:
                    if col not in df_leden.columns:
                        result["valid"] = False
                        result["errors"].append(f"Leden missing column: {col}")

        except Exception as e:
            result["valid"] = False
            result["errors"].append(f"Error reading file: {str(e)}")

        return result

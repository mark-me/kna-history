"""
KNA Data Loader

ETL (Extract-Transform-Load) operations for loading data from Excel into the database.
"""
import os
from pathlib import Path
from typing import Optional

import pandas as pd
from PIL import Image

from .config import Config
from logging_kna import logger


class KnaDataLoader:
    """
    Handles loading data from Excel files into the KNA database.
    
    Performs ETL operations:
    - Extract: Read from Excel
    - Transform: Clean, enrich, and structure data
    - Load: Write to database tables
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the data loader.
        
        Args:
            config: Configuration object. If None, uses default production config.
        """
        self.config = config or Config.for_production()
        self.engine = self.config.get_engine()
        self.dir_resources = self.config.dir_resources
        
    def load_from_excel(self, file_path: str) -> dict:
        """
        Load all data from Excel file into database.
        
        Args:
            file_path: Path to Excel file with KNA data
            
        Returns:
            Dictionary with load statistics (rows loaded per table)
        """
        logger.info(f"Starting data load from {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        stats = {}
        
        # Load each table
        stats["lid"] = self._load_leden(file_path)
        stats["uitvoering"] = self._load_uitvoeringen(file_path)
        stats["media_type"] = self._load_media_types(file_path)
        stats["file"], stats["file_leden"] = self._load_files(file_path)
        stats["rol"] = self._load_rollen(file_path)
        
        # Generate thumbnails
        stats["thumbnails"] = self._generate_thumbnails()
        
        logger.info("Data load completed successfully")
        logger.info(f"Load statistics: {stats}")
        
        return stats
    
    def _load_leden(self, file_path: str) -> int:
        """Load members (leden) table"""
        logger.info("Loading leden (members)...")
        
        df_leden = pd.read_excel(file_path, sheet_name="Leden")
        
        # Transform: Sort surname, handling Dutch prefixes
        df_leden["achternaam_sort"] = ""
        tussenvoegsels = ["van der", "van den", "van de", "van", "de", "v.d."]
        
        for index, row in df_leden.iterrows():
            found = False
            i = 0
            
            while i < len(tussenvoegsels) and not found:
                if pd.isnull(row["Achternaam"]):
                    df_leden.loc[index, "achternaam_sort"] = "zzzzzzzz"
                    break
                    
                if tussenvoegsels[i] in row["Achternaam"][:len(tussenvoegsels[i])]:
                    achternaam_sort = row["Achternaam"].replace(tussenvoegsels[i] + " ", "")
                    df_leden.loc[index, "achternaam_sort"] = (
                        achternaam_sort + ", " + tussenvoegsels[i]
                    )
                    found = True
                i = i + 1
                
            if not found:
                df_leden.loc[index, "achternaam_sort"] = df_leden.loc[index, "Achternaam"]
        
        # Load to database
        df_leden.to_sql("lid", con=self.engine, if_exists="replace", index=False)
        logger.info(f"Loaded {len(df_leden)} members")
        
        return len(df_leden)
    
    def _load_uitvoeringen(self, file_path: str) -> int:
        """Load performances (uitvoeringen) table with enrichments"""
        logger.info("Loading uitvoeringen (performances)...")
        
        df_uitvoering = pd.read_excel(file_path, sheet_name="Uitvoering")
        df_uitvoering.rename(columns={"uitvoering": "ref_uitvoering"}, inplace=True)
        
        # Load roles to get director information
        df_rollen = pd.read_excel(file_path, sheet_name="Rollen")
        df_uitvoering_regie = (
            df_rollen.loc[df_rollen["rol"] == "Regie"]
            .groupby("ref_uitvoering")
            .agg("max")
            .reset_index()
        )
        df_uitvoering_regie = df_uitvoering_regie.drop(["rol", "rol_bijnaam"], axis=1)
        df_uitvoering_regie.columns = ["ref_uitvoering", "regie"]
        
        # Merge director info
        df_uitvoering = df_uitvoering.merge(
            right=df_uitvoering_regie, how="left", on="ref_uitvoering"
        )
        
        # Get media counts (will be updated after files are loaded)
        df_uitvoering["qty_media"] = 0
        
        # Load to database
        df_uitvoering.to_sql("uitvoering", con=self.engine, if_exists="replace", index=False)
        logger.info(f"Loaded {len(df_uitvoering)} performances")
        
        return len(df_uitvoering)
    
    def _load_media_types(self, file_path: str) -> int:
        """Load media types table"""
        logger.info("Loading media types...")
        
        df_media_type = pd.read_excel(file_path, sheet_name="Type_Media")
        df_media_type.to_sql("media_type", con=self.engine, if_exists="replace", index=False)
        logger.info(f"Loaded {len(df_media_type)} media types")
        
        return len(df_media_type)
    
    def _load_files(self, file_path: str) -> tuple[int, int]:
        """
        Load files and file_leden tables.
        
        Returns:
            Tuple of (file count, file_leden count)
        """
        logger.info("Loading files...")
        
        # Get uitvoering folder mapping
        df_uitvoering = pd.read_excel(file_path, sheet_name="Uitvoering")
        df_uitvoering.rename(columns={"uitvoering": "ref_uitvoering"}, inplace=True)
        df_uitvoering_folder = df_uitvoering[["ref_uitvoering", "folder"]]
        
        # Load files
        df_files = pd.read_excel(file_path, sheet_name="Bestand")
        df_files = df_files.merge(right=df_uitvoering_folder, how="left", on="ref_uitvoering")
        
        # Extract file extension
        df_files["file_ext"] = df_files["bestand"].str.split('.').str[-1]
        df_files["file_ext"] = df_files["file_ext"].str.lower()
        
        # Create file_leden (file-to-member mapping)
        df_files_leden = df_files.melt(
            id_vars=["ref_uitvoering", "bestand", "type_media", "file_ext", "folder"],
            var_name="vlnr",
            value_name="lid",
        ).reset_index()
        df_files_leden.dropna(subset=["lid"], inplace=True)
        df_files_leden.drop(columns=["index"], inplace=True)
        
        # Load file_leden table
        df_files_leden.to_sql("file_leden", con=self.engine, if_exists="replace", index=False)
        logger.info(f"Loaded {len(df_files_leden)} file-member associations")
        
        # Clean up file table (remove lid_* columns)
        df_files = df_files[df_files.columns.drop(list(df_files.filter(regex="lid_")))]
        df_files.to_sql("file", con=self.engine, if_exists="replace", index=False)
        logger.info(f"Loaded {len(df_files)} files")
        
        # Update uitvoering with media counts
        df_uitvoering_files = df_files.groupby("ref_uitvoering").size().reset_index()
        df_uitvoering_files.columns = ["ref_uitvoering", "qty_media"]
        
        # Update uitvoering table
        for _, row in df_uitvoering_files.iterrows():
            self.engine.execute(
                f"""
                UPDATE uitvoering 
                SET qty_media = {row['qty_media']} 
                WHERE ref_uitvoering = '{row['ref_uitvoering']}'
                """
            )
        
        return len(df_files), len(df_files_leden)
    
    def _load_rollen(self, file_path: str) -> int:
        """Load roles (rollen) table with media counts"""
        logger.info("Loading rollen (roles)...")
        
        df_rollen = pd.read_excel(file_path, sheet_name="Rollen")
        
        # Get media counts per role
        df_file_leden = pd.read_sql("SELECT * FROM file_leden", con=self.engine)
        df_rol_files = df_file_leden.groupby(["ref_uitvoering", "lid"]).size().reset_index()
        df_rol_files.columns = ["ref_uitvoering", "id_lid", "qty_media"]
        
        # Merge media counts
        df_rollen = df_rollen.merge(right=df_rol_files, how="left", on=["ref_uitvoering", "id_lid"])
        df_rollen["qty_media"] = df_rollen["qty_media"].fillna(0)
        
        # Load to database
        df_rollen.to_sql("rol", con=self.engine, if_exists="replace", index=False)
        logger.info(f"Loaded {len(df_rollen)} roles")
        
        return len(df_rollen)
    
    def _generate_thumbnails(self) -> int:
        """
        Generate thumbnail images for all photos in resources directory.
        
        Returns:
            Number of thumbnails created
        """
        logger.info("Generating thumbnails...")
        
        thumbnail_count = 0
        
        for root, dirs, files in os.walk(self.dir_resources):
            if "thumbnails" not in root:
                # Create thumbnails directory if it doesn't exist
                thumbnail_dir = Path(root) / "thumbnails"
                thumbnail_dir.mkdir(parents=True, exist_ok=True)
                
                # Process each image file
                for file in files:
                    if any(file.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg"]):
                        try:
                            image_path = os.path.join(root, file)
                            thumbnail_path = os.path.join(thumbnail_dir, file)
                            
                            # Skip if thumbnail already exists
                            if os.path.exists(thumbnail_path):
                                continue
                            
                            # Create thumbnail
                            image = Image.open(image_path)
                            image.thumbnail((300, 300), Image.LANCZOS)
                            image.save(thumbnail_path, quality=95)
                            thumbnail_count += 1
                            
                        except Exception as e:
                            logger.error(f"Failed to create thumbnail for {file}: {e}")
        
        logger.info(f"Generated {thumbnail_count} new thumbnails")
        return thumbnail_count
    
    def validate_excel(self, file_path: str) -> dict:
        """
        Validate Excel file structure before loading.
        
        Args:
            file_path: Path to Excel file
            
        Returns:
            Dictionary with validation results
        """
        logger.info(f"Validating Excel file: {file_path}")
        
        validation = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "info": {}
        }
        
        if not os.path.exists(file_path):
            validation["valid"] = False
            validation["errors"].append(f"File not found: {file_path}")
            return validation
        
        try:
            # Check required sheets exist
            required_sheets = ["Leden", "Uitvoering", "Rollen", "Bestand", "Type_Media"]
            xl_file = pd.ExcelFile(file_path)
            
            for sheet in required_sheets:
                if sheet not in xl_file.sheet_names:
                    validation["valid"] = False
                    validation["errors"].append(f"Missing required sheet: {sheet}")
                else:
                    # Get row counts
                    df = pd.read_excel(file_path, sheet_name=sheet)
                    validation["info"][sheet] = len(df)
            
            # Check for required columns
            df_leden = pd.read_excel(file_path, sheet_name="Leden")
            required_leden_cols = ["id_lid", "Voornaam", "Achternaam"]
            for col in required_leden_cols:
                if col not in df_leden.columns:
                    validation["valid"] = False
                    validation["errors"].append(f"Leden sheet missing column: {col}")
            
            # Additional validation can be added here
            
        except Exception as e:
            validation["valid"] = False
            validation["errors"].append(f"Error reading Excel file: {str(e)}")
        
        return validation

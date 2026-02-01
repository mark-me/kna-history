import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from PIL import Image


data_root = Path("/data/kna_resources/")
file_db = data_root / "kna_database.xlsx"


class DBLoader:
    def __init__(self, path_excel: Path):
        """Initialize a DBLoader for importing Excel data into the KNA database.

        Sets up the source Excel path and creates a MySQL SQLAlchemy engine for
        persisting loaded data into the configured KNA schema.

        """
        self.path_excel = path_excel
        self.engine = create_engine(
            "mysql+mysqldb://root:kna-toneel@127.0.0.1:3306/kna"
        )

    def process(self) -> None:
        self._members()
        self._media_types()

        self._create_thumbnails()

    def _create_thumbnails(self) -> None:
        """Generate 300x300 thumbnails for all images under the KNA resources tree.

        Walks the `/data/kna_resources` directory, creates a `thumbnails` subdirectory
        in each folder, and writes resized copies of JPEG and PNG images there.

        """
        for root, dirs, files in os.walk("/data/kna_resources"):
            if "thumbnails" not in root:
                Path(root + "/thumbnails").mkdir(parents=True, exist_ok=True)
                for file in files:
                    if any(file.lower().endswith(ext) for ext in [".png", ".jpg", ".jpeg"]):
                        image = Image.open(root + "/" + file)
                        image.thumbnail((300, 300), Image.LANCZOS)
                        image.save(root + "/thumbnails/" + file, quality=95)

    def _members(self) -> None:
        """Load member data from the Excel file and persist it to the database.

        Normalizes the last-name field for sorting purposes and writes the resulting
        member table into the `lid` table in the configured database.

        """
        df_members = pd.read_excel(self.path_excel, sheet_name="Leden")
        # Achternaam sortering, verwijderen tussenvoegsels
        df_members["achternaam_sort"] = ""
        tussenvoegsels = ["van der", "van den", "van de", "van", "de", "v.d."]
        for index, row in df_members.iterrows():
            found = False
            i = 0
            while i < len(tussenvoegsels) and not found:
                if pd.isnull(row["Achternaam"]):
                    df_members.loc[index, "achternaam_sort"] = "zzzzzzzz"
                    break
                if tussenvoegsels[i] in row["Achternaam"][: len(tussenvoegsels[i])]:
                    achternaam_sort = row["Achternaam"].replace(
                        tussenvoegsels[i] + " ", ""
                    )
                    df_members.loc[index, "achternaam_sort"] = (
                        achternaam_sort + ", " + tussenvoegsels[i]
                    )
                    found = True
                i += 1
            if not found:
                df_members.loc[index, "achternaam_sort"] = df_members.loc[
                    index, "Achternaam"
                ]
        df_members.to_sql("lid", con=self.engine, if_exists="replace", index=False)

    def _performace(self) -> None:
        df_performance = pd.read_excel(self.path_excel, sheet_name="Uitvoering")
        df_performance.rename(columns={"uitvoering": "ref_uitvoering"}, inplace=True)

        df_performance_folder = df_performance[["ref_uitvoering", "folder"]]
        self._files(df_performance_folder=df_performance_folder)
        df_roles = self._roles()
        df_director = self._director(df_roles=df_roles)
        df_performance = df_director.merge(
            right=df_director, how="left", on="ref_uitvoering"
        )
        df_performance_files = self._performance_files(df_files=)

    def _roles(self) -> pd.DataFrame:
        df_roles = pd.read_excel(self.path_excel, sheet_name="Rollen")
        return df_roles

    def _media_types(self) -> None:
        df_media_type = pd.read_excel(self.path_excel, sheet_name="Type_Media")
        df_media_type.to_sql(
            "media_type", con=self.engine, if_exists="replace", index=False
        )

    def _files(self, df_performance_folder: pd.DataFrame) -> None:
        """Load file metadata, enrich it with performance information, and persist it.

        Reads file records from Excel, derives file extensions, links files to their
        performance folders, normalizes member associations, and writes the result to
        the `file` table.

        Args:
            df_performance_folder (pd.DataFrame): DataFrame mapping performance
                references to their corresponding folder paths.

        Returns:
            None: The processed file metadata is written directly to the database.

        """
        df_files = pd.read_excel(self.path_excel, sheet_name="Bestand")
        df_files = df_files.merge(
            right=df_performance_folder, how="left", on="ref_uitvoering"
        )
        df_files["file_ext"] = df_files["bestand"].str.split(".").str[-1]
        df_files["file_ext"] = df_files["file_ext"].str.lower()
        self._file_members(df_files=df_files)
        df_files = df_files[df_files.columns.drop(list(df_files.filter(regex="lid_")))]
        df_files.to_sql("file", con=self.engine, if_exists="replace", index=False)

    def _file_members(self, df_files: pd.DataFrame) -> None:
        """Transform per-file member columns into a normalized file-member mapping.

        Unpivots member-related columns into rows, removes empty member entries, and
        writes the resulting file-to-member associations to the `file_leden` table.

        Args:
            df_files (pd.DataFrame): DataFrame containing file records, including
                member reference columns to be normalized.

        Returns:
            None: The resulting associations are persisted directly to the database.

        """
        df_file_members = df_files.melt(
            id_vars=["ref_uitvoering", "bestand", "type_media", "file_ext", "folder"],
            var_name="vlnr",
            value_name="lid",
        ).reset_index()
        df_file_members.dropna(subset=["lid"], inplace=True)
        df_file_members.drop(columns=["index"], inplace=True)
        df_file_members.to_sql("file_leden", con=self.engine, if_exists="replace", index=False)

    def _performance_files(self, df_files: pd.DataFrame) -> pd.DataFrame:
        """Aggregate the number of media files per performance.

        Groups the provided file metadata by performance reference and returns a
        summary table with a media count for each performance.

        Args:
            df_files (pd.DataFrame): DataFrame containing file records with a
                `ref_uitvoering` column identifying the related performance.

        Returns:
            pd.DataFrame: DataFrame with one row per performance and a `qty_media`
                column containing the number of associated files.

        """
        df_performance_files = df_files.groupby("ref_uitvoering").size().reset_index()
        df_performance_files.columns = ["ref_uitvoering", "qty_media"]
        return df_performance_files

    def _director(self, df_roles: pd.DataFrame) -> pd.DataFrame:
        """Extract the director for each performance from the roles data.

        Filters the roles to those marked as direction, aggregates them per
        performance, and returns a condensed mapping of performance to director.

        Args:
            df_roles (pd.DataFrame): DataFrame containing role records per performance,
                including a column identifying direction roles.

        Returns:
            pd.DataFrame: DataFrame with one row per performance and the associated
                director information.

        """
        df_director = (
            df_roles.loc[df_roles["rol"] == "Regie"]
            .groupby("ref_uitvoering")
            .agg("max")
            .reset_index()
        )
        df_director = df_director.drop(["rol", "rol_bijnaam"], axis=1)
        df_director.columns = ["ref_uitvoering", "regie"]



df_uitvoering = df_uitvoering.merge(
    right=df_uitvoering_files, how="left", on="ref_uitvoering"
)
df_uitvoering["qty_media"] = df_uitvoering["qty_media"].fillna(0)
df_uitvoering.to_sql("uitvoering", con=self.engine, if_exists="replace", index=False)

df_rol_files = df_files_leden.groupby(["ref_uitvoering", "lid"]).size().reset_index()
df_rol_files.columns = ["ref_uitvoering", "id_lid", "qty_media"]
df_roles = df_rollen.merge(
    right=df_rol_files, how="left", on=["ref_uitvoering", "id_lid"]
)
df_roles["qty_media"] = df_roles["qty_media"].fillna(0)
df_roles.to_sql("rol", con=self.engine, if_exists="replace", index=False)



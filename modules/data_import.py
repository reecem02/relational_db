import pandas as pd
from Bio import SeqIO
from sqlalchemy import create_engine, inspect
import yaml
import os
from modules.data_output import print_row_key_value
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from datetime import datetime


# Load configuration (from config.yaml)
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# Load DB Path 
DB_PATH = os.path.expanduser("~/fungal_db.sqlite")  # or from config.yaml
DB_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DB_URL)

Session = sessionmaker(bind=engine)

def validate_columns(table_name, df):
    """
    Validate that the columns in the DataFrame match the columns in the database table.
    
    :param table_name: The name of the target table in the database.
    :param df: The DataFrame containing the data to be imported.
    :return: None if columns match, raises ValueError if they don’t.
    """
    # Use SQLAlchemy inspector to fetch table schema
    inspector = inspect(engine)
    try:
        db_columns = [col["name"] for col in inspector.get_columns(table_name)]
    except:
        raise ValueError(f"Table '{table_name}' does not exist in the database. "
                         f"Please create it or let pandas create it before validation.")    
    
    # Get DataFrame columns
    file_columns = list(df.columns)

    # Check for mismatches
    missing_columns = [col for col in db_columns if col not in file_columns]
    extra_columns = [col for col in file_columns if col not in db_columns]

    if missing_columns or extra_columns:
        raise ValueError(
            f"Column mismatch for table '{table_name}':\n"
            f"Missing columns in file: {missing_columns}\n"
            f"Unexpected columns in file: {extra_columns}"
        )


def import_metadata(file_path):
    """
    Import metadata from an Excel file into the Metadata table.
    """
    try:
        # Load metadata into DataFrame
        print("Loading metadata...")
        metadata = pd.read_excel(file_path)

        with Session() as session:
            for _, row in metadata.iterrows():
                lab_id = row["Uehling Lab ID"]

                # Check if lab_id already exists
                query = text("SELECT * FROM metadata WHERE [Uehling Lab ID] = :lab_id")
                result = session.execute(query, {"lab_id": lab_id}).mappings().fetchone()

                if result:
                    print(f"\nLab ID {lab_id} already exists in the database.")
                    print_row_key_value(dict(result), "Existing Entry in Database")
                    print_row_key_value(row.to_dict(), "New Entry from File")

                    decision = input(f"\nOptions: [1] Skip or [2] Replace existing entry for '{lab_id}' (1/2): ")

                    if decision == "2":
                        # Replace existing entry
                        delete_query = text("DELETE FROM metadata WHERE [Uehling Lab ID] = :lab_id")
                        session.execute(delete_query, {"lab_id": lab_id})
                        print(f"Deleted existing entry for Lab ID {lab_id}.")

                        # Prepare the row dictionary with correct keys
                        row_dict = {
                            "lab_id": row["Uehling Lab ID"],
                            "sample_location_plate": row["Sample Location Plate"],
                            "gc3f_submission_sample_id": row["GC3F Submission Sample ID"],
                            "alternate_id_1": row["Alternate ID 1"],
                            "alternate_id_2": row["Alternate ID 2"],
                            "lab_unique_id_3": row["Lab Unique ID 3"],
                            "extracted_by": row["Extracted by"],
                            "top_its_blast_hit": row["Top ITS Blast Hit"],
                            "its_top_hit_similarity": row["ITS Top Hit Similarity"],
                            "its_taxonomy_comments": row["ITS Taxonomy Comments"],
                            "top_16s_blast_hit": row["Top 16S Blast Hit"],
                            "16s_top_hit_similarity": row["16S Top Hit Similarity"],
                            "16s_taxonomy_comments": row["16S Taxonomy Comments"],
                            "project_funding": row["Project Funding"],
                            "latitude": row["Latitude"],
                            "longitude": row["Longitude"],
                            "location_id": row["Location ID"],
                            "dna_extraction_method": row["DNA Extraction Method"],
                            # Convert Timestamp to string
                            "extraction_date": row["Extraction Date"].strftime("%Y-%m-%d"),
                            "file_uploaded": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                        }

                        # Insert new entry using the session
                        insert_query = text("""
                            INSERT INTO metadata (
                                "Uehling Lab ID", "Sample Location Plate", "GC3F Submission Sample ID",
                                "Alternate ID 1", "Alternate ID 2", "Lab Unique ID 3", "Extracted by",
                                "Top ITS Blast Hit", "ITS Top Hit Similarity", "ITS Taxonomy Comments",
                                "Top 16S Blast Hit", "16S Top Hit Similarity", "16S Taxonomy Comments",
                                "Project Funding", "Latitude", "Longitude", "Location ID",
                                "DNA Extraction Method", "Extraction Date"
                            ) VALUES (
                                :lab_id, :sample_location_plate, :gc3f_submission_sample_id,
                                :alternate_id_1, :alternate_id_2, :lab_unique_id_3, :extracted_by,
                                :top_its_blast_hit, :its_top_hit_similarity, :its_taxonomy_comments,
                                :top_16s_blast_hit, :16s_top_hit_similarity, :16s_taxonomy_comments,
                                :project_funding, :latitude, :longitude, :location_id,
                                :dna_extraction_method, :extraction_date, :file_uploaded
                            )
                        """)
                        session.execute(insert_query, row_dict)
                        print(f"Replaced existing entry for Lab ID {lab_id}.")
                    else:
                        print(f"Skipped entry for Lab ID {lab_id}.")
                else:
                    # Prepare the row dictionary with correct keys
                    row_dict = {
                        "lab_id": row["Uehling Lab ID"],
                        "sample_location_plate": row["Sample Location Plate"],
                        "gc3f_submission_sample_id": row["GC3F Submission Sample ID"],
                        "alternate_id_1": row["Alternate ID 1"],
                        "alternate_id_2": row["Alternate ID 2"],
                        "lab_unique_id_3": row["Lab Unique ID 3"],
                        "extracted_by": row["Extracted by"],
                        "top_its_blast_hit": row["Top ITS Blast Hit"],
                        "its_top_hit_similarity": row["ITS Top Hit Similarity"],
                        "its_taxonomy_comments": row["ITS Taxonomy Comments"],
                        "top_16s_blast_hit": row["Top 16S Blast Hit"],
                        "16s_top_hit_similarity": row["16S Top Hit Similarity"],
                        "16s_taxonomy_comments": row["16S Taxonomy Comments"],
                        "project_funding": row["Project Funding"],
                        "latitude": row["Latitude"],
                        "longitude": row["Longitude"],
                        "location_id": row["Location ID"],
                        "dna_extraction_method": row["DNA Extraction Method"],
                        # Convert Timestamp to string
                        "extraction_date": row["Extraction Date"].strftime("%Y-%m-%d"),
                        "file_uploaded": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 

                    }

                    # Insert new entry using the session
                    insert_query = text("""
                        INSERT INTO metadata (
                            "Uehling Lab ID", "Sample Location Plate", "GC3F Submission Sample ID",
                            "Alternate ID 1", "Alternate ID 2", "Lab Unique ID 3", "Extracted by",
                            "Top ITS Blast Hit", "ITS Top Hit Similarity", "ITS Taxonomy Comments",
                            "Top 16S Blast Hit", "16S Top Hit Similarity", "16S Taxonomy Comments",
                            "Project Funding", "Latitude", "Longitude", "Location ID",
                            "DNA Extraction Method", "Extraction Date"
                        ) VALUES (
                            :lab_id, :sample_location_plate, :gc3f_submission_sample_id,
                            :alternate_id_1, :alternate_id_2, :lab_unique_id_3, :extracted_by,
                            :top_its_blast_hit, :its_top_hit_similarity, :its_taxonomy_comments,
                            :top_16s_blast_hit, :16s_top_hit_similarity, :16s_taxonomy_comments,
                            :project_funding, :latitude, :longitude, :location_id,
                            :dna_extraction_method, :extraction_date, :file_uploaded
                        )
                    """)
                    session.execute(insert_query, row_dict)
                    print(f"Inserted new entry for Lab ID {lab_id}.")

            # Commit the transaction
            session.commit()

        # Validate columns
        validate_columns("metadata", metadata)
        print("Validating metadata columns...")

    except Exception as e:
        print(f"Error importing metadata: {e}")


def import_fasta(file_path):
    """
    Import genomic data from a FASTA file into the GenomicData table.
    """
    try:
        print("Loading genomic data from FASTA file...")
        sequences = []
        for record in SeqIO.parse(file_path, "fasta"):
            lab_id = input(f"Enter the Uehling Lab ID for sequence {record.id}: ").strip()
            sequences.append({"lab_id": lab_id, "sequence": str(record.seq)})

        # Create DataFrame
        df = pd.DataFrame(sequences)

        # Validate that lab_id exists in Metadata
        with Session() as session:
            for _, row in df.iterrows():
                query = text("SELECT * FROM metadata WHERE [Uehling Lab ID] = :lab_id")
                result = session.execute(query, {"lab_id": row["lab_id"]}).mappings().fetchone()
                if not result:
                    raise ValueError(f"Lab ID {row['lab_id']} does not exist in Metadata. Please add it first.")

        # Insert into GenomicData table
        df.to_sql("genomicdata", con=engine, if_exists="append", index=False)
        print("FASTA data imported successfully.")

    except Exception as e:
        print(f"Error importing FASTA file: {e}")

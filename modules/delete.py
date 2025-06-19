from sqlalchemy import text
from modules.data_output import display_data_by_lab_id
from modules.data_import import engine, Session
import pandas as pd
from modules.data_import import engine

def display_lab_id_data(lab_id):
    # Show metadata as a clean table
    query_metadata = """
        SELECT key, value
        FROM Metadata
        WHERE lab_id = :lab_id
    """
    metadata = pd.read_sql(query_metadata, con=engine, params={"lab_id": lab_id})
    if not metadata.empty:
        print("\n-- Metadata --")
        print(metadata.to_string(index=False))
    else:
        print("No metadata found.")

    # Show FASTA/GenomicData as a clean table (first 5 sequences)
    query_genomic = """
        SELECT key, value
        FROM GenomicData
        WHERE lab_id = :lab_id
        LIMIT 5
    """
    fasta = pd.read_sql(query_genomic, con=engine, params={"lab_id": lab_id})
    if not fasta.empty:
        print("\n-- FASTA Sequences (first 5) --")
        for idx, row in fasta.iterrows():
            seq = row['value']
            lines = [seq[i:i+60] for i in range(0, len(seq), 60)]
            display_lines = lines[:2]
            print(f">{row['key']}")
            for l in display_lines:
                print(l)
            if len(lines) > 2:
                print("...")
    else:
        print("No FASTA sequences found.")

def delete_lab_id(lab_id):
    with Session() as session:
        session.execute(text("DELETE FROM Metadata WHERE lab_id = :lab_id"), {"lab_id": lab_id})
        session.execute(text("DELETE FROM GenomicData WHERE lab_id = :lab_id"), {"lab_id": lab_id})
        session.commit()

def delete_metadata(lab_id):
    with Session() as session:
        session.execute(text("DELETE FROM Metadata WHERE lab_id = :lab_id"), {"lab_id": lab_id})
        session.commit()

def delete_fasta(lab_id):
    with Session() as session:
        session.execute(text("DELETE FROM GenomicData WHERE lab_id = :lab_id"), {"lab_id": lab_id})
        session.commit()
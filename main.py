import tables
import populate
import subprocess
import os
import argparse

def main(force, repopulate, update, diff, tables_to_process, where_clause):
    subprocess.run("cls" if os.name == "nt" else "clear", shell=True)
    
    tables.start(force=force, tables_to_process=tables_to_process)
    
    mode = None        
    if diff:
        mode = "diff"

    if repopulate:
        mode = "repopulate"

    if update:
        mode = "update"
    
    populate.populate_tables(mode, tables_to_process, force)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Command line arguments:')
    parser.add_argument('--force', action='store_true', help='Force drop and recreate the target database')
    parser.add_argument('--repopulate', action='store_true', help='Repopulate the database')
    parser.add_argument('--update', action='store_true', help='Update the database')
    parser.add_argument('--diff', action='store_true', help='Show the differences between the current database and the new data')
    parser.add_argument('--table', type=str, nargs='*', help='List of tables to process, separated by commas')
    parser.add_argument('--where', type=str, nargs=1, help='SQL where clause to use for populating tables')
    args = parser.parse_args()
    main(force=args.force, repopulate=args.repopulate, update=args.update, diff=args.diff, tables_to_process=args.table, where_clause=args.where[0] if args.where else None)

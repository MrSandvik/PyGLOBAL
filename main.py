import tables
import populate
import os

def main():
    os.system('clear')
    tables.create_tables()
    populate.populate_tables()

if __name__ == '__main__':
    main()

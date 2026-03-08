"""
Database migration script to update the unique constraint on fees table
This recreates the fees table with the correct constraint
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db
from datetime import datetime
from sqlalchemy import text

def migrate_fees_constraint():
    """Update unique constraint from (student_id, semester) to (student_id, semester, fee_type)"""
    app = create_app()
    
    with app.app_context():
        try:
            with db.engine.connect() as connection:
                print("Starting constraint migration...")
                
                # Step 1: Create a new table with the correct constraint
                print("1. Creating new fees table with updated constraint...")
                connection.execute(text("""
                    CREATE TABLE fees_new (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        student_id INTEGER NOT NULL,
                        fee_type VARCHAR(100) NOT NULL,
                        semester INTEGER NOT NULL,
                        amount FLOAT NOT NULL,
                        status VARCHAR(20) NOT NULL DEFAULT 'pending',
                        paid_date DATETIME,
                        due_date DATE,
                        notes TEXT,
                        created_at DATETIME,
                        updated_at DATETIME,
                        FOREIGN KEY(student_id) REFERENCES students (id),
                        UNIQUE (student_id, semester, fee_type)
                    )
                """))
                connection.commit()
                print("✓ New table created")
                
                # Step 2: Copy data from old table to new table
                print("2. Copying data from old table to new table...")
                connection.execute(text("""
                    INSERT INTO fees_new 
                    (id, student_id, fee_type, semester, amount, status, paid_date, due_date, notes, created_at, updated_at)
                    SELECT id, student_id, fee_type, semester, amount, status, paid_date, due_date, notes, created_at, updated_at
                    FROM fees
                """))
                connection.commit()
                print("✓ Data copied successfully")
                
                # Step 3: Drop old table
                print("3. Dropping old fees table...")
                connection.execute(text("DROP TABLE fees"))
                connection.commit()
                print("✓ Old table dropped")
                
                # Step 4: Rename new table to fees
                print("4. Renaming new table to fees...")
                connection.execute(text("ALTER TABLE fees_new RENAME TO fees"))
                connection.commit()
                print("✓ Table renamed")
                
                print("\n✅ Constraint migration completed successfully!")
                print("The fees table now has the correct unique constraint: (student_id, semester, fee_type)")
                
        except Exception as e:
            print(f"\n❌ Migration failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("Fee Table Constraint Migration Script")
    print("=" * 60)
    print("\nThis script will update the unique constraint on fees table:")
    print("  FROM: (student_id, semester)")
    print("  TO:   (student_id, semester, fee_type)")
    print("\nThis allows multiple fee types per semester.")
    print("\n⚠️  WARNING: This will recreate the fees table.")
    print("   Make sure you have a backup of your database!")
    print("\n" + "=" * 60)
    
    response = input("\nProceed with migration? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        migrate_fees_constraint()
    else:
        print("Migration cancelled.")

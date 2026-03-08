"""
Database migration script to add fee_type and updated_at columns to fees table
Run this script to update your existing database schema
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import db
from datetime import datetime
from sqlalchemy import text, inspect

def migrate_fees_table():
    """Add fee_type and updated_at columns to fees table"""
    app = create_app()
    
    with app.app_context():
        try:
            # Check if columns already exist
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('fees')]
            
            print(f"Current columns in fees table: {columns}")
            
            with db.engine.connect() as connection:
                # Add fee_type column if it doesn't exist
                if 'fee_type' not in columns:
                    print("Adding fee_type column...")
                    connection.execute(text(
                        "ALTER TABLE fees ADD COLUMN fee_type VARCHAR(100) DEFAULT 'Tuition'"
                    ))
                    connection.commit()
                    print("✓ Added fee_type column")
                else:
                    print("✓ fee_type column already exists")
                
                # Add updated_at column if it doesn't exist
                if 'updated_at' not in columns:
                    print("Adding updated_at column...")
                    timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                    connection.execute(text(
                        f"ALTER TABLE fees ADD COLUMN updated_at DATETIME DEFAULT '{timestamp}'"
                    ))
                    connection.commit()
                    print("✓ Added updated_at column")
                else:
                    print("✓ updated_at column already exists")
                
                # Update existing records to have 'Tuition' as default fee_type
                print("Setting default fee_type for existing records...")
                connection.execute(text(
                    "UPDATE fees SET fee_type = 'Tuition' WHERE fee_type IS NULL"
                ))
                connection.commit()
                
                # Update existing records to have current timestamp for updated_at
                print("Setting updated_at timestamp for existing records...")
                timestamp = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                connection.execute(text(
                    f"UPDATE fees SET updated_at = '{timestamp}' WHERE updated_at IS NULL"
                ))
                connection.commit()
            
            print("\n✅ Migration completed successfully!")
            print("The fees table now has fee_type and updated_at columns.")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {str(e)}")
            print("\nIf you see 'duplicate column name' error, the columns already exist.")
            import traceback
            traceback.print_exc()
            return False
    
    return True

if __name__ == '__main__':
    print("=" * 60)
    print("Fee Table Migration Script")
    print("=" * 60)
    print("\nThis script will add the following columns to the fees table:")
    print("  - fee_type (VARCHAR(100), default: 'Tuition')")
    print("  - updated_at (DATETIME)")
    print("\n" + "=" * 60)
    
    response = input("\nProceed with migration? (yes/no): ").strip().lower()
    
    if response in ['yes', 'y']:
        migrate_fees_table()
    else:
        print("Migration cancelled.")

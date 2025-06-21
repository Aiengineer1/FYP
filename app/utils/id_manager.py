"""
ID Manager Utility
Provides functions to manage sequential IDs with gap filling capability.
When records are deleted, their IDs are reused for new records.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func, text
from typing import Type, Optional
import logging

logger = logging.getLogger(__name__)

def get_next_available_id(db: Session, model_class: Type, id_column_name: str = "id") -> int:
    """
    Get the next available ID for a model, filling gaps from deleted records.
    
    Args:
        db: Database session
        model_class: SQLAlchemy model class (User, Mall, Camera, etc.)
        id_column_name: Name of the ID column (default: "id")
    
    Returns:
        int: Next available ID (either a gap or next sequential number)
    """
    try:
        # Get the ID column
        id_column = getattr(model_class, id_column_name)
        
        # Get all existing IDs, ordered
        existing_ids = db.query(id_column).order_by(id_column).all()
        existing_ids = [id_tuple[0] for id_tuple in existing_ids]
        
        logger.info(f"Existing IDs for {model_class.__name__}: {existing_ids}")
        
        # If no records exist, start with ID 1
        if not existing_ids:
            logger.info(f"No existing records, returning ID: 1")
            return 1
        
        # Check for gaps in the sequence
        for i in range(1, max(existing_ids) + 1):
            if i not in existing_ids:
                logger.info(f"Found gap at ID: {i}")
                return i
        
        # No gaps found, return next sequential number
        next_id = max(existing_ids) + 1
        logger.info(f"No gaps found, returning next sequential ID: {next_id}")
        return next_id
        
    except Exception as e:
        logger.error(f"Error getting next available ID for {model_class.__name__}: {str(e)}")
        # Fallback to auto-increment behavior
        return None

def reset_sequence_to_lowest_gap(db: Session, model_class: Type, id_column_name: str = "id") -> Optional[int]:
    """
    Reset the auto-increment sequence to the lowest available gap.
    This is useful after bulk deletions to ensure new records use the lowest IDs.
    
    Args:
        db: Database session
        model_class: SQLAlchemy model class
        id_column_name: Name of the ID column
    
    Returns:
        int: The sequence value that was set, or None if failed
    """
    try:
        table_name = model_class.__tablename__
        next_id = get_next_available_id(db, model_class, id_column_name)
        
        if next_id is None:
            return None
        
        # Reset PostgreSQL sequence (if using PostgreSQL)
        sequence_name = f"{table_name}_{id_column_name}_seq"
        try:
            # Set sequence to next_id - 1 so next insert gets next_id
            sequence_value = max(1, next_id - 1)
            db.execute(text(f"ALTER SEQUENCE {sequence_name} RESTART WITH {sequence_value}"))
            db.commit()
            logger.info(f"Reset sequence {sequence_name} to {sequence_value}")
            return sequence_value
        except Exception as seq_error:
            logger.warning(f"Could not reset sequence (might not be PostgreSQL): {str(seq_error)}")
            # For SQLite or other databases, we'll handle this manually
            return next_id
            
    except Exception as e:
        logger.error(f"Error resetting sequence: {str(e)}")
        return None

def create_record_with_managed_id(db: Session, model_class: Type, record_data: dict, id_column_name: str = "id"):
    """
    Create a new record with managed ID (fills gaps).
    
    Args:
        db: Database session
        model_class: SQLAlchemy model class
        record_data: Dictionary of record data (without ID)
        id_column_name: Name of the ID column
    
    Returns:
        Created record instance
    """
    try:
        # Get the next available ID
        next_id = get_next_available_id(db, model_class, id_column_name)
        
        if next_id is not None:
            # Explicitly set the ID
            record_data[id_column_name] = next_id
            logger.info(f"Creating {model_class.__name__} with managed ID: {next_id}")
        else:
            logger.info(f"Using auto-increment for {model_class.__name__}")
        
        # Create the record
        db_record = model_class(**record_data)
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        
        logger.info(f"Successfully created {model_class.__name__} with ID: {db_record.id}")
        return db_record
        
    except Exception as e:
        logger.error(f"Error creating {model_class.__name__} with managed ID: {str(e)}")
        db.rollback()
        raise

def get_id_statistics(db: Session, model_class: Type, id_column_name: str = "id") -> dict:
    """
    Get statistics about ID usage for a model.
    
    Args:
        db: Database session
        model_class: SQLAlchemy model class
        id_column_name: Name of the ID column
    
    Returns:
        dict: Statistics including gaps, count, min, max, etc.
    """
    try:
        id_column = getattr(model_class, id_column_name)
        
        # Get basic statistics
        result = db.query(
            func.count(id_column).label('total_records'),
            func.min(id_column).label('min_id'),
            func.max(id_column).label('max_id')
        ).first()
        
        total_records = result.total_records
        min_id = result.min_id
        max_id = result.max_id
        
        if total_records == 0:
            return {
                'model': model_class.__name__,
                'total_records': 0,
                'min_id': None,
                'max_id': None,
                'gaps': [],
                'gap_count': 0,
                'next_available_id': 1,
                'sequence_efficiency': 100.0
            }
        
        # Get all existing IDs
        existing_ids = db.query(id_column).order_by(id_column).all()
        existing_ids = [id_tuple[0] for id_tuple in existing_ids]
        
        # Find gaps
        gaps = []
        if min_id and max_id:
            expected_range = set(range(min_id, max_id + 1))
            existing_set = set(existing_ids)
            gaps = sorted(list(expected_range - existing_set))
        
        # Calculate efficiency (how many IDs are actually used vs theoretical max)
        if max_id:
            sequence_efficiency = (total_records / max_id) * 100
        else:
            sequence_efficiency = 100.0
        
        # Get next available ID
        next_available_id = get_next_available_id(db, model_class, id_column_name)
        
        return {
            'model': model_class.__name__,
            'total_records': total_records,
            'min_id': min_id,
            'max_id': max_id,
            'gaps': gaps,
            'gap_count': len(gaps),
            'next_available_id': next_available_id,
            'sequence_efficiency': round(sequence_efficiency, 2)
        }
        
    except Exception as e:
        logger.error(f"Error getting ID statistics for {model_class.__name__}: {str(e)}")
        return {
            'model': model_class.__name__,
            'error': str(e)
        } 
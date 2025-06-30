"""
Operational Transform implementation for real-time collaborative editing.
Handles conflict resolution when multiple users edit the same document simultaneously.
"""
import json
from typing import Dict, List, Tuple, Any
from datetime import datetime


class Operation:
    """Represents a single operation (insert, delete, replace) on a document."""
    
    def __init__(self, op_type: str, position: int, content: str = "", length: int = 0):
        self.type = op_type  # 'insert', 'delete', 'replace'
        self.position = position
        self.content = content
        self.length = length or len(content)
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert operation to dictionary for JSON serialization."""
        return {
            'type': self.type,
            'position': self.position,
            'content': self.content,
            'length': self.length,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Operation':
        """Create operation from dictionary."""
        return cls(
            op_type=data['type'],
            position=data['position'],
            content=data.get('content', ''),
            length=data.get('length', 0)
        )
    
    def __repr__(self):
        if self.type == 'insert':
            return f"Insert('{self.content}' at {self.position})"
        elif self.type == 'delete':
            return f"Delete({self.length} chars at {self.position})"
        elif self.type == 'replace':
            return f"Replace({self.length} chars at {self.position} with '{self.content}')"
        return f"Operation({self.type}, {self.position})"


class OperationalTransform:
    """
    Operational Transform implementation for collaborative text editing.
    
    This implementation uses the standard OT approach where operations are
    transformed against each other to maintain document consistency across
    multiple concurrent edits.
    """
    
    def __init__(self):
        self.operation_history = []
    
    def transform_operations(self, op1: Operation, op2: Operation) -> Tuple[Operation, Operation]:
        """
        Transform two concurrent operations against each other.
        
        Returns transformed versions of both operations that can be applied
        in any order and will result in the same final document state.
        """
        if op1.type == 'insert' and op2.type == 'insert':
            return self._transform_insert_insert(op1, op2)
        elif op1.type == 'insert' and op2.type == 'delete':
            return self._transform_insert_delete(op1, op2)
        elif op1.type == 'delete' and op2.type == 'insert':
            op2_prime, op1_prime = self._transform_insert_delete(op2, op1)
            return op1_prime, op2_prime
        elif op1.type == 'delete' and op2.type == 'delete':
            return self._transform_delete_delete(op1, op2)
        elif op1.type == 'replace' or op2.type == 'replace':
            return self._transform_with_replace(op1, op2)
        else:
            # Default: no transformation needed
            return op1, op2
    
    def _transform_insert_insert(self, op1: Operation, op2: Operation) -> Tuple[Operation, Operation]:
        """Transform two concurrent insert operations."""
        if op1.position <= op2.position:
            # op1 comes before op2, adjust op2's position
            op2_prime = Operation('insert', op2.position + len(op1.content), op2.content)
            return op1, op2_prime
        else:
            # op2 comes before op1, adjust op1's position
            op1_prime = Operation('insert', op1.position + len(op2.content), op1.content)
            return op1_prime, op2
    
    def _transform_insert_delete(self, insert_op: Operation, delete_op: Operation) -> Tuple[Operation, Operation]:
        """Transform insert operation against delete operation."""
        if insert_op.position <= delete_op.position:
            # Insert happens before delete region
            delete_op_prime = Operation('delete', delete_op.position + len(insert_op.content), "", delete_op.length)
            return insert_op, delete_op_prime
        elif insert_op.position >= delete_op.position + delete_op.length:
            # Insert happens after delete region
            insert_op_prime = Operation('insert', insert_op.position - delete_op.length, insert_op.content)
            return insert_op_prime, delete_op
        else:
            # Insert happens within delete region - prioritize insert
            delete_op_prime = Operation('delete', delete_op.position, "", delete_op.length + len(insert_op.content))
            return insert_op, delete_op_prime
    
    def _transform_delete_delete(self, op1: Operation, op2: Operation) -> Tuple[Operation, Operation]:
        """Transform two concurrent delete operations."""
        # Case 1: No overlap
        if op1.position + op1.length <= op2.position:
            # op1 comes entirely before op2
            op2_prime = Operation('delete', op2.position - op1.length, "", op2.length)
            return op1, op2_prime
        elif op2.position + op2.length <= op1.position:
            # op2 comes entirely before op1
            op1_prime = Operation('delete', op1.position - op2.length, "", op1.length)
            return op1_prime, op2
        
        # Case 2: Overlap - merge the deletions
        start = min(op1.position, op2.position)
        end = max(op1.position + op1.length, op2.position + op2.length)
        merged_length = end - start
        
        # Create merged delete operation
        merged_op = Operation('delete', start, "", merged_length)
        
        # Return the merged operation and a no-op
        no_op = Operation('insert', start, "")  # Effectively a no-op
        
        if op1.position <= op2.position:
            return merged_op, no_op
        else:
            return no_op, merged_op
    
    def _transform_with_replace(self, op1: Operation, op2: Operation) -> Tuple[Operation, Operation]:
        """Transform operations involving replace (complex case)."""
        # Simplify: convert replace to delete + insert sequence
        if op1.type == 'replace':
            delete_op1 = Operation('delete', op1.position, "", op1.length)
            insert_op1 = Operation('insert', op1.position, op1.content)
            
            # Transform both parts against op2
            if op2.type == 'replace':
                # Both are replace operations - handle as separate delete/insert pairs
                delete_op2 = Operation('delete', op2.position, "", op2.length)
                insert_op2 = Operation('insert', op2.position, op2.content)
                
                # Transform the delete operations
                delete_op1_prime, delete_op2_prime = self._transform_delete_delete(delete_op1, delete_op2)
                
                # Transform the insert operations
                insert_op1_prime, insert_op2_prime = self._transform_insert_insert(insert_op1, insert_op2)
                
                # Combine back into replace operations
                op1_prime = Operation('replace', delete_op1_prime.position, insert_op1_prime.content, delete_op1_prime.length)
                op2_prime = Operation('replace', delete_op2_prime.position, insert_op2_prime.content, delete_op2_prime.length)
                
                return op1_prime, op2_prime
            else:
                # op1 is replace, op2 is insert/delete
                delete_op1_prime, op2_prime = self.transform_operations(delete_op1, op2)
                insert_op1_prime, _ = self.transform_operations(insert_op1, op2_prime)
                
                op1_prime = Operation('replace', delete_op1_prime.position, insert_op1_prime.content, delete_op1_prime.length)
                return op1_prime, op2_prime
        else:
            # op2 is replace, op1 is insert/delete
            op2_prime, op1_prime = self._transform_with_replace(op2, op1)
            return op1_prime, op2_prime
    
    def apply_operation(self, document: str, operation: Operation) -> str:
        """Apply an operation to a document string."""
        if operation.type == 'insert':
            return document[:operation.position] + operation.content + document[operation.position:]
        elif operation.type == 'delete':
            end_pos = operation.position + operation.length
            return document[:operation.position] + document[end_pos:]
        elif operation.type == 'replace':
            end_pos = operation.position + operation.length
            return document[:operation.position] + operation.content + document[end_pos:]
        else:
            return document
    
    def compose_operations(self, op1: Operation, op2: Operation) -> Operation:
        """
        Compose two sequential operations into a single operation.
        Used for optimization and reducing operation history.
        """
        # Simple composition cases
        if op1.type == 'insert' and op2.type == 'insert':
            if op2.position == op1.position + len(op1.content):
                # Sequential inserts at adjacent positions
                return Operation('insert', op1.position, op1.content + op2.content)
        
        elif op1.type == 'delete' and op2.type == 'delete':
            if op2.position == op1.position:
                # Sequential deletes at same position
                return Operation('delete', op1.position, "", op1.length + op2.length)
        
        # For complex cases, return the operations as-is
        # In practice, you might want more sophisticated composition
        return None
    
    def validate_operation(self, document: str, operation: Operation) -> bool:
        """Validate that an operation can be safely applied to a document."""
        doc_length = len(document)
        
        if operation.type == 'insert':
            return 0 <= operation.position <= doc_length
        elif operation.type == 'delete':
            return (0 <= operation.position < doc_length and 
                   operation.position + operation.length <= doc_length)
        elif operation.type == 'replace':
            return (0 <= operation.position < doc_length and 
                   operation.position + operation.length <= doc_length)
        
        return False
    
    def generate_inverse_operation(self, document: str, operation: Operation) -> Operation:
        """Generate the inverse operation for undo functionality."""
        if operation.type == 'insert':
            return Operation('delete', operation.position, "", len(operation.content))
        elif operation.type == 'delete':
            deleted_content = document[operation.position:operation.position + operation.length]
            return Operation('insert', operation.position, deleted_content)
        elif operation.type == 'replace':
            original_content = document[operation.position:operation.position + operation.length]
            return Operation('replace', operation.position, original_content, len(operation.content))
        
        return operation


class CollaborativeTextEditor:
    """
    High-level interface for collaborative text editing with operational transforms.
    """
    
    def __init__(self, initial_content: str = ""):
        self.content = initial_content
        self.ot = OperationalTransform()
        self.operation_history = []
        self.pending_operations = {}  # User ID -> list of pending operations
    
    def apply_local_operation(self, user_id: str, operation: Operation) -> bool:
        """Apply a local operation and prepare it for broadcasting."""
        if not self.ot.validate_operation(self.content, operation):
            return False
        
        # Apply operation locally
        self.content = self.ot.apply_operation(self.content, operation)
        self.operation_history.append((user_id, operation))
        
        return True
    
    def apply_remote_operation(self, user_id: str, operation: Operation) -> Tuple[bool, Operation]:
        """Apply a remote operation, transforming it against local operations."""
        if not self.ot.validate_operation(self.content, operation):
            return False, operation
        
        # Transform against all pending local operations
        transformed_op = operation
        
        # Simple transformation - in practice, you'd want more sophisticated tracking
        for local_user_id, local_op in reversed(self.operation_history[-10:]):  # Last 10 operations
            if local_user_id != user_id:
                transformed_op, _ = self.ot.transform_operations(transformed_op, local_op)
        
        # Apply the transformed operation
        if self.ot.validate_operation(self.content, transformed_op):
            self.content = self.ot.apply_operation(self.content, transformed_op)
            self.operation_history.append((user_id, transformed_op))
            return True, transformed_op
        
        return False, operation
    
    def get_content(self) -> str:
        """Get current document content."""
        return self.content
    
    def get_operation_count(self) -> int:
        """Get total number of operations applied."""
        return len(self.operation_history)
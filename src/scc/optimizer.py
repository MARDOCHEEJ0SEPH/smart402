"""
Storage Optimizer for Smart Contracts
"""

from typing import Dict, List


class StorageOptimizer:
    """
    Optimize storage layout for gas efficiency

    Storage cost model:
    SSTORE(key, value) = 20,000 if new slot
                       = 2,900 if update
                       = 4,800 if delete
    """

    def __init__(self):
        """Initialize optimizer"""
        pass

    def optimize_layout(self, variables: List[Dict]) -> Dict:
        """
        Generate optimized storage layout

        Args:
            variables: State variables

        Returns:
            Optimized layout
        """
        # Sort by size (descending) for better packing
        sorted_vars = sorted(
            variables,
            key=lambda v: self._get_size(v.get('type', 'uint256')),
            reverse=True
        )

        layout = []
        slot = 0
        slot_used = 0

        for var in sorted_vars:
            var_size = self._get_size(var.get('type', 'uint256'))

            if slot_used + var_size <= 256:
                layout.append({
                    'name': var['name'],
                    'slot': slot,
                    'offset': slot_used,
                    'size': var_size
                })
                slot_used += var_size
            else:
                slot += 1
                slot_used = var_size
                layout.append({
                    'name': var['name'],
                    'slot': slot,
                    'offset': 0,
                    'size': var_size
                })

        efficiency = sum(v['size'] for v in layout) / ((slot + 1) * 256)

        return {
            'layout': layout,
            'efficiency': efficiency,
            'slots_used': slot + 1
        }

    def _get_size(self, type_name: str) -> int:
        """Get size of type in bits"""
        if 'uint' in type_name or 'int' in type_name:
            # Extract size from uint256, int128, etc.
            try:
                return int(''.join(filter(str.isdigit, type_name)) or '256')
            except:
                return 256
        elif type_name == 'address':
            return 160
        elif type_name == 'bool':
            return 8
        return 256

"""Contract export utilities"""
import yaml
import json

async def export_contract(ucl, format='yaml'):
    """Export contract to format"""
    if format == 'yaml':
        return yaml.dump(ucl)
    elif format == 'json':
        return json.dumps(ucl, indent=2)
    return str(ucl)

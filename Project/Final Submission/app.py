"""
IP Calculator for Subnet Design
Flask Backend — app.py
Areeba Hasnain (23K-00059) & Emman Abrar (23K-0051)
"""

from flask import Flask, render_template, request, jsonify
import math

app = Flask(__name__)


# ─── IP Utility Functions ────────────────────────────────────────────────────

def ip_to_int(ip: str) -> int:
    """Convert dotted-decimal IP string to 32-bit integer."""
    parts = list(map(int, ip.split('.')))
    return (parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]


def int_to_ip(n: int) -> str:
    """Convert 32-bit integer to dotted-decimal IP string."""
    n = n & 0xFFFFFFFF
    return f"{(n >> 24) & 255}.{(n >> 16) & 255}.{(n >> 8) & 255}.{n & 255}"


def prefix_to_mask(prefix: int) -> int:
    """Convert CIDR prefix length to 32-bit subnet mask integer."""
    if prefix == 0:
        return 0
    return (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF


def mask_to_prefix(mask_int: int) -> int:
    """Convert subnet mask integer to prefix length."""
    return bin(mask_int).count('1')


def to_binary(n: int, bits: int = 8) -> str:
    """Convert integer to zero-padded binary string."""
    return format(n, f'0{bits}b')


def ip_to_binary(ip: str) -> str:
    """Convert IP to dotted binary string."""
    parts = list(map(int, ip.split('.')))
    return '.'.join(format(p, '08b') for p in parts)


def validate_ip(ip: str) -> bool:
    """Validate an IPv4 address string."""
    parts = ip.strip().split('.')
    if len(parts) != 4:
        return False
    try:
        return all(0 <= int(p) <= 255 for p in parts)
    except ValueError:
        return False


def parse_cidr(cidr: str) -> int:
    """Parse CIDR notation — accepts '/24', '24', '/255.255.255.0'."""
    cidr = cidr.strip()
    if cidr.startswith('/'):
        cidr = cidr[1:]
    # Could be a dotted mask like 255.255.255.0
    if '.' in cidr:
        try:
            mask_int = ip_to_int(cidr)
            return mask_to_prefix(mask_int)
        except Exception:
            raise ValueError("Invalid subnet mask format")
    try:
        prefix = int(cidr)
        if not 0 <= prefix <= 32:
            raise ValueError("Prefix must be between 0 and 32")
        return prefix
    except ValueError:
        raise ValueError("Invalid CIDR / prefix notation")


def get_ip_class(ip: str) -> dict:
    """Determine IP address class and default prefix."""
    first = int(ip.split('.')[0])
    if first == 0:
        return {'class': 'Special', 'default_prefix': 8,  'range': '0.x.x.x — This network'}
    if first < 128:
        return {'class': 'A', 'default_prefix': 8,  'range': '1.0.0.0 – 126.255.255.255'}
    if first == 127:
        return {'class': 'Special', 'default_prefix': 8,  'range': '127.x.x.x — Loopback'}
    if first < 192:
        return {'class': 'B', 'default_prefix': 16, 'range': '128.0.0.0 – 191.255.255.255'}
    if first < 224:
        return {'class': 'C', 'default_prefix': 24, 'range': '192.0.0.0 – 223.255.255.255'}
    if first < 240:
        return {'class': 'D', 'default_prefix': 32, 'range': '224.0.0.0 – 239.255.255.255(Multicast)'}
    return    {'class': 'E', 'default_prefix': 32, 'range': '240.0.0.0 – 255.255.255.255 (Experimental)'}


def is_private(ip: str) -> bool:
    """Check if IP is in RFC 1918 private address space."""
    parts = list(map(int, ip.split('.')))
    a, b = parts[0], parts[1]
    if a == 10:
        return True
    if a == 172 and 16 <= b <= 31:
        return True
    if a == 192 and b == 168:
        return True
    return False


def subnet_info(ip: str, prefix: int) -> dict:
    """Compute full subnet information for a given IP and prefix."""
    ip_int  = ip_to_int(ip)
    mask    = prefix_to_mask(prefix)
    net_int = ip_int & mask
    bcast   = net_int | (~mask & 0xFFFFFFFF)

    total_hosts = 2 ** (32 - prefix)
    usable      = max(0, total_hosts - 2) if prefix <= 30 else 0

    first_host = int_to_ip(net_int + 1) if prefix <= 30 else int_to_ip(net_int)
    last_host  = int_to_ip(bcast  - 1) if prefix <= 30 else int_to_ip(bcast)

    cls_info   = get_ip_class(ip)
    default_pfx = cls_info['default_prefix']
    subnets     = 2 ** max(0, prefix - default_pfx)

    # Binary breakdown with network/host split
    ip_bin  = ip_to_binary(ip)
    net_bin = ip_to_binary(int_to_ip(net_int))
    msk_bin = ip_to_binary(int_to_ip(mask))
    bct_bin = ip_to_binary(int_to_ip(bcast))

    return {
        'ip_address':      ip,
        'network_address': int_to_ip(net_int),
        'broadcast':       int_to_ip(bcast),
        'subnet_mask':     int_to_ip(mask),
        'prefix':          prefix,
        'cidr':            f'/{prefix}',
        'first_host':      first_host,
        'last_host':       last_host,
        'usable_hosts':    usable,
        'total_addresses': total_hosts,
        'subnets_from_default': subnets,
        'ip_class':        cls_info['class'],
        'class_range':     cls_info['range'],
        'is_private':      is_private(ip),
        'binary': {
            'ip':        ip_bin,
            'network':   net_bin,
            'mask':      msk_bin,
            'broadcast': bct_bin,
            'prefix':    prefix,
        }
    }


# ─── FLSM ────────────────────────────────────────────────────────────────────

def calc_flsm(ip: str, prefix: int, num_subnets: int) -> dict:
    """
    Fixed-Length Subnet Masking.
    Divides a network into `num_subnets` equal-sized subnets.
    """
    bits_needed = math.ceil(math.log2(max(num_subnets, 1)))
    new_prefix  = prefix + bits_needed

    if new_prefix > 30:
        raise ValueError(
            f"Cannot create {num_subnets} subnets — new prefix /{new_prefix} "
            "is too long (max /30 for usable subnets)."
        )

    total_subnets   = 2 ** bits_needed
    host_bits       = 32 - new_prefix
    hosts_per_subnet = max(0, 2 ** host_bits - 2)
    block_size      = 2 ** host_bits

    mask_int = prefix_to_mask(prefix)
    base_int = ip_to_int(ip) & mask_int

    subnets = []
    for i in range(total_subnets):
        net_int = (base_int + i * block_size) & 0xFFFFFFFF
        s = subnet_info(int_to_ip(net_int), new_prefix)
        s['subnet_index'] = i
        s['subnet_name']  = f'Subnet {i}'
        subnets.append(s)

    cls_info = get_ip_class(ip)

    return {
        'original_network': f'{int_to_ip(base_int)}/{prefix}',
        'new_prefix':        new_prefix,
        'new_mask':          int_to_ip(prefix_to_mask(new_prefix)),
        'bits_borrowed':     bits_needed,
        'total_subnets':     total_subnets,
        'hosts_per_subnet':  hosts_per_subnet,
        'block_size':        block_size,
        'ip_class':          cls_info['class'],
        'is_private':        is_private(ip),
        'subnets':           subnets,
    }


# ─── VLSM ────────────────────────────────────────────────────────────────────

def calc_vlsm(ip: str, prefix: int, subnet_requests: list) -> dict:
    """
    Variable-Length Subnet Masking.
    Allocates subnets of different sizes from a parent network.
    subnet_requests: list of {'name': str, 'hosts': int}
    """
    if not subnet_requests:
        raise ValueError("Provide at least one subnet requirement.")

    # Sort by required hosts descending (best-fit allocation)
    sorted_reqs = sorted(subnet_requests, key=lambda x: x['hosts'], reverse=True)

    total_space = 2 ** (32 - prefix)
    mask_int    = prefix_to_mask(prefix)
    base_int    = ip_to_int(ip) & mask_int
    end_int     = (base_int + total_space) & 0xFFFFFFFF

    current_int = base_int
    allocated   = []

    for req in sorted_reqs:
        needed_hosts = req['hosts']
        if needed_hosts < 1:
            raise ValueError(f"Subnet '{req['name']}' must require at least 1 host.")

        # Minimum host bits to fit needed_hosts + network + broadcast
        host_bits = math.ceil(math.log2(needed_hosts + 2))
        if host_bits < 2:
            host_bits = 2
        new_pfx  = 32 - host_bits
        if new_pfx < prefix:
            raise ValueError(
                f"Subnet '{req['name']}' requires /{new_pfx} which is "
                f"larger than the parent /{prefix} network."
            )

        block_size = 2 ** host_bits

        # Align current pointer to block boundary
        if current_int % block_size != 0:
            current_int = ((current_int // block_size) + 1) * block_size

        if (current_int + block_size) > end_int:
            raise ValueError(
                f"Not enough address space in /{prefix} to allocate "
                f"subnet '{req['name']}' ({needed_hosts} hosts). "
                "Reduce requirements or use a larger parent network."
            )

        s = subnet_info(int_to_ip(current_int), new_pfx)
        s['subnet_name']     = req['name']
        s['hosts_required']  = needed_hosts
        s['hosts_available'] = s['usable_hosts']
        s['block_size']      = block_size
        allocated.append(s)

        current_int = (current_int + block_size) & 0xFFFFFFFF

    used_ips  = sum(s['block_size'] for s in allocated)
    free_ips  = total_space - used_ips
    cls_info  = get_ip_class(ip)

    return {
        'base_network':   f'{int_to_ip(base_int)}/{prefix}',
        'total_addresses': total_space,
        'used_addresses':  used_ips,
        'free_addresses':  free_ips,
        'subnets_count':   len(allocated),
        'ip_class':        cls_info['class'],
        'is_private':      is_private(ip),
        'subnets':         allocated,
    }


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/basic', methods=['POST'])
def api_basic():
    data = request.get_json()
    try:
        ip     = data.get('ip', '').strip()
        cidr   = data.get('cidr', '').strip()
        if not validate_ip(ip):
            return jsonify({'error': 'Invalid IP address. Use dotted-decimal format e.g. 192.168.1.0'}), 400
        prefix = parse_cidr(cidr)
        result = subnet_info(ip, prefix)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/flsm', methods=['POST'])
def api_flsm():
    data = request.get_json()
    try:
        ip          = data.get('ip', '').strip()
        cidr        = data.get('cidr', '').strip()
        num_subnets = int(data.get('num_subnets', 0))
        if not validate_ip(ip):
            return jsonify({'error': 'Invalid IP address.'}), 400
        if num_subnets < 1:
            return jsonify({'error': 'Number of subnets must be at least 1.'}), 400
        prefix = parse_cidr(cidr)
        result = calc_flsm(ip, prefix, num_subnets)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/api/vlsm', methods=['POST'])
def api_vlsm():
    data = request.get_json()
    try:
        ip       = data.get('ip', '').strip()
        cidr     = data.get('cidr', '').strip()
        requests_list = data.get('subnets', [])
        if not validate_ip(ip):
            return jsonify({'error': 'Invalid IP address.'}), 400
        if not requests_list:
            return jsonify({'error': 'Provide at least one subnet requirement.'}), 400
        prefix = parse_cidr(cidr)
        result = calc_vlsm(ip, prefix, requests_list)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == '__main__':
    app.run(debug=True)

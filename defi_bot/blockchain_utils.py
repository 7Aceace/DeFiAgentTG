import os
import logging
import requests
from web3 import Web3
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Web3 connection
def get_web3():
    """Get a Web3 connection to Ethereum."""
    eth_rpc_url = os.getenv('ETH_RPC_URL')
    if not eth_rpc_url:
        # Use a public RPC endpoint if none is provided
        eth_rpc_url = "https://eth.llamarpc.com"
    
    return Web3(Web3.HTTPProvider(eth_rpc_url))

# Gas price functions
def get_gas_prices():
    """Get current gas prices from Etherscan API."""
    api_key = os.getenv('ETHERSCAN_API_KEY', '')
    gas_api_url = os.getenv('GAS_API_URL', 'https://api.etherscan.io/api?module=gastracker&action=gasoracle')
    
    if api_key:
        gas_api_url += f"&apikey={api_key}"
    
    try:
        response = requests.get(gas_api_url)
        data = response.json()
        
        if data['status'] == '1':
            result = data['result']
            return {
                'slow': int(result['SafeGasPrice']),
                'average': int(result['ProposeGasPrice']),
                'fast': int(result['FastGasPrice'])
            }
        else:
            # Fallback to default values if API fails
            return {'slow': 30, 'average': 45, 'fast': 60}
    except Exception as e:
        logger.error(f"Failed to get gas prices: {e}")
        # Fallback to default values
        return {'slow': 30, 'average': 45, 'fast': 60}

def estimate_transaction_cost(gas_limit, gas_price_gwei):
    """Estimate transaction cost in ETH and USD."""
    web3 = get_web3()
    
    # Convert gas price from Gwei to Wei
    gas_price_wei = web3.to_wei(gas_price_gwei, 'gwei')
    
    # Calculate cost in Wei
    cost_wei = gas_limit * gas_price_wei
    
    # Convert to ETH
    cost_eth = web3.from_wei(cost_wei, 'ether')
    
    # Get ETH price in USD (in a real implementation, this would use a price API)
    eth_price_usd = 3000  # Example price
    
    # Calculate cost in USD
    cost_usd = float(cost_eth) * eth_price_usd
    
    return {
        'eth': float(cost_eth),
        'usd': cost_usd
    }

# Security functions
def check_contract_security(contract_address):
    """Check the security of a smart contract."""
    if not Web3.is_address(contract_address):
        return {
            'valid': False,
            'message': 'Invalid Ethereum address format'
        }
    
    web3 = get_web3()
    etherscan_api_key = os.getenv('ETHERSCAN_API_KEY', '')
    
    # Check if contract exists
    code = web3.eth.get_code(Web3.to_checksum_address(contract_address))
    if code == '0x':
        return {
            'valid': False,
            'message': 'This is not a contract address'
        }
    
    # In a real implementation, this would perform more thorough checks:
    # 1. Check if contract is verified on Etherscan
    # 2. Look for known vulnerabilities
    # 3. Check contract age and usage statistics
    # 4. Run static analysis on the contract code
    
    # For this demo, we'll return a mock result
    return {
        'valid': True,
        'verified': True,
        'age_days': 120,
        'risk_score': 7,  # 1-10 scale, 10 being highest risk
        'issues': [
            'Medium risk: Contract is less than 6 months old',
            'Low risk: Uses standard ERC20 implementation'
        ],
        'usage': {
            'unique_addresses': 1500,
            'transaction_count': 8500
        }
    }

# Yield functions
def get_defi_yields():
    """Get current DeFi yield opportunities."""
    # In a real implementation, this would fetch data from DeFi APIs
    # For this demo, we'll return mock data
    
    return {
        'lending': [
            {'protocol': 'Aave', 'asset': 'USDC', 'apy': 4.2},
            {'protocol': 'Compound', 'asset': 'DAI', 'apy': 3.8},
            {'protocol': 'Euler', 'asset': 'USDT', 'apy': 5.1}
        ],
        'liquidity': [
            {'protocol': 'Uniswap', 'asset': 'ETH/USDC', 'apy': 15.2},
            {'protocol': 'Curve', 'asset': '3pool', 'apy': 8.7},
            {'protocol': 'Balancer', 'asset': 'BTC/ETH/USDC', 'apy': 12.3}
        ],
        'staking': [
            {'protocol': 'Ethereum', 'asset': 'ETH', 'apy': 4.0},
            {'protocol': 'Polygon', 'asset': 'MATIC', 'apy': 5.2},
            {'protocol': 'Avalanche', 'asset': 'AVAX', 'apy': 8.1}
        ],
        'farming': [
            {'protocol': 'Convex', 'asset': 'CRV', 'apy': 18.7},
            {'protocol': 'Yearn', 'asset': 'USDC', 'apy': 11.2},
            {'protocol': 'Harvest', 'asset': 'FARM', 'apy': 22.5}
        ]
    }

def estimate_next_claim_date(protocol, asset):
    """Estimate the next yield claim date for a given protocol and asset."""
    # In a real implementation, this would analyze the protocol's claim schedule
    # For this demo, we'll return mock data
    
    from datetime import datetime, timedelta
    
    # Map protocols to claim frequencies (in days)
    claim_frequencies = {
        'Aave': 7,
        'Compound': 3,
        'Uniswap': 14,
        'Curve': 7,
        'Yearn': 7,
        'Convex': 14,
        'Harvest': 7
    }
    
    # Get the claim frequency for the protocol (default to 7 days)
    frequency = claim_frequencies.get(protocol, 7)
    
    # Calculate the next claim date
    next_claim_date = datetime.now() + timedelta(days=frequency)
    
    return next_claim_date.strftime('%Y-%m-%d')

# Example usage
if __name__ == '__main__':
    # Test gas price function
    gas_prices = get_gas_prices()
    print(f"Current gas prices: {gas_prices}")
    
    # Test transaction cost estimation
    cost = estimate_transaction_cost(21000, gas_prices['average'])
    print(f"Estimated transaction cost: {cost['eth']} ETH (${cost['usd']:.2f})")
    
    # Test contract security check
    security = check_contract_security('0x6B175474E89094C44Da98b954EedeAC495271d0F')  # DAI address
    print(f"Contract security: {security}")
    
    # Test yield function
    yields = get_defi_yields()
    print(f"Top lending opportunity: {yields['lending'][0]}")
    
    # Test claim date estimation
    next_claim = estimate_next_claim_date('Compound', 'USDC')
    print(f"Next claim date for Compound USDC: {next_claim}")

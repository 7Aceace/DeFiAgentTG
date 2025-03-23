import os
import logging
from datetime import datetime
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

class DeFiGuard:
    """Security and compliance features for DeFi operations."""
    
    def __init__(self):
        self.etherscan_api_key = os.getenv('ETHERSCAN_API_KEY', '')
        self.web3 = self._get_web3()
    
    def _get_web3(self):
        """Get a Web3 connection to Ethereum."""
        eth_rpc_url = os.getenv('ETH_RPC_URL')
        if not eth_rpc_url:
            # Use a public RPC endpoint if none is provided
            eth_rpc_url = "https://eth.llamarpc.com"
        
        return Web3(Web3.HTTPProvider(eth_rpc_url))
    
    def verify_contract(self, contract_address):
        """Verify a smart contract's security."""
        if not Web3.is_address(contract_address):
            return {
                'valid': False,
                'message': 'Invalid Ethereum address format'
            }
        
        # Check if contract exists
        code = self.web3.eth.get_code(Web3.to_checksum_address(contract_address))
        if code == '0x':
            return {
                'valid': False,
                'message': 'This is not a contract address'
            }
        
        # Check if contract is verified on Etherscan
        if self.etherscan_api_key:
            try:
                url = f"https://api.etherscan.io/api?module=contract&action=getsourcecode&address={contract_address}&apikey={self.etherscan_api_key}"
                response = requests.get(url)
                data = response.json()
                
                if data['status'] == '1' and data['result'][0]['SourceCode'] != '':
                    verified = True
                else:
                    verified = False
            except Exception as e:
                logger.error(f"Error checking contract verification: {e}")
                verified = False
        else:
            verified = False
        
        # In a real implementation, this would perform more thorough checks:
        # 1. Look for known vulnerabilities
        # 2. Check contract age and usage statistics
        # 3. Run static analysis on the contract code
        
        # For this demo, we'll return a mock result
        return {
            'valid': True,
            'verified': verified,
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
    
    def simulate_transaction(self, from_address, to_address, value, data='0x'):
        """Simulate a transaction to check for potential issues."""
        try:
            # Convert addresses to checksum format
            from_address = Web3.to_checksum_address(from_address)
            to_address = Web3.to_checksum_address(to_address)
            
            # Convert value to Wei if it's in ETH
            if isinstance(value, float):
                value = self.web3.to_wei(value, 'ether')
            
            # Build transaction
            tx = {
                'from': from_address,
                'to': to_address,
                'value': value,
                'gas': 2000000,  # High gas limit for simulation
                'gasPrice': self.web3.to_wei('50', 'gwei'),
                'nonce': self.web3.eth.get_transaction_count(from_address),
                'data': data
            }
            
            # Call (simulate) the transaction
            result = self.web3.eth.call(tx)
            
            return {
                'success': True,
                'result': result.hex(),
                'warnings': []
            }
        except Exception as e:
            error_message = str(e)
            
            # Parse the error message to provide more user-friendly feedback
            if 'revert' in error_message.lower():
                reason = 'Transaction would revert'
                if 'message' in error_message:
                    reason += f": {error_message.split('message')[-1]}"
            elif 'gas' in error_message.lower():
                reason = 'Insufficient gas'
            else:
                reason = 'Unknown error'
            
            return {
                'success': False,
                'error': reason,
                'original_error': error_message
            }
    
    def check_phishing(self, url):
        """Check if a URL is a known phishing site."""
        # In a real implementation, this would check against phishing databases
        # For this demo, we'll return a mock result
        
        suspicious_domains = [
            'etherdelta.one',
            'myetherwallet.com.ru',
            'metamask.io.ph',
            'uniswap.org.io',
            'aave-app.com'
        ]
        
        for domain in suspicious_domains:
            if domain in url:
                return {
                    'is_phishing': True,
                    'confidence': 'high',
                    'reason': f'Domain {domain} is a known phishing site'
                }
        
        return {
            'is_phishing': False,
            'confidence': 'medium',
            'reason': 'No known phishing indicators found'
        }
    
    def check_approval_risks(self, token_address, spender_address):
        """Check risks associated with token approvals."""
        # In a real implementation, this would check the reputation of the spender
        # For this demo, we'll return a mock result
        
        known_safe_spenders = [
            '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',  # Uniswap V2 Router
            '0xE592427A0AEce92De3Edee1F18E0157C05861564',  # Uniswap V3 Router
            '0x3d9819210A31b4961b30EF54bE2aeD79B9c9Cd3B'   # Compound Comptroller
        ]
        
        if spender_address in known_safe_spenders:
            risk_level = 'low'
            recommendation = 'This is a well-known protocol contract'
        else:
            risk_level = 'medium'
            recommendation = 'Consider using a limited approval amount instead of unlimited'
        
        return {
            'risk_level': risk_level,
            'recommendation': recommendation,
            'unlimited_approval_risk': 'High - allows spender to transfer all tokens at any time'
        }

class GasWizard:
    """Transaction optimization features for DeFi operations."""
    
    def __init__(self):
        self.etherscan_api_key = os.getenv('ETHERSCAN_API_KEY', '')
        self.web3 = self._get_web3()
        self.gas_price_history = []
    
    def _get_web3(self):
        """Get a Web3 connection to Ethereum."""
        eth_rpc_url = os.getenv('ETH_RPC_URL')
        if not eth_rpc_url:
            # Use a public RPC endpoint if none is provided
            eth_rpc_url = "https://eth.llamarpc.com"
        
        return Web3(Web3.HTTPProvider(eth_rpc_url))
    
    def get_current_gas_prices(self):
        """Get current gas prices from Etherscan API."""
        gas_api_url = os.getenv('GAS_API_URL', 'https://api.etherscan.io/api?module=gastracker&action=gasoracle')
        
        if self.etherscan_api_key:
            gas_api_url += f"&apikey={self.etherscan_api_key}"
        
        try:
            response = requests.get(gas_api_url)
            data = response.json()
            
            if data['status'] == '1':
                result = data['result']
                gas_prices = {
                    'slow': int(result['SafeGasPrice']),
                    'average': int(result['ProposeGasPrice']),
                    'fast': int(result['FastGasPrice'])
                }
                
                # Store in history for analysis
                self.gas_price_history.append({
                    'timestamp': datetime.now(),
                    'prices': gas_prices
                })
                
                # Keep only the last 24 hours of data
                one_day_ago = datetime.now().timestamp() - (24 * 60 * 60)
                self.gas_price_history = [
                    entry for entry in self.gas_price_history 
                    if entry['timestamp'].timestamp() > one_day_ago
                ]
                
                return gas_prices
            else:
                # Fallback to default values if API fails
                return {'slow': 30, 'average': 45, 'fast': 60}
        except Exception as e:
            logger.error(f"Failed to get gas prices: {e}")
            # Fallback to default values
            return {'slow': 30, 'average': 45, 'fast': 60}
    
    def estimate_transaction_cost(self, gas_limit, gas_price_gwei):
        """Estimate transaction cost in ETH and USD."""
        # Convert gas price from Gwei to Wei
        gas_price_wei = self.web3.to_wei(gas_price_gwei, 'gwei')
        
        # Calculate cost in Wei
        cost_wei = gas_limit * gas_price_wei
        
        # Convert to ETH
        cost_eth = self.web3.from_wei(cost_wei, 'ether')
        
        # Get ETH price in USD (in a real implementation, this would use a price API)
        eth_price_usd = 3000  # Example price
        
        # Calculate cost in USD
        cost_usd = float(cost_eth) * eth_price_usd
        
        return {
            'eth': float(cost_eth),
            'usd': cost_usd
        }
    
    def predict_optimal_gas_time(self):
        """Predict the optimal time to send a transaction based on historical gas prices."""
        if not self.gas_price_history:
            return {
                'recommendation': 'Not enough data to make a prediction',
                'best_time': 'Unknown',
                'confidence': 'low'
            }
        
        # Analyze gas price patterns
        # In a real implementation, this would use more sophisticated analysis
        # For this demo, we'll use a simple approach
        
        # Group by hour of day
        hours = {}
        for entry in self.gas_price_history:
            hour = entry['timestamp'].hour
            if hour not in hours:
                hours[hour] = []
            hours[hour].append(entry['prices']['average'])
        
        # Find the hour with the lowest average gas price
        best_hour = min(hours.items(), key=lambda x: sum(x[1]) / len(x[1]))
        
        # Format as AM/PM
        if best_hour[0] == 0:
            best_time = '12 AM'
        elif best_hour[0] < 12:
            best_time = f'{best_hour[0]} AM'
        elif best_hour[0] == 12:
            best_time = '12 PM'
        else:
            best_time = f'{best_hour[0] - 12} PM'
        
        return {
            'recommendation': f'Based on historical data, gas prices are typically lowest around {best_time} UTC',
            'best_time': best_time,
            'confidence': 'medium' if len(self.gas_price_history) > 12 else 'low'
        }
    
    def suggest_batch_transactions(self, transactions):
        """Suggest how to batch multiple transactions to save gas."""
        if not transactions or len(transactions) < 2:
            return {
                'can_batch': False,
                'message': 'Need at least 2 transactions to batch'
            }
        
        # Group transactions by recipient
        recipients = {}
        for tx in transactions:
            if tx['to'] not in recipients:
                recipients[tx['to']] = []
            recipients[tx['to']].append(tx)
        
        # Find recipients with multiple transactions
        batchable = {addr: txs for addr, txs in recipients.items() if len(txs) > 1}
        
        if not batchable:
            return {
                'can_batch': False,
                'message': 'No transactions can be batched (different recipients)'
            }
        
        # Calculate potential savings
        total_gas = sum(tx.get('gas', 21000) for tx in transactions)
        
        # Estimate batched gas
        batched_gas = 0
        for addr, txs in batchable.items():
            # Base cost for one transaction
            batched_gas += 21000
            # Data cost for each function call
            batched_gas += sum(2000 for _ in txs)
        
        # Add gas for non-batchable transactions
        non_batchable_count = sum(1 for addr, txs in recipients.items() if len(txs) == 1)
        batched_gas += non_batchable_count * 21000
        
        # Calculate savings
        savings = total_gas - batched_gas
        savings_percentage = (savings / total_gas) * 100 if total_gas > 0 else 0
        
        return {
            'can_batch': True,
            'batchable_groups': len(batchable),
            'total_transactions': len(transactions),
            'batchable_transactions': sum(len(txs) for txs in batchable.values()),
            'estimated_gas_savings': savings,
            'savings_percentage': savings_percentage,
            'message': f'You can batch {sum(len(txs) for txs in batchable.values())} transactions, saving approximately {savings_percentage:.1f}% in gas'
        }
    
    def recommend_gas_strategy(self, transaction_urgency='normal'):
        """Recommend a gas price strategy based on current conditions and transaction urgency."""
        gas_prices = self.get_current_gas_prices()
        
        if transaction_urgency == 'high':
            recommended_price = gas_prices['fast']
            message = 'Using fast gas price for urgent transaction'
        elif transaction_urgency == 'low':
            recommended_price = gas_prices['slow']
            message = 'Using slow gas price to minimize costs'
        else:  # normal
            recommended_price = gas_prices['average']
            message = 'Using average gas price for standard transaction'
        
        # Check if current prices are unusually high
        if gas_prices['average'] > 100:  # Arbitrary threshold
            warning = 'Gas prices are unusually high right now. Consider waiting if possible.'
        else:
            warning = None
        
        # Get optimal time prediction
        optimal_time = self.predict_optimal_gas_time()
        
        return {
            'recommended_gas_price': recommended_price,
            'message': message,
            'warning': warning,
            'optimal_time': optimal_time['recommendation'] if optimal_time else None
        }

class YieldSense:
    """Portfolio management and yield optimization features for DeFi operations."""
    
    def __init__(self):
        self.web3 = self._get_web3()
    
    def _get_web3(self):
        """Get a Web3 connection to Ethereum."""
        eth_rpc_url = os.getenv('ETH_RPC_URL')
        if not eth_rpc_url:
            # Use a public RPC endpoint if none is provided
            eth_rpc_url = "https://eth.llamarpc.com"
        
        return Web3(Web3.HTTPProvider(eth_rpc_url))
    
    def get_defi_yields(self):
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
    
    def estimate_next_claim_date(self, protocol, asset):
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
    
    def calculate_impermanent_loss(self, initial_prices, current_prices, liquidity_ratio=0.5):
        """Calculate impermanent loss for a liquidity position."""
        # Formula: IL = 2 * sqrt(price_ratio) / (1 + price_ratio) - 1
        
        if len(initial_prices) != len(current_prices):
            return {
                'error': 'Price arrays must have the same length'
            }
        
        price_ratios = [current / initial for initial, current in zip(initial_prices, current_prices)]
        
        # For a 50/50 pool (most common)
        if len(price_ratios) == 2 and liquidity_ratio == 0.5:
            price_ratio = price_ratios[1] / price_ratios[0]
            il = 2 * (price_ratio ** 0.5) / (1 + price_ratio) - 1
            il_percentage = il * 100
            
            return {
                'impermanent_loss': il,
                'impermanent_loss_percentage': il_percentage,
                'hodl_value': sum(initial * current / initial for initial, current in zip(initial_prices, current_prices)),
                'pool_value': 2 * (price_ratio ** 0.5) / (1 + price_ratio) * sum(initial_prices)
            }
        else:
            # For more complex pools, this would require more sophisticated calculations
            return {
                'error': 'Complex pool calculations not supported in this demo'
            }
    
    def optimize_yield_strategy(self, risk_tolerance='medium', investment_amount=10000):
        """Optimize yield strategy based on risk tolerance and investment amount."""
        yields = self.get_defi_yields()
        
        # Filter and sort opportunities based on risk tolerance
        if risk_tolerance == 'low':
            # For low risk, focus on lending and staking
            opportunities = yields['lending'] + yields['staking']
            # Sort by APY
            opportunities.sort(key=lambda x: x['apy'])
            # Take top 3
            selected = opportunities[:3]
            allocation = [0.4, 0.3, 0.3]  # 40%, 30%, 30%
        elif risk_tolerance == 'high':
            # For high risk, focus on farming and liquidity
            opportunities = yields['farming'] + yields['liquidity']
            # Sort by APY (descending)
            opportunities.sort(key=lambda x: x['apy'], reverse=True)
            # Take top 3
            selected = opportunities[:3]
            allocation = [0.5, 0.3, 0.2]  # 50%, 30%, 20%
        else:  # medium
            # For medium risk, mix of all types
            opportunities = []
            for category in yields.values():
                # Take the highest APY from each category
                category_sorted = sorted(category, key=lambda x: x['apy'], reverse=True)
                if category_sorted:
                    opportunities.append(category_sorted[0])
            # Sort by APY (descending)
            opportunities.sort(key=lambda x: x['apy'], reverse=True)
            # Take top 3
            selected = opportunities[:3]
            allocation = [0.4, 0.4, 0.2]  # 40%, 40%, 20%
        
        # Calculate allocations
        strategy = []
        for i, opportunity in enumerate(selected):
            amount = investment_amount * allocation[i]
            expected_yield = amount * opportunity['apy'] / 100
            strategy.append({
                'protocol': opportunity['protocol'],
                'asset': opportunity['asset'],
                'amount': amount,
                'percentage': allocation[i] * 100,
                'apy': opportunity['apy'],
                'expected_annual_yield': expected_yield
            })
        
        return {
            'risk_tolerance': risk_tolerance,
            'total_investment': investment_amount,
            'expected_annual_yield': sum(s['expected_annual_yield'] for s in strategy),
            'expected_apy': sum(s['expected_annual_yield'] for s in strategy) / investment_amount * 100,
            'strategy': strategy
        }
    
    def analyze_portfolio_performance(self, positions):
        """Analyze the performance of a DeFi portfolio."""
        if not positions:
            return {
                'error': 'No positions provided'
            }
        
        total_value = sum(position.get('current_value', 0) for position in positions)
        total_invested = sum(position.get('invested_value', 0) for position in positions)
        
        if total_invested == 0:
            return {
                'error': 'No investment value provided'
            }
        
        total_return = total_value - total_invested
        total_return_percentage = (total_return / total_invested) * 100
        
        # Calculate weighted average APY
        weighted_apy = sum(position.get('apy', 0) * position.get('current_value', 0) for position in positions) / total_value if total_value > 0 else 0
        
        # Analyze by category
        categories = {}
        for position in positions:
            category = position.get('category', 'unknown')
            if category not in categories:
                categories[category] = {
                    'value': 0,
                    'invested': 0,
                    'return': 0
                }
            categories[category]['value'] += position.get('current_value', 0)
            categories[category]['invested'] += position.get('invested_value', 0)
            categories[category]['return'] += position.get('current_value', 0) - position.get('invested_value', 0)
        
        # Calculate category percentages
        for category in categories:
            categories[category]['percentage'] = (categories[category]['value'] / total_value) * 100 if total_value > 0 else 0
            categories[category]['return_percentage'] = (categories[category]['return'] / categories[category]['invested']) * 100 if categories[category]['invested'] > 0 else 0
        
        return {
            'total_value': total_value,
            'total_invested': total_invested,
            'total_return': total_return,
            'total_return_percentage': total_return_percentage,
            'weighted_apy': weighted_apy,
            'categories': categories,
            'position_count': len(positions)
        }

# Example usage
if __name__ == '__main__':
    # Test DeFiGuard
    defi_guard = DeFiGuard()
    contract_security = defi_guard.verify_contract('0x6B175474E89094C44Da98b954EedeAC495271d0F')  # DAI address
    print(f"Contract security: {contract_security}")
    
    # Test GasWizard
    gas_wizard = GasWizard()
    gas_prices = gas_wizard.get_current_gas_prices()
    print(f"Current gas prices: {gas_prices}")
    
    # Test YieldSense
    yield_sense = YieldSense()
    yields = yield_sense.get_defi_yields()
    print(f"Top lending opportunity: {yields['lending'][0]}")
    
    # Test yield optimization
    strategy = yield_sense.optimize_yield_strategy()
    print(f"Recommended strategy: {strategy}")

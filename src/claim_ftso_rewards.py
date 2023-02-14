#!/usr/bin/env python

import os
import yaml
import json

from web3 import Web3, HTTPProvider
from web3.middleware import geth_poa_middleware

import argparse

from enum import Enum


from rich import print
from rich import box
from rich.traceback import install
from rich.panel import Panel
from rich.pretty import pprint

from attributedict.collections import AttributeDict

install(show_locals=False)

from base_logger import log

from network.songbird import *
from network.flare import *


def init_argparse() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog = 'claim_ftso_rewards.py',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        usage="""
        %(prog)s --network flare | songbird [OPTION] ...
        """,
        description="Flare FTSO Rewards - Check and Claim",
        epilog = """

Written by Dustin Lee [FTSO Express]

If you like it, send some VP My Way

FLR: 0xc0452CEcee694Ab416d19E95a0907f022DEC5664
SGB: 0x33ddae234e403789954cd792e1febdbe2466adc2
---
""",
        # add_help=True
    )

    parser.add_argument(
        "-V", "--version", action="version",
        version = f"{parser.prog} version 1.0.0"
    )

    parser.add_argument(
        "-c", "--claim", action='store_true',
        help='If you want to claim an amount'
    )

    parser.add_argument(
        "-r", "--rewards", action='store',
        help='Amount of Rewards you want to claim'
    )

    parser.add_argument(
        '--verbose', '-v', action='count', 
        default=0,
        help='Enable Logs Increase Verbosity, with -vvv'
    )

    # parser.add_argument(
    #     "-l", "--log", action='store',
    #     # default='INFO',
    #     default='ERROR',
    #     # required=True,
    #     choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
    #     help='Which Network to Claim On'
    # )

    parser.add_argument(
        "-n", "--network", action='store',
        # default='flare',
        required=True,
        choices=['flare', 'songbird'],
        help='Which Network to Claim On'
    )

    # parser.add_argument(
    #     "-h", "--help", action='help',
    #     help='Amount of Rewards you want to claim'
    # )

    return parser

def get_ftso_wallet_balance(web3: Web3, _ftso_account) -> (int, float):
    _ftso_balance_wei = web3.eth.get_balance(_ftso_account.address)
    _ftso_balance = web3.fromWei(_ftso_balance_wei,'ether')
    log.debug(f"FTSO Balance: {_ftso_balance} [{_ftso_balance_wei}]")
    return (_ftso_balance_wei, _ftso_balance)

def get_total_ftso_rewards_balance(web3: Web3, _CONTRACT_FTSO_REWARD_MANAGER) -> (int, float):
    # Check How much it has to make sure it's not dry
    _contract_total_ftso_reward_manager_balance_wei = web3.eth.get_balance(_CONTRACT_FTSO_REWARD_MANAGER['address'])
    _contract_total_ftso_reward_manager_balance = web3.fromWei(_contract_total_ftso_reward_manager_balance_wei,'ether')
    log.debug(f"FTSO Reward Manager Balance: {_contract_total_ftso_reward_manager_balance} [{_contract_total_ftso_reward_manager_balance_wei}]")
    return (_contract_total_ftso_reward_manager_balance_wei, _contract_total_ftso_reward_manager_balance)



# function claim(address _rewardOwner, address payable _recipient, uint256 _rewardAmount, bool _wrap) external;
# def claim_ftso_reward( web3: Web3, _ftso_account, _contract_ftso_reward_manager,
#     _rewardOwner = cfg['rewards']['claim']['_rewardOwner'],
#     _recipient = cfg['rewards']['claim']['_recipient'],
#     _rewardAmount = cfg['rewards']['claim']['_rewardAmount'], 
#     _wrap = cfg['rewards']['claim']['_wrap']):
    
#     try:
#         nonce = web3.eth.getTransactionCount(_ftso_account.address)
#         log.debug(f"NONCE: {nonce}")
#     except Exception as error:
#         log.exception(f"Claim [GET_NONCE] : {error}")

#     try:        
#         _submission_txn = _contract_ftso_reward_manager.functions.claim(
#                 _rewardOwner, _recipient, _rewardAmount, _wrap
#             ).buildTransaction(
#                 {'nonce': nonce, 'gas': GAS_LIMIT,'gasPrice': web3.toWei(GAS_PRICE, 'gwei')}
#             )
#         log.debug(f"submission_txn: {_submission_txn}")
#     except Exception as error:
#         log.exception(f"Claim [SUBMISSION_TXN] : {error}")
    
#     try:
#         _signed_txn = web3.eth.account.signTransaction(_submission_txn, VALIDATOR_PRIVATE_KEY)
#         log.debug(f"signed_txn",{_signed_txn})
#     except Exception as error:
#         log.exception(f"Claim [SIGNED_TXN] : {error}")


#     try:
#         _txn_id = web3.toHex(web3.eth.sendRawTransaction(_signed_txn.rawTransaction))
#         log.debug(f"TX ID: {_txn_id}")
#     except Exception as error:
#         log.exception(f"Claim [SEND TX] : {error}")

#     try:
#         # Wait for Receipt
#         _txn_receipt = web3.eth.waitForTransactionReceipt(_txn_id,timeout=240)
#         log.debug(f"TX RCPT: {_txn_receipt}")
#     except Exception as error:
#         log.exception(f"Claim [TX RECEIPT] : {error}")
    
#     return (_txn_id, _txn_receipt)



def main() -> None:
    
    parser = init_argparse()
    args = parser.parse_args()

    log_levels = [ "WARNING", "INFO", "DEBUG" ]

    if args.verbose:
        log.propagate = True
        if args.verbose <= len(log_levels):
            log.setLevel(log_levels[args.verbose-1])
        else:
            log.setLevel(len(log_levels)-1)

    print(Panel.fit("[bold yellow]FTSO Express - FTSO Reward Checker/Claimer", border_style="blue", box=box.DOUBLE))

    with open("config.yml", 'r') as ymlfile:
        cfg = yaml.safe_load(ymlfile)

    if args.network:
        log.info(f"Network Selected: {args.network}")

    _network_selected = str(args.network)
    if _network_selected.upper() == "FLARE":
        print(Panel.fit(f"[bold green] {_network_selected.upper()} ", border_style="green"))
    
    if _network_selected.upper() == "SONGBIRD":
        print(Panel.fit(f"[bold blue] {_network_selected.upper()} ", border_style="bold yellow"))

    NETWORK = cfg['network'][_network_selected]
    log.debug(f"Network: {NETWORK}")
    
    # Pull In Config
    FTSO_NODE_C_CHAIN_URL = f"{NETWORK['nodes']['node']['url']}{NETWORK['nodes']['node']['c_chain']}"
    log.debug(f"FTSO C Chain: {FTSO_NODE_C_CHAIN_URL}")

    FTSO_PRIVATE_KEY = os.getenv('FTSO_PRIVATE_KEY', NETWORK['ftso']['private_key'])
    log.debug(f"FTSO PRIVATE KEY LOADED")
    

    CONTRACT_FTSO_REWARD_MANAGER=NETWORK['contracts']['ftso_reward_manager']
    log.debug(f"FTSO Reward Manager Address: {CONTRACT_FTSO_REWARD_MANAGER['address']}")
    log.debug(f"FTSO Reward Manager ABI: {CONTRACT_FTSO_REWARD_MANAGER['abi']}")

    # Wrapped Songbird Contract
    CONTRACT_WNAT=NETWORK['contracts']['wnat']
    log.debug(f"WNAT Address: {CONTRACT_WNAT['address']}")
    log.debug(f"WNAT ABI: {CONTRACT_WNAT['abi']}")
    
    GAS_LIMIT = NETWORK['blockchain']['gas_limit']
    log.debug(f"GAS_LIMIT: {GAS_LIMIT}")
    GAS_PRICE = NETWORK['blockchain']['gas_price']
    log.debug(f"GAS_PRICE: {GAS_PRICE}")
    REWARD_TO_CLAIM_RECIPIENT = NETWORK['rewards']['claim']['_recipient']
    # log.debug(f"REWARD_TO_CLAIM: {REWARD_TO_CLAIM}")
    log.debug(f"REWARD_TO_CLAIM_RECIPIENT: {REWARD_TO_CLAIM_RECIPIENT}")
    

    if "FTSO_URL" in os.environ:
        web3 = Web3(HTTPProvider(os.getenv('FTSO_URL', FTSO_NODE_C_CHAIN_URL)))
        log.debug(f"FTSO_URL: {FTSO_NODE_C_CHAIN_URL}")
    else:
        web3 = Web3(HTTPProvider(FTSO_NODE_C_CHAIN_URL))
        log.debug(f"FTSO_URL: {FTSO_NODE_C_CHAIN_URL}")
        
    log.debug(f"FTSO_URL: {FTSO_NODE_C_CHAIN_URL}")

    # Avalanche Networks Require This
    web3.middleware_onion.inject(geth_poa_middleware, layer=0)

    if web3.isConnected():
        # Setup Account to be Used
        ftso_account = web3.eth.account.privateKeyToAccount(FTSO_PRIVATE_KEY)
        # Configure the default account to use
        web3.eth.default_account = ftso_account.address
    else:
        log.warning(f"Not Connected to {NETWORK['name'].upper()} NODE [ {FTSO_NODE_C_CHAIN_URL} ]")

    contract_ftso_reward_manager = web3.eth.contract(
        address=CONTRACT_FTSO_REWARD_MANAGER['address'], 
        abi=CONTRACT_FTSO_REWARD_MANAGER['abi']
    )

    contract_wnat = web3.eth.contract(
        address=CONTRACT_WNAT['address'], 
        abi=CONTRACT_WNAT['abi']
    )

    
    # Show Balance of FTSO
    _ftso_balance_wei, _ftso_balance = get_ftso_wallet_balance(web3, ftso_account)
    
    match str(NETWORK['name'].upper()):
        case 'FLARE':
            log.debug('FLARE Matched')
            # Get the Amount in the FTSO Reward Manager - Check there is enough to claim.
            _contract_ftso_reward_manager_balance_wei, _contract_ftso_reward_manager_balance = get_total_ftso_rewards_balance(web3, CONTRACT_FTSO_REWARD_MANAGER)
            if not is_contract_ftso_reward_manager_active(web3, contract_ftso_reward_manager):
                log.exception("FTSO Reward Manager is Not Active - Please Investigate !")
            # Whats the Current Reward EPOCH
            _current_reward_epoch = get_flare_current_reward_epoch(web3, contract_ftso_reward_manager)
            _claim_epoch_range = get_flare_claimable_reward_epoch_range(web3, contract_ftso_reward_manager)
            _ftso_rewards_epochs_claimable = get_flare_rewards_epoch_for_rewards_unclaimed(web3, ftso_account, contract_ftso_reward_manager)
            # xa = get_flare_rewards_claimable_from_ftso_rewards_manager(web3, ftso_account, contract_ftso_reward_manager, int(_ftso_rewards_epochs_claimable))
            _ftso_rewards_claimable = get_flare_rewards_claimable_from_ftso_rewards_manager(web3, ftso_account, contract_ftso_reward_manager, CONTRACT_FTSO_REWARD_MANAGER, _ftso_rewards_epochs_claimable)

            if args.claim:
                if len(_ftso_rewards_epochs_claimable):
                    if _contract_ftso_reward_manager_balance_wei < _ftso_rewards_claimable[0]['amount_wei']:
                        raise ValueError("Not Enough In FTSO Reward Manager")

                    wallet_recipient = NETWORK['rewards']['claim']['_recipient']
                    log.debug(f"Wallet Recipient: {wallet_recipient}")
                    
                    try:
                        tx = execute_reward_claim_flare(web3, ftso_account, FTSO_PRIVATE_KEY, contract_ftso_reward_manager, wallet_recipient, _ftso_rewards_epochs_claimable.pop(), GAS_LIMIT, GAS_PRICE)
                    except Exception as err:
                        exit(1)
                else:
                    log.info(f"No Rewards Claimable")

        case 'SONGBIRD':
            log.debug('SONGBIRD Matched')
            # Get the Amount in the FTSO Reward Manager - Check there is enough to claim.
            _contract_ftso_reward_manager_balance_wei, _contract_ftso_reward_manager_balance = get_total_ftso_rewards_balance(web3, CONTRACT_FTSO_REWARD_MANAGER)
            # Whats the Current Reward EPOCH
            _current_reward_epoch = get_songbird_current_reward_epoch(web3, contract_ftso_reward_manager)
            _claim_epoch_range = get_songbird_claimable_reward_epoch_range(web3, contract_ftso_reward_manager)
            _ftso_rewards_epochs_claimable = get_songbird_pricing_epoch_for_rewards_unclaimed(web3, ftso_account, contract_ftso_reward_manager)
            _ftso_rewards_claimable = get_songbird_rewards_claimable_from_ftso_rewards_manager(web3, ftso_account, contract_ftso_reward_manager, CONTRACT_FTSO_REWARD_MANAGER, _ftso_rewards_epochs_claimable)

            if args.claim:
                # get_songbird_wallet_balances_wsgb(web3, ftso_account, contract_wnat, CONTRACT_WNAT, _ftso_rewards_epochs_claimable)
                # get_songbird_wallet_balances_wsgb(web3, ftso_account, contract_wnat, CONTRACT_WNAT)
                if len(_ftso_rewards_epochs_claimable):
                    # Initiate Rewards
                    # web3.eth.get_balance(wallet_account['account_address'],)
                    # wnat_token = web3.eth.contract(address=contracts["WrappedFlare"]["address"], abi=contracts["WrappedFlare"]["abi"])
                
                    if _contract_ftso_reward_manager_balance_wei < _ftso_rewards_claimable[0]['amount_wei']:
                        ...
                        raise ValueError("Not Enough In FTSO Reward Manager")
                    
                    wallet_recipient = NETWORK['rewards']['claim']['_recipient']
                    log.debug(f"Wallet Recipient: {wallet_recipient}")
                    try:
                        tx = execute_reward_claim_songbird(web3, ftso_account, FTSO_PRIVATE_KEY, contract_ftso_reward_manager, wallet_recipient, _ftso_rewards_epochs_claimable.pop(), GAS_LIMIT, GAS_PRICE)
                    except Exception as err:
                        exit(1)
                
                else:
                    log.info(f"No Rewards Claimable")

        case _:
            log.exception('NETWORK NOT RECOGNISED')

    
    # _rewards_available_wei
    # pprint(_rewards_available_wei)
    
    
    # _contract_ftso_rewards_available_wei = web3.fromWei(_rewards_available_wei,'ether')
    # log.info(f"Rewards Claimable [{_rewards_available_wei}] WEI      : {_rewards_available_wei:.18f} FLR")

    # exit(0)
    # if args.claim:
    #     if args.rewards:
    #         _arg_rewards = float(args.rewards)
    #         _arg_rewards_wei = web3.toWei(_arg_rewards,'ether')
    #         # log.debug(f"Rewards Amount    : {args.rewards} FLR Requested ")
    #         # log.debug(f"Rewards to Claim  [{_arg_rewards_wei}] WEI : {_arg_rewards:.18f} FLR Requested ")
    #         # log.debug(f"Rewards Claimable [{_rewards_available_wei}] WEI : {_rewards_available:.18f} FLR Requested ")

    #         if (_rewards_available_wei - _arg_rewards_wei) > 0:
    #             log.info(f"Claiming Rewards   [{_arg_rewards_wei}] WEI      : {_arg_rewards:.18f} FLR")
    #             # Mock
    #             # _txn_id, _txn_receipt  = ("Wassup",AttributeDict({'status': 0}))
    #             # The Real Deal
    #             _txn_id, _txn_receipt  = claim_reward(web3, ftso_account, contract_ftso_reward_manager, _rewardAmount=_arg_rewards_wei)
    #             log.debug(f"TXN Receipt: {_txn_receipt.status}: {type(_txn_receipt.status)}")
    #             if not _txn_receipt.status == 1:
    #                 log.exception(f"Rewards Not Claimed -- Please Investigate -- TXN ID [{_txn_id}]")
    #         else:
    #             log.warning(f"Not Enough Rewards: {_rewards_available_wei}")


    #     _rewards_available = check_rewards_available(web3, ftso_account, contract_ftso_reward_manager)
    #     # log.info(f"Amount of Rewards Available: {_rewards_available} [{web3.fromWei(_rewards_available,'ether')}] FLR")
    print(Panel.fit("[bold blue]Finished", border_style="blue", box=box.DOUBLE))

if __name__ == "__main__":
    # log.setLevel("DEBUG")

    main()